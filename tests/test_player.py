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
    assert issubclass(helper.Vulnerable, helper.Effect)
    entities.random.seed(123)
    all_cards = list(items.cards)
    SKIP_CARDS = ['Dual Wield']
    all_cards = [card for card in all_cards if card.name not in SKIP_CARDS]

    # Create uberplayer
    player = entities.Player(health=100, block=0, max_energy=100, deck=all_cards)
    for relic in items.relics:
      player.relics.append(relic)
    player.in_combat = True
    player.draw_pile = deepcopy(player.deck)

    # Create boss
    boss = enemy_catalog.SlimeBoss(health_range=[1000,1000])
    # helper.active_enemies.append(boss)

    # Patch some side effects
    with monkeypatch.context() as m:
        m.setattr('builtins.input', patched_input)
        m.setattr(helper, 'sleep', lambda x: None)
        m.setattr(entities, 'sleep', lambda x: None)
        helper.view.clear = replacement_clear_screen

        # Let 'er rip!
        initial_size = len(player.draw_pile)
        for idx, card in enumerate(player.draw_pile):
          stats(player, boss)
          print(f"Playing card {idx} of {initial_size} - {card.name}")
          player.use_card(card=card, enemies=[boss], target=boss, exhaust=True, pile=player.draw_pile)


class TestPendingAction():
    def test_pending_action_str_and_repl(self):
        pa = entities.PendingAction("draw_cards", lambda: None, 100)
        assert str(pa) == "PendingAction: draw_cards(100)"
        assert repr(pa) == "PendingAction: draw_cards(100)"

    def test_pending_action_can_set_argument(self):
        def action(arg1):
            print(f"Action executed with arg1={arg1}")
            return arg1

        pa = entities.PendingAction("PendingAction", action, 1)
        pa.set_amount(2)
        assert pa.amount == 2
        assert pa.execute() == 2

    def test_pending_action_can_modify_argument(self):
        def action(arg1):
            print(f"Action executed with arg1={arg1}")
            return arg1

        pa = entities.PendingAction("PendingAction", action, 1)
        pa.increase_amount(2)
        assert pa.amount == 3
        assert pa.execute() == 3

    def test_pending_action_can_be_cancelled(self):
        num_times_called = 0
        def action(arg1):
            nonlocal num_times_called
            print(f"Action executed with arg1={arg1}")
            num_times_called += 1
            return arg1

        pa = entities.PendingAction("PendingAction", action, 1)
        pa.cancel()
        assert pa.execute() is None
        assert pa.execute() is None
        assert num_times_called == 0

    def test_pending_action_can_only_be_executed_once(self):
        num_times_called = 0
        def action(arg1):
            nonlocal num_times_called
            print(f"Action executed with arg1={arg1}")
            num_times_called += 1
            return arg1

        pa = entities.PendingAction("PendingAction", action, 1)
        assert pa.execute() == 1
        assert pa.execute() is None
        assert num_times_called == 1
