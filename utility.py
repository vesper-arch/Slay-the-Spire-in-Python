from time import sleep
from os import system
import math
import random
from ansimarkup import parse, ansiprint


active_enemies = []
combat_turn = 0
cards = {
    "Strike": {"Name": "Strike", "Damage": 6, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 6 damage"},
    "Strike+": {"Name": "<green>Strike+</green>", "Upgraded": True, "Damage": 9, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 9 damage"},

    "Defend": {"Name": "Defend", "Block": 5, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain 5 <yellow>Block</yellow>"},
    "Defend+": {"Name": "<green>Defend+</green>", "Upgraded": True, "Block": 8, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain 8 <yellow>Block</yellow>"},

    "Bash": {"Name": "Bash", "Damage": 8, "Vulnerable": 2, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 8 damage. Apply 2 <yellow>Vulnerable</yellow>"},
    "Bash+": {"Name": "<green>Bash+</green>", "Upgraded": True, "Damage": 10, "Vulnerable": 3, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 10 damage. Apply 3 <yellow>Vulnerable</yellow>"},

    "Body Slam": {"Name": "Body Slam", "Damage": 0, "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Deal damage equal to your <yellow>Block</yellow>"},
    "Body Slam+": {"Name": "<green>Body Slam+", "Upgraded": True, "Damage": 0, "Energy": 0, "Rarity": "Common", "Type": "Attack", "Info": "Deal damage equal to your <yellow>Block</yellow>"},

    "Clash": {"Name": "Clash", "Damage": 14, "Energy": 0, "Rarity": "Common", "Type": "Attack", "Info": "Can only be played is every card in your hand is an Attack. Deal 14 damage."},
    "Clash+": {"Name": "<green>Clash+</green>", "Upgraded": True, "Damage": 18, "Energy": 0, "Rarity": "Common", "Type": "Attack", "Info": "Can only be player if every card in your hand is an Attack. Deal 18 damage."},

    "Cleave": {"Name": "Cleave", "Damage": 8, "Target": "All", "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Deal 8 damage to ALL enemies"},
    "Cleave+": {"Name": "<green>Cleave+</green>", "Damage": 11, "Target": "All", "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Deal 11 Damage to ALL enemies"},

    "Clothesline": {"Name": "Clothesline", "Damage": 12, "Weak": 2, "Rarity": "Common", "Type": "Attack", "Info": "Deal 12 damage. Apply 2 <yellow>Weak</yellow>"},
    "Clothesline+": {"Name": "<green>Clothesline</green>", "Damage": 14, "Weak": 3, "Upgraded": True, "Rarity": "Common", "Type": "Attack", "Info": "Deal 14 damage. Apply 3 <yellow>Weak</yellow>"}
}


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
    target.health = max(target.health, 0)


def display_ui(entity, combat=True):
    # Displays all the card in the player's hand(Look at the function above for code)
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
