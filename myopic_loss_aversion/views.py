# -*- coding: utf-8 -*-
from __future__ import division
from . import models
from ._builtin import Page, WaitPage
from otree.common import Currency as c, currency_range
from .models import Constants

def vars_for_all_templates(self):
    return {'Constants': Constants,
            'player': self.player}


class Introduction(Page):

    def is_displayed(self):
        return self.subsession.round_number == 1

    def vars_for_template(self):
        return {}


class Decide(Page):

    def is_displayed(self):
        return True

    form_model = models.Player
    form_fields = ['bet']

    def vars_for_template(self):
        label = "In round {}, I invest".format(self.subsession.round_number)
        return {"label": label}

    def before_next_page(self):
        self.player.set_payoff()


class Feedback(Page):

    def is_displayed(self):
        return self.player.feedback_time()

    def vars_for_template(self):
        if self.is_displayed():
            method_name = "_sg{}_vars_for_template".format(
                self.group.subgroup_type)
            method = getattr(self, method_name)
            return method()

    def _sg1_vars_for_template(self):
        return {}

    def _sg2_vars_for_template(self):

        def rreplace(s, old, new, occurrence):
            li = s.rsplit(old, occurrence)
            return new.join(li)

        limit = self.subsession.round_number
        offset = limit - 3  # last 3 rounds

        players = self.player.in_previous_rounds() + [self.player]
        combined_payoff = sum(p.payoff for p in players[offset:limit])

        rounds = map(str, range(offset+1, limit+1))
        rounds = rreplace(", ".join(rounds), ", ", " and ", 1)

        return {"combined_payoff": combined_payoff, "rounds": rounds}

    def _sg3_vars_for_template(self):
        limit = self.subsession.round_number
        offset = limit - 3  # last 3 rounds
        players = self.player.in_previous_rounds() + [self.player]
        return {"player_x_round": players[offset:limit]}

    def _sg4_vars_for_template(self):
        return self._sg2_vars_for_template()


class Resume(Page):

    def is_displayed(self):
        return self.subsession.round_number == Constants.num_rounds


page_sequence = [Introduction, Decide, Feedback, Resume]
