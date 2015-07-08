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



page_sequence = [Introduction, Decide]
