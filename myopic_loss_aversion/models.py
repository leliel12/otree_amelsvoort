# -*- coding: utf-8 -*-
# <standard imports>
from __future__ import division
from otree.db import models
import otree.models
from otree import widgets
from otree.common import Currency as c, currency_range
import random
# </standard imports>

from django.conf import settings


doc = """
The goal of the experiment is to look how participants want to divide and
endowment between a risky asset and safe asset. The risky asset is just a
simple gamble were participants either win 7% or lose -3%. The chance that
they win is 40% and the chance that the loose is 60%. The safe asset does not
have a return so the part invested stays the same. Participants will invest
their endowment for nine rounds.
"""


source_code = "https://github.com/leliel12/otree_amelsvoort"


bibliography = ()

links = {
    "Wikipedia": {}
}

keywords = ("Myopic loss aversion", "Additive", "Multiplicative")


# =============================================================================
# CONSTANTS
# =============================================================================

class Constants:

    dev = settings.DEBUG

    name_in_url = 'myopic_loss_aversion'

    gadd, gmul = "additive", "multiplicative"
    gadd_endowment, gmul_endowment = c(10000), c(100000)

    sg1, sg2, sg3, sg4 = 1, 2, 3, 4
    groups = [
        (g, sg) for g in (gadd, gmul) for sg in (sg1, sg2, sg3, sg4)]

    players_per_group = None
    num_rounds = 9

    win_chance = 40
    loose_chance = 100 - win_chance
    win_perc = 7
    loose_perc = -3


# =============================================================================
# SUBSESSION
# =============================================================================

class Subsession(otree.models.BaseSubsession):

    def before_first_round(self):
        # extract and mix the players
        players = self.get_players()
        random.shuffle(players)

        # create the base for number of groups
        num_players = len(players)
        num_groups = len(Constants.groups)

        # create a list of how many players must be in every group
        # the result of this will be [2, 2, 2, 2, 2, 2, 2, 2]
        # obviously 2 * 8 = 16
        players_per_group = [int(num_players/num_groups)] * num_groups

        # add one player in order per group until the sum of size of
        # every group is equal to total of players
        idxg = 0
        while sum(players_per_group) < num_players:
            players_per_group[idxg] += 1
            idxg += 1
            if idxg >= len(players_per_group):
                idxg = 0

        # reassignment of groups
        list_of_lists = []
        for g_idx, g_size in enumerate(players_per_group):
            # it is the first group the offset is 0 otherwise we start
            # after all the players already exausted
            offset = 0 if g_idx == 0 else sum(players_per_group[:g_idx])

            # the asignation of this group end when we asign the total
            # size of the group
            limit = offset + g_size

            # we select the player to add
            group_players = players[offset:limit]
            list_of_lists.append(group_players)
        self.set_groups(list_of_lists)

    def before_session_starts(self):
        if self.round_number == 1:
            self.before_first_round()
        for idx, group in enumerate(self.get_groups()):
            group.group_type, group.subgroup_type = Constants.groups[0]

# =============================================================================
# GROUP
# =============================================================================

class Group(otree.models.BaseGroup):

    # <built-in>
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    group_type = models.CharField(
        max_length=20, choices=[Constants.gadd, Constants.gmul])

    subgroup_type = models.IntegerField(
        choices=[Constants.sg1, Constants.sg2, Constants.sg3, Constants.sg4])


# =============================================================================
# PLAYER
# =============================================================================

class Player(otree.models.BasePlayer):

    # <built-in>
    group = models.ForeignKey(Group, null=True)
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    fw = models.CurrencyField(min=0)
    bet = models.PositiveIntegerField(
        min=0, max=100, widget=widgets.SliderInput())
    rt = models.FloatField()
    is_winner = models.BooleanField()

    def feedback_time(self):
        round_number = self.subsession.round_number
        if self.group.subgroup_type == Constants.sg1:
            return True
        return round_number % 3 == 0

    def gadd_payoff(self, winner, pw):
        X = Constants.gadd_endowment
        alpha_t = self.bet / 100.
        rtp = (Constants.win_perc if winner else Constants.loose_perc) / 100.
        self.payoff = X * (alpha_t * (1 + rtp) + (1 - alpha_t))
        self.rt = float(X * (alpha_t * rtp))
        self.fw = pw + self.payoff

    def gmul_payoff(self, winner, pw):
        alpha_t = self.bet / 100.
        rtp = (Constants.win_perc if winner else Constants.loose_perc) / 100.
        self.rt = float(pw * alpha_t * rtp)
        self.fw = self.payoff = pw * (alpha_t * (1 + rtp) + (1 - alpha_t))

    def set_payoff(self):

        # retrieve the last whealt
        fw = self.last_fw()

        # check if is winner
        self.is_winner = (
            random.randint(0, 99) <= Constants.win_chance)

        # payoff ccompute
        if self.group.group_type == Constants.gadd:
            self.gadd_payoff(self.is_winner, fw)
        else:
            self.gmul_payoff(self.is_winner, fw)
            self.fw = fw * self.payoff

    def last_fw(self):
        previous = self.in_previous_rounds()
        first = not previous
        if first and self.group.group_type == Constants.gadd:
            return 0
        elif first and self.group.group_type == Constants.gmul:
            return Constants.gmul_endowment
        return previous[-1].fw

    def current_wealth(self):
        if self.group.subgroup_type == Constants.sg1:
            cw = self.last_fw()
        else:
            round_idx = self.subsession.round_number - 1
            if round_idx in (0, 3, 6):
                cw = self.last_fw()
            elif round_idx in (1, 2):
                players = self.in_previous_rounds()
                cw = players[0].last_fw()
            elif round_idx in (4, 5):
                players = self.in_previous_rounds()
                cw = players[3].last_fw()
            elif round_idx in (7, 8):
                players = self.in_previous_rounds()
                cw = players[6].last_fw()

        if cw == 0 and self.group.group_type == Constants.gadd:
            cw = Constants.gadd_endowment
        return cw

    def resume_rt(self):
        if self.group.subgroup_type == Constants.sg1:
            cw = [self.rt]
        else:
            players = self.in_previous_rounds() + [self]
            limit = self.subsession.round_number
            offset = limit - 1
            while offset > 0 and round_number % 3 != 0:
                offset -= 1
            return [p.rt for p in players[offset:limit]]

