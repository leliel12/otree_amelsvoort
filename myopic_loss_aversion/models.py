# -*- coding: utf-8 -*-
# <standard imports>
from __future__ import division
from otree.db import models
import otree.models
from otree import widgets
from otree.common import Currency as c, currency_range
import random
# </standard imports>



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



class Constants:
    name_in_url = 'myopic_loss_aversion'

    gadd, gmul = "additive", "multiplicative"
    gadd_endowment, gmul_endowment = c(10), c(100)

    sg1, sg2, sg3, sg4 = 1, 2, 3, 4
    groups = [
        (g, sg) for g in (gadd, gmul) for sg in (sg1, sg2, sg3, sg4)]

    players_per_group = None
    num_rounds = 9

    win_chance = 40
    loose_chance = 100 - win_chance
    win_perc = 7
    loose_perc = -3


class Subsession(otree.models.BaseSubsession):

    def before_session_starts(self):

        if self.round_number == 1:

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


class Group(otree.models.BaseGroup):

    # <built-in>
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    group_type = models.CharField(
        max_length=20, choices=[Constants.gadd, Constants.gmul])

    subgroup_type = models.IntegerField(
        choices=[Constants.sg1, Constants.sg2, Constants.sg3, Constants.sg4])


class Player(otree.models.BasePlayer):

    # <built-in>
    group = models.ForeignKey(Group, null=True)
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    payoff = models.CurrencyField(min=0)
    fw = models.CurrencyField(min=0)
    bet = models.PositiveIntegerField(
        min=0, max=100, widget=widgets.SliderInput())
    is_winner = models.BooleanField()

    def feedback_time(self):
        round_number = self.subsession.round_number
        if self.group.subgroup_type == Constants.sg1:
            return True
        return round_number % 3 == 0

    def gadd_payoff(self, winner):
        X = Constants.gadd_endowment
        alpha_t = self.bet / 100.
        rt = (Constants.win_perc if winner else Constants.loose_perc) / 100.
        return X * (alpha_t * (1 + rt) + (1 - alpha_t))

    def gmul_payoff(self, winner):
        alpha_t = self.bet / 100.
        rt = (Constants.win_perc if winner else Constants.loose_perc) / 100.
        return alpha_t * (1 + rt) + (1 - alpha_t)

    def set_payoff(self):

        # retrieve all palyers that not have payoff
        to_compute = [
            p for p in self.in_previous_rounds() if p.is_winner is None
        ] + [self]

        for idx, player in enumerate(to_compute):

            # check if is winner
            player.is_winner = (
                random.randint(0, 99) <= Constants.win_chance)

            # endowment changre
            if idx == 0 and self.group.group_type == Constants.gad:
                fw = 0
            elif idx == 0 and self.group.group_type == Constants.gmul:
                fw = Constants.gmul_endowment
            else:
                fw = to_compute[idx-1].fw

            # payoff ccompute
            if self.group.group_type == Constants.gad:
                self.payoff = self.gadd_payoff(player.is_winner)
                self.fw = fw + self.payoff
            else:
                self.payoff = self.gmul_payoff(player.is_winner)
                self.fw = fw * self.payoff
