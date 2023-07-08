import math
import random
from time import sleep
from os import system
from ansimarkup import parse, ansiprint
from utility import cards, damage, active_enemies, combat_turn
class Player:
  """
  Attributes:::
  health: Player's current health
  block: Block reduces the damage deal by attacks and is removed at the start of their turn
  max_health: Maximum amount of health the player can have
  energy: Used to play cards
  max_energy: Maximum amount of energy the player can have
  deck: All the cards that can appear in game. Players can collect cards to add to the deck
  hand: The cards availible to play at any given time
  draw_pile: A randomized instance of the deck, cards are drawn in order from it.(All cards from the discard pile are shuffled into this when the draw pile is empty)
  discard_pile: Cards get put here when they are played
  exhaust_pile: List of exhausted cards
  """
  def __init__(self, health:int, block:int, max_health:int, energy:int, max_energy:int, deck:list, hand:list, draw_pile:list, discard_pile:list, exhaust_pile:list):
    self.health = health
    self.block = block
    self.name = "Ironclad"
    self.max_health = max_health
    self.energy = energy
    self.max_energy = max_energy
    self.deck = deck
    self.hand = hand
    self.draw_pile = draw_pile
    self.discard_pile = discard_pile
    self.draw_strength = 5
    self.exhaust_pile = exhaust_pile
    self.weak = 0
    self.frail = 0
    self.vulnerable = 0
    self.entangled = False

  def use_card(self, card:dict, target:object):
    if card == cards["Strike"]:
      self.use_strike(target)
    elif card == cards['Bash']:
      self.use_bash(target)
    elif card == cards['Defend']:
      self.use_defend()
  def use_strike(self, targeted_enemy:object):
    print()
    # If the enemy has the Vulnerable debuff applied to it, multiply the damage by 1.5 and round it up to the nearest whole number
    damage(cards['Strike']['Damage'], targeted_enemy)
    # Prevents the enemy's health from going below 0
    targeted_enemy.health = max(targeted_enemy.health, 0)
    # Displays the damage dealt and the name of the enemy dealt to
    if targeted_enemy.vulnerable > 0:
      ansiprint(f"Player dealt <green>{cards['Strike']['Damage'] * 1.50:.0f}</green> damage to {targeted_enemy.name}")
    else:
      print(f"Player dealt {cards['Strike']['Damage']} to {targeted_enemy.name}")
    # Takes the card's energy cost away from the player's energy
    self.energy -= cards["Strike"]["Energy"]
    # Removes the card from the player's cards
    self.hand.remove(cards["Strike"])
    self.discard_pile.append(cards["Strike"])
    print()
    sleep(1)
    system("clear")
  def use_bash(self, targeted_enemy:object):
    print()
    # If the enemy has the Vulnerable debuff applied to it, multiply the damage by 1.5 and round it up to the nearest whole number
    damage(cards['Bash']['Damage'], targeted_enemy)
    # prevents the enemy's health from going below 0
    targeted_enemy.health = max(targeted_enemy.health, 0)
    player.energy -= cards["Bash"]["Energy"]
    player.energy = max(player.energy, 0)
    if targeted_enemy.artifact > 0:
      ansiprint(f"{self.name} dealt {cards['Bash']['Damage']} damage to {targeted_enemy.name}. <yellow>Vulnerable</yellow> was blocked by {targeted_enemy.name}'s <light-cyan>Artifact</light-cyan>")
      targeted_enemy.artifact -= 1
    else:
      ansiprint(f"{self.name} dealt {cards['Bash']['Damage']} to {targeted_enemy.name} and applied {cards['Bash']['Vulnerable']} <yellow>Vulnerable</yellow>")
      targeted_enemy.vulnerable += 2
    # Adds 2 vulnerable to the enemy if the enemy does not have the Artifact debuff
    # Puts the card in the discard pile
    player.hand.remove(cards['Bash'])
    player.discard_pile.append(cards['Bash'])
    print()
    sleep(1.5)
    system("clear")
  def use_defend(self):
    print()
    if self.frail > 0:
      self.blocking(math.floor(cards['Defend']['Block']))
      ansiprint(f"{self.name} gained <red>{math.floor(cards['Defend']['Block'] * 0.75)}</red> <light-cyan>Block</light-cyan> | Block was reduced by <light-cyan>Frail</light-cyan>")
    else:
      self.blocking(cards['Defend']["Block"])
      print(f"Player gained <blue>{cards['Defend']['Block']} Block</blue>")
    player.energy -= cards["Defend"]["Energy"]
    player.hand.remove(cards['Defend'])
    player.discard_pile.append(cards['Defend'])
    print()
    sleep(1.5)
    system("clear")
  def draw_cards(self):
    if len(player.draw_pile) < 5:
      player.draw_pile.extend(random.sample(player.discard_pile, len(player.discard_pile)))
      player.discard_pile = []
    player.hand = player.draw_pile[-5:]
    # Removes those cards
    player.draw_pile = player.draw_pile[:-5]
  def blocking(self, block:int):
    if self.frail > 0:
      self.block += math.floor(block * 0.75)
    else:
      self.block += block
  def heal(self, heal):
    self.health += heal
    self.health = min(self.health, self.max_health)
  def RemoveCardFromDeck(self, card:dict, action:str):
    while True:
      if action == "Remove":
        counter = 1
        for card in player.deck:
          ansiprint(f"{counter}: <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
          counter += 1
        try:
          remove_index = int(input("What card do you want to remove?")) - 1
        except ValueError:
          print("You have to enter a number")
          sleep(1)
          system("clear")
          continue
        player.deck.remove(card)
      elif action == 'Upgrade':
        player.deck.remove(card)
        player.deck.append(cards[card["Name", '+']])
  def show_status(self, combat=True):
    if combat is True:
      status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)"
      if self.weak > 0:
        status += f" | <light-cyan>Weak: {self.weak}</light-cyan>"
      if self.frail > 0:
        status += f" | <light-cyan>Frail: {self.frail}</light-cyan>"
      if self.vulnerable > 0:
        status += f" | <light-cyan>Vulnerable: {self.vulnerable}</light-cyan>"
    else:
      status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue>)"
    ansiprint(status, "\n")
  def end_player_turn(self):
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
class Enemy:
  def __init__(self, health:int, max_health:int, block:int, name:str, order:list, moves:dict):
    '''
    Attributes::
    health: Current health[int]
    max_health: Maximum health[int]
    block: Current block[int]
    name: Enemy name[str]
    order: Order of moves(planning on using parsing to run)[array, list, whatever]
    moves: All moves the enemy can use[2D dict]
    barricade: Block is not removed at the start of combat[bool]
    artifact: Blocks the next debuff[int]
    vulnerable: Takes 50% more damage from attacks[int](duration stack)
    weak: Deals 25% less damage with attacks[int](duration stack)
    strength: Deal more damage[int](intensity stack)
    '''
    self.health = health
    self.max_health = max_health
    self.block = block
    self.name = name
    self.order = order
    self.moves = moves
    self.barricade = False
    self.artifact = 0
    if self.name == "Spheric Guardian":
      self.barricade = True
      self.artifact = 3
    self.vulnerable = 0
    self.weak = 0
    self.strength = 0
    # PArsing to determine the order of moves
    for item in self.order:
      # Contains all the items with percent symbols in them
      parsed_order = []
      # Adds the respective items
      if "%" in item:
        parsed_order.append(item)
      # Dictionary is basically (everything before this->"%"[string]: everything after this->"%" exclusive[int])
      # Contains the percent chances for each move
      percent_chances = {text[:text.index("%")]: int(text[text.index("%") + 1]) for text in parsed_order}
      # Checks if the first character is a right facing arrow
      if item[:1] == ">":
        # List of all the indexes and extras instructions in between ()s
        repeats = [item[item.index["("] + 1: item[item.index[")"]]].split(",")]
        for index in repeats:
          if index.isdigit() is True:
            int(index)
          else:
            if index == "inf":
              rep_inf = True
              repeats.remove(index)

  def die(self):
    """
    Dies.
    """
    print(f"{self.name} has died.")
    active_enemies.remove(self)
  def debuff_and_buff_check(self):
    """
    Not finished
    """
    pass
  def enemy_turn(self):
    global combat_turn
    if self.name == 'Spheric Guardian':
      if combat_turn == 1:
        # Gives the enemy 25 block
        self.block += 25
        ansiprint("<reverse>Activate</reverse>")
        sleep(1)
        ansiprint(f"{self.name} gained <light-blue>25 block</light-blue>")
        sleep(1.5)
        system("clear")
        combat_turn += 1
      elif combat_turn == 2:
        # Deals 10 damage to the player
        damage(10, player)
        player.frail += 5
        ansiprint(f"{self.name} dealt 10 damage to player and inflicted 5 <yellow>Frail</yellow>(Recieve 25% less block from cards)")
        sleep(2)
        system("clear")
        combat_turn += 1
      elif combat_turn % 2 == 0 and combat_turn > 2:
        # Deals 10 damage to the player twice
        damage(10, player)
        print(f"{self.name} dealt 10 damage to player")
        sleep(0.5)
        damage(10, player)
        print(f"{self.name} dealt 10 damage to player")
        sleep(1.5)
        system("clear")
      elif combat_turn % 2 == 1 and combat_turn > 2:
        # Deals 10 damage to the player and gains 15 block
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

# Characters
player = Player(80, 0, 80, 3, 3, [cards["Strike"], cards["Strike"], cards["Strike"], cards["Strike"], cards["Strike"], cards["Defend"], cards["Defend"], cards["Defend"], cards["Defend"], cards["Bash"]], [], [], [], [])
# Enemies
Spheric_Guardian = Enemy(20, 20, 40, "Spheric Guardian", ["Activate", "Attack/Debuff", "Slam", "Harden", "rep(2,3,inf)"], {"Activate": {"Block": 25},
                                                                                                                           "Attack/Debuff": {"Damage": 10, "Frail": 5},
                                                                                                                           "Slam": {"Damage": 10, "Times": 2},
                                                                                                                           "Harden": {"Damage": 10, "Block": 15}})
encounters = [[Spheric_Guardian]]
