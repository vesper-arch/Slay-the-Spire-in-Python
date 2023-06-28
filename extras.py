import math
from time import sleep
from os import system
import random
from ansimarkup import parse, ansiprint
from entities import Player

turn = 0
# Defines a class called Card. This class will give the given variable the energy_cost, damage, and name attributes
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
class Enemy:
  def __init__(self, health, max_health, block, name, debuff_buffs={}):
    '''
    Attributes::
    health: Current health
    max_health: Maximum health
    block: Current block
    name: Enemy name
    debuff_buffs: Current debuff_buffs w/ debuff length
    '''
    self.health = health
    self.max_health = max_health
    self.block = block
    self.name = name
    self.debuff_buffs = debuff_buffs
    self.barricade = False
    self.artifact = 0
    if self.name == "Spheric Guardian":
      self.barricade = True
      self.artifact = 3
    else:
      self.barricade = False
      self.artifact = 0
    self.vulnerable = 0
    self.weak = 0
    self.strength = 0
  def die(self, enemy):
    print(f"{enemy.name} has died.")
    active_enemies.remove(enemy)
  def debuff_and_buff_check(self):
    pass
  def enemy_turn(self):
    global turn
    if self.name == 'Spheric Guardian':
      if turn == 1:
        # Gives the enemy 25 block
        self.block += 25
        ansiprint("<reverse>Activate</reverse>")
        sleep(1)
        ansiprint(f"{self.name} gained <light-blue>25 block</light-blue>")
        sleep(1.5)
        system("clear")
        turn += 1
      elif turn == 2:
        damage(10, player)
        player.frail += 5
        ansiprint(f"{self.name} dealt 10 damage to player and inflicted 5 <yellow>Frail</yellow>(Recieve 25% less block from cards)")
        sleep(2)
        system("clear")
        turn += 1
      elif turn % 2 == 0 and turn > 2:
        damage(10, player)
        print(f"{self.name} dealt 10 damage to player")
        sleep(0.5)
        damage(10, player)
        print(f"{self.name} dealt 10 damage to player")
        sleep(1.5)
        system("clear")
      elif turn % 2 == 1 and turn > 2:
        damage(10, player)
        self.block += 15
        ansiprint(f"{self.name} dealt 10 damage to player and gained <light-blue>15 block</light-blue>")
        sleep(1.5)
        system("clear")
  def show_status(self):
    status = f"{self.name} (<red>{self.health} / {self.max_health}</red> | <light-blue>{self.block} Block</light-blue>)"
    if self.barricade is True:
      status += " | <light-cyan>Barricade</light-cyan>"
    if self.artifact > 0:
      status += f" | <light-cyan>Artifact {self.artifact}</light-cyan>"
    if self.vulnerable > 0:
      status += f" | <light-cyan>Vulnerable {self.vulnerable}</light-cyan>"
    ansiprint(status, "\n")
Spheric_Guardian = Enemy(20, 20, 40, "Spheric Guardian")
# Creates a list of enemies availible
encounters = [[Spheric_Guardian]]
# Chooses a random enemy to spawn
def start_combat():
  encounter_enemies = random.choice(encounters)
  for enemy in encounter_enemies:
    return enemy
def end_player_turn():
  player.discard_pile.extend(player.hand)
  player.hand = []
  player.draw_cards()
  player.energy = player.max_energy
  for enemy in active_enemies:
    if enemy.health <= 0:
      enemy.die(enemy)
    else:
      enemy.enemy_turn()
    enemy.debuff_and_buff_check()
  sleep(1.5)
  system("clear")
# Creates an enemy that has all the attributes of a randomly chosen enemy
active_enemies = []
active_enemies.append(start_combat())
# Shows every card in the player's inventory with it's name, defintion, and energy cost
def cards_display():
  # Puts a number before each card
  counter = 1
  # Repeats for every card in the player's hand
  for card in player.hand:
    # Prints in red if the player doesn't have enough energy to use the card
    if card["Energy"] > player.energy:
      ansiprint(f"{counter}: <red>{card['Name']}</red> | <light-red>{card['Info']}</light-red> | <red>{card['Energy']}</red>")
    # Otherwise, print in full color
    else:
      ansiprint(f"{counter}: <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
    # Adds one to the counter to make a numbered list(Ex. 1: Defend// 2: Strike...)
    counter += 1
# Function that displays all the relevant info to the player
def display_ui():
  # Displays all the card in the player's hand(Look at the function above for code)
  cards_display()
  print()
  # Displays the number of cards in the draw and discard pile
  print(f"Draw pile: {len(player.draw_pile)}\nDiscard pile: {len(player.discard_pile)}\n")
  # Displays the player's current health, block, and energy
  player.show_status()
  print()
  counter = 1
  for enemy in active_enemies:
    enemy.show_status()
def neow_interact():
  print("1: WIP \n2: Enemies in your first 3 combats will have 1 hp \n3:")
cards = {
  "Strike": {"Name": "Strike", "Damage": 6, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 6 damage"},
  "Strike+": {"Name": "<green>Strike+</green>", "Upgraded": True, "Damage": 9, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal <green>9</green> damage"},

  "Defend": {"Name": "Defend", "Block": 5, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain 5 <yellow>Block</yellow>"},
  "Defend+": {"Name": "<green>Defend+</green>", "Upgraded": True, "Block": 8, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain <green>8</green> <yellow>Block</yellow"},

  "Bash": {"Name": "Bash", "Damage": 8, "Vulnerable": 2, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 8 damage. Apply 2 <yellow>Vulnerable</yellow>"},
  "Bash+": {"Name": "<green>Bash+</green>", "Upgraded": True, "Damage": 10, "Vulnerable": 3, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal <green>10</green> damage. Apply <green>3</green> <yellow>Vulnerable</yellow>"}
}
"""
//Player stats//
health       =  80
block        =  0
max_health   =  80
energy       =  3
max_energy   =  3
deck         =  (blah, blah look at the big list)
hand         =  [](empty)
draw_pile    =  [](empty)
discard_pile =  [](empty)
"""
player = Player(80, 0, 80, 3, 3, [cards["Strike"], cards["Strike"], cards["Strike"], cards["Strike"], cards["Strike"], cards["Defend"], cards["Defend"], cards["Defend"], cards["Defend"], cards["Bash"]], [], [], [], [])
# Shuffles the player's deck into the draw pile
player.draw_pile = random.sample(player.deck, len(player.deck))
# Gives the player 5 cards to start the game(Is only run ONCE in the code)
player.draw_cards()