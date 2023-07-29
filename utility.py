from time import sleep
from os import system
import math
import random
from ansimarkup import parse, ansiprint


active_enemies = []
combat_turn = 1
combat_potion_dropchance = 40



def damage(dmg: int, target: object, user, card=True):
    dmg = dmg + user.strength + user.vigor
    if user.weak > 0 and card:
        dmg = math.floor(dmg * 0.75)
    if target.vulnerable > 0:
        dmg = math.floor(dmg * 1.50)
    # Manages Block
    if dmg < target.block:
        target.block -= dmg
    elif dmg > target.block:
        target.health -= dmg - target.block
        target.block = 0
    elif dmg == target.block:
        target.block -= dmg
    
    print(f"{user.name} dealt {dmg:.0f} damage to {target.name}")
    # Removes debuffs that trigger on attack.
    if user.vigor > 0:
        user.vigor = 0
        ansiprint("<light-cyan>Vigor</light-cyan> wears off")
    target.health = max(target.health, 0)
    if target.health <= 0:
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
    if combat is True:
        for card in entity.hand:
            # Prints in red if the player doesn't have enough energy to use the card
            if card["Energy"] > entity.energy:
                ansiprint(f"{counter}: <red>{card['Name']}</red> | <light-red>{card['Info']}</light-red> | <red>{card['Energy']}</red>")
            # Otherwise, print in full color
            else:
                ansiprint(f"{counter}: <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            # Adds one to the counter to make a numbered list(Ex. 1: Defend// 2: Strike...)
            counter += 1
    else:
        for card in entity.deck:
            ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            counter += 1
            sleep(0.05)
    print()
    if combat is True:
        for enemy in active_enemies:
            enemy.show_status()
        # Displays the number of cards in the draw and discard pile
        print(f"Draw pile: {len(entity.draw_pile)}\nDiscard pile: {len(entity.discard_pile)}\n")
        # Displays the player's current health, block, and energy
        entity.show_status()
    else:
        entity.show_status(False)
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
    
def integer_input(input_string, array):
    while True:
        try:
            option = int(input(input_string)) - 1
            array[option] = array[option] # Does nothing, checks that the number is in range
        except ValueError:
            print("You have to enter a number")
            sleep(1.5)
            system("clear")
            continue
        except IndexError:
            print("Option not in range")
            sleep(1.5)
            system("clear")
            continue
        return option
        break
