import entities
import enemy_catalog
import items
import pytest
from copy import deepcopy
import helper
from ansi_tags import ansiprint

def replacement_clear_screen():
    '''Replacement for game.view.clear() so that I can see the test output'''
    print("\n--------------------------\n")

def patched_input(*args, **kwargs):
    '''Patch for input() so that anytime we get asked a question, we just pick the first option'''
    return "1"

def stats(player, enemy):
    ansiprint(f"<yellow>Player has {player.health} health, {player.block} block, {player.energy} energy, {len(player.hand)} cards in hand, {len(player.draw_pile)} cards in draw pile, {len(player.discard_pile)} cards in discard pile, {len(player.exhaust_pile)} cards in exhaust pile</yellow>")
    ansiprint(f"<red>Enemy has {enemy.health} health, {enemy.block} block</red>")

def test_all_attack_cards_with_all_relics(monkeypatch):
    '''A kind of crazy test that will load up a player with all cards and all
    relics and play them all against a boss. Sensitive to combat initialization details
    because that logic is not isolated from enemy creation.
    '''
    entities.random.seed(123)
    all_cards = list(items.cards)

    # Create uberplayer
    player = entities.Player(health=100, block=0, max_energy=3, deck=all_cards)
    for relic in items.relics.values():
      player.relics.append(relic)
    player.in_combat = True
    player.draw_pile = deepcopy(player.deck)

    # Create boss
    boss = enemy_catalog.SlimeBoss()
    helper.active_enemies.append(boss)

    # Patch some side effects
    with monkeypatch.context() as m:
        m.setattr('builtins.input', patched_input)
        m.setattr(helper, 'sleep', lambda x: None)
        m.setattr(entities, 'sleep', lambda x: None)
        m.setattr(items, 'sleep', lambda x: None)
        helper.view.clear = replacement_clear_screen

        # Let 'er rip!
        for idx, card in enumerate(player.draw_pile):
          stats(player, boss)
          print(f"Playing card {idx} of {len(player.draw_pile)} - {card['Name']}")
          player.use_card(card=card, target=boss, exhaust=True, pile=player.draw_pile)

