import math
from time import sleep
from os import system
import random
from ansimarkup import parse, ansiprint
from entities import Player, cards, Enemy
from utility import damage

turn = 0
# Defines a class called Card. This class will give the given variable the energy_cost, damage, and name attributes


Spheric_Guardian = Enemy(20, 20, 40, "Spheric Guardian")
# Creates a list of enemies availible
encounters = [[Spheric_Guardian]]
# Chooses a random enemy to spawn
def start_combat():
  encounter_enemies = random.choice(encounters)
  for enemy in encounter_enemies:
    return enemy
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
def neow_interact():
  print("1: WIP \n2: Enemies in your first 3 combats will have 1 hp \n3:")
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