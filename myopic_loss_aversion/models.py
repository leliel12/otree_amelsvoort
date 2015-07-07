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
    sg1, sg2, sg3, sg4 = 1, 2, 3, 4

    groups = [
        (g, sg) for g in (gadd, gmul) for sg in (sg1, sg2, sg3, sg4)]

    players_per_group = None
    num_rounds = 1


class Subsession(otree.models.BaseSubsession):

       def before_session_starts(self):
        if self.round_number == 1:

            # create the base for number of groups
            num_players = len(self.get_players())
            num_groups = len(Constants.groups)
            players_per_group = [int(num_players/num_groups)] * num_groups

            # verify if all players are assigned
            idxg = 0
            while sum(players_per_group) < num_players:
                players_per_group[idxg] += 1
                idxg += 1

            # reassignment of groups
            list_of_lists = []
            start_index = 0
            players = self.get_players()
            for g_idx, g_size in enumerate(players_per_group):
                offset = 0 if g_idx == 0 else sum(players_per_group[:g_idx])
                limit = offset + g_size
                group_players = players[offset:limit]
                list_of_lists.append(group_players)
            self.set_groups(list_of_lists)


class Group(otree.models.BaseGroup):

    # <built-in>
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    def group_type(self):
        return Constants.groups[self.id_in_subsession]

    def set_payoffs(self):
        import ipdb; ipdb.set_trace()


class Player(otree.models.BasePlayer):

    # <built-in>
    group = models.ForeignKey(Group, null=True)
    subsession = models.ForeignKey(Subsession)
    # </built-in>


