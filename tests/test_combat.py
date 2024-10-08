from copy import deepcopy
from unittest.mock import Mock

import pytest

import displayer
import effect_catalog
import enemy_catalog
import entities
import game
import combat
import player
from ansi_tags import ansiprint
from definitions import CombatTier
from tests.fixtures import sleepless


def replacement_clear_screen():
    '''Replacement for game.view.clear() so that I can see the test output'''
    print("\n--------------------------\n")


def test_new_combat_basic(monkeypatch, sleepless):
    game.random.seed(123)

    # Create player
    test_player = player.Player.create_player()

    # Create bad guys
    acidslime = enemy_catalog.AcidSlimeS()
    jawworm = enemy_catalog.JawWorm()

    # Create combat object
    game_map = Mock()
    combat_obj = combat.Combat(player=test_player, tier=CombatTier.NORMAL, all_enemies=[acidslime, jawworm], game_map=game_map)


    # Patch the input
    responses = iter("11112e111e21e233e12e12") # Fight sequence for Acid Slime (S) and Jaw Worm
    with monkeypatch.context() as m:
        m.setattr('builtins.input', lambda *a, **kw: next(responses))
        displayer.clear = replacement_clear_screen

        # Run combat
        combat_obj.combat()