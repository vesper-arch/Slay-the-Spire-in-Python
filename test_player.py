import entities
import enemy_catalog
import items
import pytest
from copy import deepcopy
import helper

def replacement_clear_screen():
    '''Replacement for game.view.clear() so that I can see the test output'''
    print("\n--------------------------\n")

def patched_input(*args, **kwargs):
    '''Patch for input() so that anytime we get asked a question, we just pick the first option'''
    return "1"

def test_all_attack_cards_with_all_relics(monkeypatch):
    '''A kind of crazy test that will load up a player with all cards and all
    relics and play them all against a boss. Sensitive to combat initialization details
    because that logic is not isolated from enemy creation.
    '''
    entities.random.seed(123)
    all_cards = [card for card in entities.cards.values()]

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
        # m.setattr(game, 'sleep', lambda x: None)
        # m.setattr(helper, 'sleep', lambda x: None)
        # m.setattr(entities, 'sleep', lambda x: None)
        helper.view.clear = replacement_clear_screen

        # Let 'er rip!
        for idx, card in enumerate(player.draw_pile):
          player.use_card(card=card, target=boss, exhaust=True, pile=player.draw_pile)

