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

def patched_input(*args, **kwargs):
    '''Patch for input() so that anytime we get asked a question, we just pick the first option'''
    return "1"

def stats(player, enemy):
    ansiprint(f"<yellow>Player has {player.health} health, {player.block} block, {player.energy} energy, {len(player.hand)} cards in hand, {len(player.draw_pile)} cards in draw pile, {len(player.discard_pile)} cards in discard pile, {len(player.exhaust_pile)} cards in exhaust pile</yellow>")
    ansiprint(f"<red>Enemy has {enemy.health} health, {enemy.block} block</red>")

@pytest.mark.only
def test_combat_basic(monkeypatch):
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

    # Patch some side effects
    with monkeypatch.context() as m:
        m.setattr('builtins.input', patched_input)
        m.setattr(helper, 'sleep', lambda _: None)
        m.setattr(entities, 'sleep', lambda _: None)
        m.setattr(items, 'sleep', lambda _: None)
        helper.view.clear = replacement_clear_screen

        # Run combat
        combat.combat(game_map)