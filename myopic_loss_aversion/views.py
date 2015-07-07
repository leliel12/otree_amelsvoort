# -*- coding: utf-8 -*-
from __future__ import division
from . import models
from ._builtin import Page, WaitPage
from otree.common import Currency as c, currency_range
from .models import Constants

def vars_for_all_templates(self):

    return {'total_q': 1,
            'constants': Constants,
            'round_number': self.subsession.round_number,
            'player': self.player}


class Introduction(Page):

    def is_displayed(self):
        return self.subsession.round_number == 1

    def vars_for_template(self):
        group_type = self.player.group.group_type()
        return {
            "group_type": group_type[0],
        }


page_sequence = [Introduction]
