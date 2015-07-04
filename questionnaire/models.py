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
Foo
"""


source_code = ""


bibliography = ()


links = {}


keywords = ()

class Constants:
    name_in_url = 'questionnaire'
    players_per_group = 2
    num_rounds = None


class Subsession(otree.models.BaseSubsession):
    pass


class Group(otree.models.BaseGroup):

    # <built-in>
    subsession = models.ForeignKey(Subsession)
    # </built-in>


class Player(otree.models.BasePlayer):

    # <built-in>
    group = models.ForeignKey(Group, null=True)
    subsession = models.ForeignKey(Subsession)
    # </built-in>

    gender = models.CharField(
        max_length=10, choices=['Male', 'Female'], widget=widgets.RadioSelect())
    age = models.IntegerField(min=10, max=100)
    mationality = models.CharField(
        max_length=10, widget=widgets.RadioSelect(),
        choices=["Dutch", "Germany", "Spanish", "Other"])
    education_level = models.CharField(
        verbose_name="Higest finished level of education",
        max_length=29, widget=widgets.RadioSelect(),
        choices=["High school", "First year college", "second year college",
                 "third year college", "Bachelor", "Master", "Doctorate"])
    study = models.CharField(
        max_length=29, widget=widgets.RadioSelect(),
        choices=["Chemistry and physics", "Business and Economics", "Law",
                 "Health and medicine", "language and communication",
                 "technique", "Art and cultures", "other"])
