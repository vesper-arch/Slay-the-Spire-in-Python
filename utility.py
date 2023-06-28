from time import sleep
from os import system
import math
from extras import cards_display, player, active_enemies


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