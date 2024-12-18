from __future__ import annotations

import random
from os import name, system
from time import sleep
from typing import TYPE_CHECKING, Callable

from ansi_tags import ansiprint, strip
from definitions import (
    State,
)

if TYPE_CHECKING:
    from card_catalog import Card

# Displayer module
# Displays important info to the player during combat


def view_piles(pile: list[Card], shuffle=False, end=False, validator: Callable = lambda placehold: bool(placehold)):
    """Prints a numbered list of all the cards in a certain pile."""
    if len(pile) == 0:
        ansiprint("<red>This pile is empty</red>.")
        sleep(1.5)
        clear()
        return
    if shuffle is True:
        pile = random.sample(pile, len(pile))
        ansiprint("<italic>Cards are not shown in order.</italic>")
    counter = 1
    for card in pile:
        if validator(card):
            ansiprint(f"{counter}: {card.pretty_print()}")
            counter += 1
            sleep(0.05)
        else:
            ansiprint(f"{counter}: <light-black>{strip(card.pretty_print())}</light-black>")
            counter += 1
            sleep(0.05)
    if end:
        input("Press enter to continue > ")
        sleep(0.5)
        clear()

def view_relics(relic_pool, end=False, validator: Callable = lambda placehold: bool(placehold)):
    for relic in relic_pool:
        if validator(relic):
            ansiprint(relic.pretty_print())
            sleep(0.05)
    if end:
        input("Press enter to continue > ")
        sleep(1.5)
        clear()

def view_potions(potion_pool, only_the_potions = False, max_potions=3, numbered_list=True, validator: Callable = lambda placehold: bool(placehold)):
    counter = 1
    for potion in potion_pool:
        if validator(potion):
            ansiprint(f'{counter}: ' + potion.pretty_print())
            counter += 1
    if only_the_potions is False:
        for _ in range(max_potions - len(potion_pool)):
            ansiprint(f"<light-black>{f'{counter}: ' if numbered_list else ''}(Empty)</light-black>")
            counter += 1

def view_map(game_map):
    game_map.pretty_print()
    print("\n")
    sleep(0.2)
    input("Press enter to leave > ")

def display_ui(entity, enemies, combat=True):
    assert all(x is not None for x in entity.hand)
    # Repeats for every card in the entity's hand
    ansiprint("<bold>Relics: </bold>")
    view_relics(entity.relics)
    ansiprint("<bold>Hand: </bold>")
    view_piles(entity.hand, entity, False, lambda card: (card.energy_cost if card.energy_cost != -1 else entity.energy) <= entity.energy)
    if combat is True:
        counter = 1
        ansiprint("\n<bold>Enemies:</bold>")
        viewable_enemies = [enemy for enemy in enemies if enemy.state in (State.ALIVE, State.INTANGIBLE)]
        for enemy in viewable_enemies:
            ansiprint(f"{counter}: " + repr(enemy))
            counter += 1
        ansiprint("\n" + repr(entity))
    else:
        ansiprint(str(entity))
    print()

def list_input(input_string: str, choices: list, displayer: Callable,
               validator: Callable = lambda placehold: bool(placehold),
               message_when_invalid: str | None = None,
               extra_allowables=None) -> int | str | None:
    """Allows the player to choose from a certain list of options. Includes validation."""
    if extra_allowables is None:
        extra_allowables = []
    valid_choices = [choice for choice in choices if validator(choice)] + extra_allowables
    if len(valid_choices) == 0:
        ansiprint("<red>There are no valid choices.</red>")
        return None
    # Automatically choose the only option if there is only one
    if len(choices) + len(extra_allowables) == 1:
        if len(choices) == 1:
            return 0
        return extra_allowables[0]
    while True:
        try:
            displayer(choices, validator=validator)
            ansiprint(input_string + " > ", end="")
            response = input()
            if response in extra_allowables:
                return response
            option = int(response) - 1
            if not validator(choices[option]):
                ansiprint(f"\u001b[1A\u001b[1000D<red>{message_when_invalid}</red>", end="")
                sleep(1.5)
                print("\u001b[2K")
                continue
        except (IndexError, ValueError):
            ansiprint(f"\u001b[1A\u001b[100D<red>You have to enter a whole number between 1 and {len(choices)}.</red>", end="")
            sleep(1)
            print("\u001b[2K\u001b[100D", end="")
            continue
        break
    return option

def multi_input(input_string: str, choices: list, displayer: Callable, max_choices: int,
                strict: bool = False, validator: Callable = lambda placehold: bool(placehold),
                message_when_invalid: str | None = None,
                extra_allowables: list | None = None):
    """Basically the same as view.list_input but you can choose multiple cards one at a time. Mainly used for discarding and Exhausting cards."""
    if not extra_allowables:
        extra_allowables = []
    finished = False
    to_be_moved = []
    while not finished:
        while True:
            try:
                displayer(choices, validator=validator)
                ansiprint(input_string + "(type 'exit' to finish) > ", end="")
                response = input()
                if response == 'exit' and (strict and len(to_be_moved) < max_choices):
                    ansiprint(f"\u001b[1A\u001b[1000D<red>You have to choose exactly {max_choices} items.</red>", end="")
                    sleep(1)
                    print("\u001b[2K\u001b[100D", end="")
                    continue
                elif response == 'exit':
                    finished = True
                    break
                if response in extra_allowables:
                    return response
                option = int(response) - 1
                if not validator(choices[option]):
                    ansiprint(f"\u001b[1A\u001b[1000D<red>{message_when_invalid}</red>", end="")
                    sleep(1.5)
                    print("\u001b[2K\u001b[100D")
                    continue
                if len(to_be_moved) == max_choices:
                    del to_be_moved[0]
            except (IndexError, ValueError):
                ansiprint(f"\u001b[1A\u001b[100D<red>You have to enter a whole number between 1 and {len(choices)}.</red>", end="")
                sleep(1)
                print("\u001b[2K\u001b[100D", end="")
                continue
            to_be_moved.append(choices[option])
            break

def clear():
    system("cls" if name == "nt" else "clear")
