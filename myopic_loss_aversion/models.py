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
    num_rounds = 1

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

        for idx, group in enumerate(self.get_groups()):
            group.group_type, group.subgroup_type = Constants.groups[idx]
            if group.group_type == Constants.gadd or self.round_number == 1:
                endowment = (
                    Constants.gadd_endowment
                    if group.group_type == Constants.gadd else
                    Constants.gmul_endowment)
                for player in group.get_players():
                    player.fw += endowment
                    player.save()


class Group(otree.models.BaseGroup):

    # <built-in>
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    group_type = models.CharField(
        max_length=20, choices=[Constants.gadd, Constants.gmul])

    subgroup_type = models.IntegerField(
        choices=[Constants.sg1, Constants.sg2, Constants.sg3, Constants.sg4])

    def random_win(self):
        return random.randint(0, 99) <= Constants.win_chance

    def set_payoffs(self):
        import ipdb; ipdb.set_trace()


class Player(otree.models.BasePlayer):

    # <built-in>
    group = models.ForeignKey(Group, null=True)
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    fw = models.CurrencyField(min=0, default=c(0))
    bet = models.PositiveIntegerField(
        min=0, max=100, widget=widgets.SliderInput())




