from copy import deepcopy

import pytest

import card_catalog
import displayer
import effect_catalog
import enemy_catalog
import game
import items
import player
import relic_catalog
from ansi_tags import ansiprint
from tests.fixtures import sleepless


def replacement_clear_screen():
    '''Replacement for game.view.clear() so that I can see the test output'''
    print("\n--------------------------\n")

def patched_input(*args, **kwargs):
    '''Patch for input() so that anytime we get asked a question, we just pick the first option'''
    return "1"

def stats(player, enemy):
    ansiprint(f"<yellow>Player has {player.health} health, {player.block} block, {player.energy} energy, {len(player.hand)} cards in hand, {len(player.draw_pile)} cards in draw pile, {len(player.discard_pile)} cards in discard pile, {len(player.exhaust_pile)} cards in exhaust pile</yellow>")
    ansiprint(f"<red>Enemy has {enemy.health} health, {enemy.block} block</red>")


def test_relics_searchable_by_string_and_class(sleepless):
    # Create player with relics
    test_player = player.Player(health=100, block=0, max_energy=100, deck=[])
    for relic in relic_catalog.create_all_relics():
      test_player.relics.append(relic)
    assert "Burning Blood" in test_player.relics, "Should be able to find a relic by its string"
    assert relic_catalog.BurningBlood in test_player.relics, "Should be able to find a relic by its class"


def test_all_attack_cards_with_all_relics(monkeypatch, sleepless):
    '''A kind of crazy test that will load up a player with all cards and all
    relics and play them all against a boss. Sensitive to combat initialization details
    because that logic is not isolated from enemy creation.
    '''
    assert issubclass(effect_catalog.Vulnerable, effect_catalog.Effect)
    game.random.seed(123)
    all_cards = card_catalog.create_all_cards()
    SKIP_CARDS = ['Dual Wield']
    all_cards = [card for card in all_cards if card.name not in SKIP_CARDS]

    # Create uberplayer
    test_player = player.Player(health=1000, block=0, max_energy=100, deck=all_cards)
    for relic in relic_catalog.create_all_relics():
      test_player.relics.append(relic)
    test_player.in_combat = True
    test_player.draw_pile = deepcopy(test_player.deck)

    # Create boss
    boss = enemy_catalog.SlimeBoss(health_range=[1000,1000])
    # effects.active_enemies.append(boss)

    # Patch some side effects
    with monkeypatch.context() as m:
        m.setattr('builtins.input', patched_input)
        displayer.clear = replacement_clear_screen

        # Let 'er rip!
        initial_size = len(test_player.draw_pile)
        for idx, card in enumerate(test_player.draw_pile):
          stats(test_player, boss)
          print(f"Playing card {idx} of {initial_size} - {card.name}")
          test_player.use_card(card=card, enemies=[boss], target=boss, exhaust=True, pile=test_player.draw_pile)

