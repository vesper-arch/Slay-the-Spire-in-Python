from time import sleep
from os import system
import math
import random
from ansimarkup import parse, ansiprint


active_enemies = []
combat_turn = 0
combat_potion_dropchance = 40



def damage(damage: int, target: object, user, card=True):
    if user.weak > 0 and card:
        damage = math.floor(damage * 0.75)
    if target.vulnerable > 0:
        damage = math.floor(damage * 1.50)
    if damage < target.block:
        target.block -= damage
    elif damage > target.block:
        target.health -= damage - target.block
        target.block = 0
    elif damage == target.block:
        target.block -= damage
    print(f"{user.name} dealt {damage:.0f} damage to {target.name}")
    target.health = max(target.health, 0)
    if target.health == 0:
        target.die()
    sleep(1)



def display_ui(entity, combat=True):
    """
    If the player is in combat, don't show the type of card and display if the player doesn't have enough energy for it
    otherwise, Show the type with the card
    Shows the enemies's status
    Shows the player's status"""
    counter = 1
    # Repeats for every card in the player's hand
    for card in entity.hand:
        if combat is True:
            # Prints in red if the player doesn't have enough energy to use the card
            if card["Energy"] > entity.energy:
                ansiprint(f"{counter}: <red>{card['Name']}</red> | <light-red>{card['Info']}</light-red> | <red>{card['Energy']}</red>")
            # Otherwise, print in full color
            else:
                ansiprint(f"{counter}: <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            # Adds one to the counter to make a numbered list(Ex. 1: Defend// 2: Strike...)
            counter += 1
        # Displays the type of card if the player is not in combat
        else:
            ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red>| <yellow>{card['Info']}</yellow>")
            counter += 1
    print()
    if combat is True:
        for enemy in active_enemies:
            enemy.show_status()
        # Displays the number of cards in the draw and discard pile
        print(f"Draw pile: {len(entity.draw_pile)}\nDiscard pile: {len(entity.discard_pile)}\n")
        # Displays the player's current health, block, and energy
    entity.show_status()
    print()
    counter = 1


def start_combat(entity, enemy_list):
    print("Starting combat")
    entity.draw_pile = random.sample(entity.deck, len(entity.deck))
    encounter_enemies = random.choice(enemy_list)
    for enemy in encounter_enemies:
        active_enemies.append(enemy)
        enemy.health = random.randint(enemy.health[0], enemy.health[1])
        enemy.max_health = enemy.health
