from copy import deepcopy
from unittest.mock import Mock

import pytest

import displayer
import effects
import enemy_catalog
import entities
import game
import player
from ansi_tags import ansiprint
from definitions import CombatTier


def replacement_clear_screen():
    '''Replacement for game.view.clear() so that I can see the test output'''
    print("\n--------------------------\n")


def test_new_combat_basic(monkeypatch):
    entities.random.seed(123)

    # Create player
    test_player = player.Player.create_player()

    # Create bad guys
    acidslime = enemy_catalog.AcidSlimeS()
    jawworm = enemy_catalog.JawWorm()

    # Create combat object
    game_map = Mock()
    combat = game.Combat(player=test_player, tier=CombatTier.NORMAL, all_enemies=[acidslime, jawworm], game_map=game_map)


    # Patch the input
    responses = iter("11112e111e21e233e12e12") # Fight sequence for Acid Slime (S) and Jaw Worm
    with monkeypatch.context() as m:
        m.setattr('builtins.input', lambda *a, **kw: next(responses))
        m.setattr(effects, 'sleep', lambda _: None)
        m.setattr(entities, 'sleep', lambda _: None)
        m.setattr(game, 'sleep', lambda _: None)
        displayer.clear = replacement_clear_screen

        # Run combat
        combat.combat(game_map)