from __future__ import annotations

import random

import pytest

import entities
import game
import effects
import displayer
import shop
from ansi_tags import ansiprint
from definitions import CardType
import time


def replacement_clear_screen():
    '''Replacement for game.view.clear() so that I can see the test output'''
    print("\n--------------------------\n")


def repeat_check(repeat_catcher, last_return, current_return) -> tuple[int, bool]:
    '''Check if the player is stuck in a loop
    '''
    if last_return == current_return:
        repeat_catcher += 1
    else:
        repeat_catcher = 0
    if repeat_catcher > 3:
        print("Player is stuck in a loop")
        return repeat_catcher, True
    return repeat_catcher, False

@pytest.mark.timeout(20)
@pytest.mark.parametrize("seed", list(range(2)))
def test_e2e(seed, monkeypatch):
    '''Test the game from start to finish
    Plays with (more or less) random inputs to test the game.
    Seems to find lots of bugs, but very hard to repeat.
    '''
    ansiprint(f"<red><bold>Seed for this run is: {seed}</bold></red>")
    mygame = game.Game(seed=seed)
    repeat_catcher = 0
    last_return = None
    def patched_input(*args, **kwargs):
        '''Patch for input that can play the game!
        '''
        nonlocal mygame
        nonlocal repeat_catcher
        nonlocal last_return
        random_return = random.choice(
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'e',
             'p', 'm', 'd', 'a', 's', 'x', 'f', 'y', 'n',
             'rest', 'smith', 'view deck', 'leave', 'exit', 'lift', 'toke', 'dig'])
        player = mygame.player
        if player.state == entities.State.DEAD:
            return '\n'
        if args and "Choose" in args[0]:
            choice = random.randint(1, 10)
            print(f"Player chose {choice}")
            return str(choice)
        possible_cards = [card for card in player.hand if card.energy_cost <= player.energy and card.type != CardType.STATUS]
        if len(possible_cards) > 0:
            ret = str(random.randint(1, len(possible_cards)))
            repeat_catcher, check = repeat_check(repeat_catcher, last_return, ret)
            if not check:
                last_return = ret
                print(f"Player chose {ret}")
                return ret
            else:
                print(f"Player chose {random_return}")
                last_return = random_return
                return random_return

        if player.energy == 0 and player.in_combat:
            print("Player has no energy left.")
            # from pprint import pprint
            # pprint(player.__dict__)
            repeat_catcher, check = repeat_check(repeat_catcher, last_return, 'e')
            if not check:
                last_return = 'e'
                print("Player chose 'e'")
                return 'e'
            else:
                last_return = random_return
                print(f"Player chose {random_return}")
                return random_return

        # Default to picking randomly
        print(f"Player chose {random_return}")
        return random_return

    with monkeypatch.context() as m:
        m.setattr('builtins.input', patched_input)
        m.setattr(effects, 'sleep', lambda x: None)
        m.setattr(entities, 'sleep', lambda x: None)
        m.setattr(game, 'sleep', lambda x: None)
        displayer.clear = replacement_clear_screen
        try:
            start = time.time()
            mygame.start()
        except Exception as e:
            ansiprint(f"<red><bold>Failed with seed: {seed}</bold></red>")
            raise e
        finally:
            end = time.time()
            ansiprint(f"\n\n<green><bold>Game took {end - start:.2f} seconds</bold></green>")

