import random, math
from os import system
from time import sleep
# Text colors and variants
Faint = "\033[2m"
Italic = "\033[3m"
Underline = "\033[4m"
Blink = "\033[5m"
Negative = "\033[7m"
Crossed = "\033[9m"
End = "\033[0m"
Bold = "\033[1m"
Black = "\033[0;30m" + Bold
Red = "\033[0;31m" + Bold
Orange = '\033[38;2;255;135;0m' + Bold
Green = "\033[0;32m" + Bold
Brown = "\033[0;33m" + Bold
Blue = "\033[0;34m" + Bold
Turquoise = '\033[38;2;64;224;208m' + Bold
Purple = "\033[0;35m" + Bold
Cyan = "\033[0;36m" + Bold
Light_gray = "\033[0;37m" + Bold
Dark_gray = "\033[1;30m" + Bold
Light_red = "\033[1;31m" + Bold
Light_green = "\033[1;32m" + Bold
Yellow = "\033[38;2;255;255;0m" + Bold
Light_blue = "\033[1;34m" + Bold
Light_purple = "\033[1;35m" + Bold
Light_cyan = "\033[1;36m" + Bold
Light_white = "\033[1;37m" + Bold

# Defines a class called Card. This class will give the given variable the energy_cost, damage, and name attributes
def damage(damage, target):
  if damage < target.block:
    target.block -= damage
  elif damage > target.block:
    target.health -= damage - target.block
    target.block == 0
  elif damage == target.block:
    target.block -= damage
class Card:
  def __init__(self, energy_cost, change, name, definition, debuff=None, debuff_length=0, tags=[]):
    """
    Attributes:::
    energy_cost: The amount of energy required to use it
    change: The amount of energy, block, damage, ect the card has
    name: The display name of the card
    definition: The definition of what the card does
    debuff:(Optional) The debuff(s) that the card inflicts
    debuff_length:(Optional) The amount of turns the debuff lasts for
    tags:(Exhaust, Innate, etc) Special tags for the card
    """
    self.energy_cost = energy_cost
    self.change = change
    self.name = name
    self.definition = definition
    self.debuff = debuff
    self.debuff_length = debuff_length
    self.tags = tags
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
  def die(self, enemy):
    print(f"{enemy.name} has died.")
    active_enemies.remove(enemy)
  def debuff_and_buff_check(self):
    for debuff_buff, debuff_buff_length in self.debuff_buffs.items():
      if debuff_buff[-5:] != '(Perm)':
        self.debuff_buffs[debuff_buff] -= 1
        if self.debuff_buffs[debuff_buff] == 0:
          del self.debuff_buffs[debuff_buff]
          break
  def enemy_turn(self):
    global turn
    if self.name == 'Spheric Guardian':
      if turn == 1:
        # Gives the enemy 25 block
        self.block += 25
        print(f"{Bold}Activate{End}")
        sleep(1)
        print(f"{self.name} gained {Blue}25 block{End}")
        sleep(1.5)
        system("clear")
        turn += 1
      elif turn == 2:
        damage(10, player)
        player.debuff_buffs["Frail"] = 5
        print(f"{self.name} dealt 10 damage to player and inflicted 5 {Yellow}Frail{End}(Recieve 25% less block from cards)")
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
        print(f"{self.name} dealt 10 damage to player and gained {Blue}15 block{End}")
        sleep(1.5)
        system("clear")
# CancerousRodent is an enemy with 50 max health and the name of "Cancerous Rodent"
Spheric_Guardian = Enemy(20, 20, 5, "Spheric Guardian", {"Barricade(Perm)": 1, "Artifact(Perm)": 3} )
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
  debuff_buffs: Current debuff_buffs and buffs
  """
  def __init__(self, health, block, max_health, energy, max_energy, deck, hand, draw_pile, discard_pile, debuff_buffs={}):
    self.health = health
    self.block = block
    self.max_health = max_health
    self.energy = energy
    self.max_energy = max_energy
    self.deck = deck
    self.hand = hand
    self.draw_pile = draw_pile
    self.discard_pile = discard_pile
    self.debuff_buffs = debuff_buffs
  def use_card(self, card, target):
    if card == strike:
      self.use_strike(target)
    elif card == bash:
      self.use_bash(target)
    elif card == defend:
      self.use_defend()
    elif card == seeing_red:
      self.use_seeing_red()
  def use_strike(self, targeted_enemy):
    print()
    # If the enemy has the Vulnerable debuff applied to it, multiply the damage by 1.5 and round it up to the nearest whole number
    if 'Vulnerable' in targeted_enemy.debuff_buffs:
      damage(math.ceil(strike.change * 1.50), targeted_enemy)
    else:
      damage(strike.change, targeted_enemy)
    # Prevents the enemy's health from going below 0
    targeted_enemy.health = max(targeted_enemy.health, 0)
    # Displays the damage dealt and the name of the enemy dealt to
    if 'Vulnerable' in targeted_enemy.debuff_buffs:
      print(f"Player dealt {Green}{strike.change * 1.50:.0f}{End} damage to {targeted_enemy.name}")
    else:
      print(f"Player dealt {strike.change} to {targeted_enemy.name}")
    # Takes the card's energy cost away from the player's energy
    self.energy -= strike.energy_cost
    # Removes the card from the player's cards
    self.hand.remove(strike)
    self.discard_pile.append(strike)
    print()
    sleep(1)
    system("clear")
  def use_bash(self, targeted_enemy):
    print()
    # If the enemy has the Vulnerable debuff applied to it, multiply the damage by 1.5 and round it up to the nearest whole number
    if 'Vulnerable' in targeted_enemy.debuff_buffs:
      damage(math.ceil(bash.change * 1.50), targeted_enemy)
    else:
      damage(bash.change, targeted_enemy)
    # prevents the enemy's health from going below 0
    targeted_enemy.health = max(targeted_enemy.health, 0)
    player.energy -= bash.energy_cost
    player.energy = max(player.energy, 0)
    if 'Vulnerable' in targeted_enemy.debuff_buffs:
      print(f"Player dealt {Green}{bash.change * 1.50:.0f}{End} damage to {targeted_enemy.name} and applied 2 {Yellow}Vulnerable{End}.")
    elif 'Artifact(Perm)' in targeted_enemy.debuff_buffs and 'Vulnerable' in targeted_enemy.debuff_buffs:
      print(f"Player dealt {Green}{bash.change * 1.50:.0f}{End} damage to {targeted_enemy.name}. Vulnerable was blocked by Artifact")
    else:
      print(f"Player dealt {bash.change} damage to {targeted_enemy.name} and made them {Yellow}Vulnerable{End}(Recieve 50% more damage from attacks).")
   # Adds 2 vulnerable to the enemy if the enemy does not have the Artifact debuff
    if 'Vulnerable' not in targeted_enemy.debuff_buffs:
      targeted_enemy.debuff_buffs['Vulnerable'] = 2
    elif 'Artifact(Perm)' in targeted_enemy.debuff_buffs:
      targeted_enemy.debuff_buffs['Artifact(Perm)'] -= 1
    else:
      targeted_enemy.debuff_buffs['Vulnerable'] += 2
    # Puts the card in the discard pile
    player.hand.remove(bash)
    player.discard_pile.append(bash)
    print()
    sleep(1.5)
    system("clear")
  def use_defend(self):
    print()
    player.block += defend.change
    player.energy -= defend.energy_cost
    print(f"Player gained {Light_blue}{defend.change} Block{End}")
    player.hand.remove(defend)
    player.discard_pile.append(defend)
    print()
    sleep(1.5)
    system("clear")
  def use_seeing_red(self):
    print()
    player.energy += seeing_red.change
    player.energy -= seeing_red.energy_cost
    print(f"Player gained {Orange}2 Energy{End}")
    player.hand.remove(seeing_red)
    player.discard_pile.append(seeing_red)
    print()
    sleep(1)
    system('clear')
  def draw_cards(self):
    if len(player.draw_pile) < 5:
      player.draw_pile.extend(random.sample(player.discard_pile, len(player.discard_pile)))
      player.discard_pile = []
    # Gives the player the top 5 cards in the draw pile
    player.hand = player.draw_pile[-5:]
    # Removes those cards
    player.draw_pile = player.draw_pile[:-5]
# Shows every card in the player's inventory with it's name, defintion, and energy cost
def cards_display():
  # Puts a number before each card
  counter = 1
  # Repeats for every card in the player's hand
  for card in player.hand:
    # Prints in red if the player doesn't have enough energy to use the card
    if card.energy_cost > player.energy:
      print(f"{counter}: {Red}{card.name:<15}{card.energy_cost} Energy{Red:<15}{card.definition}{End}")
    # Otherwise, print in full color
    else:
      print(f"{counter}: {Turquoise}{card.name:<15}{Orange}{card.energy_cost} Energy{Yellow:<30}{card.definition}{End}")
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
  print(f"player: \nHealth = {Green}{player.health}/{player.max_health} {End}// {Light_blue}{player.block} Block{End} \nEnergy = {Red}{player.energy}/{player.max_energy}{End}")
  print()
  counter = 1
  for enemy in active_enemies:
    # Displays the active enemy's name and health
    print(f"{enemy.name}\nHealth: {Red}{enemy.health}{End}  //  {Blue}{enemy.block} Block{End}  //  Debuffs: ", end='')
    # Prints out all the debuff_buffs the enemy currently has with the amount of turns left
    for debuff_buffs, debuff_length in enemy.debuff_buffs.items():
      print(f"{debuff_length} {Light_green}{debuff_buffs}{End}", end=', ')
    counter += 1
def neow_interact():
  print("1: WIP \n2: Enemies in your first 3 combats will have 1 hp \n3:")
# Creates a card that deals 6 damage to the enemy and costs 1 energy
strike = Card(1, 6, "Strike", "Deal 6 damage.")
# Creates a card that deals 8 damage, makes the enemy Vulnerable(Takes 50% more damage) for 2 turns, and costs 2 energy
bash = Card(2, 8, "Bash", "Deal 8 damage. Apply 2 Vulnerable", 'Vulnerable', 2)
# Creates a card that gives the player 5 block and costs 1 energy
defend = Card(1, 5, "Defend", "Gain 5 block")
# Creates a card that gives the player 2 energy and costs 1 energy but is removed from play for the rest of combat
seeing_red = Card(1, 2, "Seeing Red", "Gain 2 Energy. Exhaust")
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
player = Player(80, 0, 80, 3, 3, [strike, strike, strike, strike, strike, defend, defend, defend, defend, bash], [], [], [])
# Shuffles the player's deck into the draw pile
player.draw_pile = random.sample(player.deck, len(player.deck))
# Gives the player 5 cards to start the game(Is only run ONCE in the code)
player.draw_cards()
# Outer loop is for the whole game
turn = 0
def combat():
  global turn
  turn = 1
  while len(active_enemies):
    # Removes the player's block at the beginning of their turn
    player.block = 0
    # Player's turn ends when the their energy is out
    while player.energy > 0:
      display_ui()
      # Asks the user what card they want to use
      try:
        card_used = int(input(f"\nWhat card do you want to use?({Red}[0] to end turn{End}) > "))
        if len(active_enemies) > 1:
          target = int(input("What enemy do you want to use it on?"))
        else:
          target = 1
        if card_used == 0:
          break
        # Checks if the number the user inputted is within range of the player.hand list
        if card_used - 1 in range(0, len(player.hand)) and player.hand[card_used - 1].energy_cost <= player.energy:
          player.use_card(player.hand[card_used - 1], active_enemies[target - 1])
          # if the enemy dies, break out of the current loop, therefore going straight to the end_turn function
          if active_enemies[target - 1].health == 0:
            system("clear")
            break
        # prevents from using a card that the player doesn't have enough energy for
        elif player.hand[card_used - 1].energy_cost > player.energy:
          system("clear")
          print(f"{Red}Not enough energy{End}")
          sleep(1.5)
          system("clear")
          continue
        # Numbers less than one will cause problems and this catches it
        else:
          system("clear")
          print(f"{Red}Card not in inventory.///{End}")
          sleep(1.5)
          system("clear")
          continue
      # Won't crash if the user inputted something that wasn't a number
      except ValueError:
        system("clear")
        print(f"{Red}Please enter an number{End}")
        sleep(1.5)
        system("clear")
        continue
      # Won't crash if the user inputted a card that they didn't have
      except IndexError:
        system("clear")
        print(f"{Red}Card not in inventory{End}")
        sleep(1.5)
        system("clear")
        continue
    # After the player's energy has run out, discard their cards, give them 5 new ones, refil their energy, and make the enemy attack
    end_player_turn()
combat()
