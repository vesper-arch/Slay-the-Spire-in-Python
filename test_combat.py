from copy import deepcopy
from unittest.mock import Mock

import pytest

import enemy_catalog
import entities
import game
import helper
import items
from ansi_tags import ansiprint
from definitions import CombatTier


def replacement_clear_screen():
    '''Replacement for game.view.clear() so that I can see the test output'''
    print("\n--------------------------\n")


def test_new_combat_basic(monkeypatch):
    entities.random.seed(123)

    # Create player
    player = entities.create_player()

    # Create bad guys
    acidslime = enemy_catalog.AcidSlimeS()
    jawworm = enemy_catalog.JawWorm()

    # Create combat object
    game_map = Mock()
    combat = game.Combat(player=player, tier=CombatTier.NORMAL, all_enemies=[acidslime, jawworm], game_map=game_map)


    # Patch the input
    responses = iter("11112e111e21e233e122e31") # Fight sequence for Acid Slime (S) and Jaw Worm
    with monkeypatch.context() as m:
        m.setattr('builtins.input', lambda *a, **kw: next(responses))
        m.setattr(helper, 'sleep', lambda _: None)
        m.setattr(entities, 'sleep', lambda _: None)
        m.setattr(items, 'sleep', lambda _: None)
        helper.view.clear = replacement_clear_screen

        # Run combat
        combat.combat(game_map)