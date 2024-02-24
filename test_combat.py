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

@pytest.mark.only
def test_new_combat_basic(monkeypatch):
    entities.random.seed(123)
    all_cards = [c() for c in items.cards]

    # Create player
    player = entities.Player(health=100, block=0, max_energy=3, deck=all_cards)

    # Create bad guys
    acidslime = enemy_catalog.AcidSlimeS()
    jawworm = enemy_catalog.JawWorm()

    # Create combat object
    combat = game.Combat(player, CombatTier.NORMAL, [acidslime, jawworm])

    game_map = Mock()

    # Patch the input
    responses = iter("11\n11\n2\n")
    with monkeypatch.context() as m:
        m.setattr('builtins.input', lambda *a, **kw: next(responses))
        m.setattr(helper, 'sleep', lambda _: None)
        m.setattr(entities, 'sleep', lambda _: None)
        m.setattr(items, 'sleep', lambda _: None)
        helper.view.clear = replacement_clear_screen

        # Run combat
        combat.combat(game_map)