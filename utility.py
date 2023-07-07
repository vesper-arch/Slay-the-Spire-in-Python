from time import sleep
from os import system
import math
import random
from ansimarkup import parse, ansiprint


active_enemies = []
combat_turn = 0
cards = {
  "Strike": {"Name": "Strike", "Damage": 6, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 6 damage"},
  "Strike+": {"Name": "<green>Strike+</green>", "Upgraded": True, "Damage": 9, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal <green>9</green> damage"},

  "Defend": {"Name": "Defend", "Block": 5, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain 5 <yellow>Block</yellow>"},
  "Defend+": {"Name": "<green>Defend+</green>", "Upgraded": True, "Block": 8, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain <green>8</green> <yellow>Block</yellow"},

  "Bash": {"Name": "Bash", "Damage": 8, "Vulnerable": 2, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 8 damage. Apply 2 <yellow>Vulnerable</yellow>"},
  "Bash+": {"Name": "<green>Bash+</green>", "Upgraded": True, "Damage": 10, "Vulnerable": 3, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal <green>10</green> damage. Apply <green>3</green> <yellow>Vulnerable</yellow>"}
}
def damage(damage:int, target:object):
  if target.vulnerable > 0:
    damage = math.floor(damage * 1.50)
  if damage < target.block:
    target.block -= damage
  elif damage > target.block:
    target.health -= damage - target.block
    target.block = 0
  elif damage == target.block:
    target.block -= damage
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
  entity.draw_pile = random.sample(entity.deck, len(entity.deck))
  encounter_enemies = random.choice(enemy_list)
  for enemy in encounter_enemies:
    active_enemies.append(enemy)