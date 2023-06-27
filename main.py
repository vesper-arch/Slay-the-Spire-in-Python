import random, math
from os import system
from time import sleep
from ansimarkup import parse, ansiprint

turn = 0
# Defines a class called Card. This class will give the given variable the energy_cost, damage, and name attributes
def damage(damage, target):
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
  def __init__(self, health, block, max_health, energy, max_energy, deck, hand, draw_pile, discard_pile, exhaust_pile):
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

  def use_card(self, card, target):
    if card == cards["Strike"]:
      self.use_strike(target)
    elif card == cards['Bash']:
      self.use_bash(target)
    elif card == cards['Defend']:
      self.use_defend()
  def use_strike(self, targeted_enemy):
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
  def use_bash(self, targeted_enemy):
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
  def blocking(self, block):
    if self.frail > 0:
      self.block += math.floor(block * 0.75)
    else:
      self.block += block
  def heal(self, heal):
    self.health += heal
    self.health = min(self.health, self.max_health)
  def RemoveCardFromDeck(self, card, type):
    while True:
      if type == "Remove":
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
      elif type == 'Upgrade':
        player.deck.remove(card)
        player.deck.append(cards[card["Name", '+']])
  def show_status(self):
    status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)"
    if self.weak > 0:
      status += f" | <light-cyan>Weak: {self.weak}</light-cyan>"
    if self.frail > 0:
      status += f" | <light-cyan>Frail: {self.frail}</light-cyan>"
    if self.vulnerable > 0:
      status += f" | <light-cyan>Vulnerable: {self.vulnerable}</light-cyan>"
    ansiprint(status, "\n")
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
# Outer loop is for the whole game
def combat():
  global turn
  turn = 1

  while len(active_enemies) > 0:
    # Removes the player's block at the beginning of their turn
    player.block = 0
    for enemy in active_enemies:
      if enemy.barricade == True:
        ansiprint(f"{enemy.name}'s block was not removed because of <light-cyan>Barricade</light-cyan>")
      else:
        enemy.block = 0
    # Player's turn ends when the their energy is out
    while True:
      display_ui()
      # Asks the user what card they want to use
      try:
        ansiprint("What card do you want to use?(<red>[0] to end turn</red>) > ", end='')
        card_used = int(input(""))
        if len(active_enemies) > 1:
          target = int(input("What enemy do you want to use it on?"))
        else:
          target = 1
        if card_used == 0:
          system("clear")
          break
        # Checks if the number the user inputted is within range of the player.hand list
        if card_used - 1 in range(0, len(player.hand)) and player.hand[card_used - 1]["Energy"] <= player.energy:
          player.use_card(player.hand[card_used - 1], active_enemies[target - 1])
          # if the enemy dies, break out of the current loop, therefore going straight to the end_turn function
          if active_enemies[target - 1].health == 0:
            system("clear")
            break
        # prevents from using a card that the player doesn't have enough energy for
        elif player.hand[card_used - 1]["Energy"] > player.energy:
          system("clear")
          ansiprint("<red>Not enough energy</red>")
          sleep(1.5)
          system("clear")
          continue
        # Numbers less than one will cause problems and this catches it
        else:
          system("clear")
          ansiprint("<red>Card not in inventory.</red>")
          sleep(1.5)
          system("clear")
          continue
      # Won't crash if the user inputted something that wasn't a number
      except ValueError:
        system("clear")
        ansiprint("<red>Please enter an number</red>")
        sleep(1.5)
        system("clear")
        continue
      # Won't crash if the user inputted a card that they didn't have
      except IndexError:
        system("clear")
        ansiprint("<red>Card not in inventory</red>")
        sleep(1.5)
        system("clear")
        continue
    # After the player's energy has run out, discard their cards, give them 5 new ones, refil their energy, and make the enemy attack
    end_player_turn()
def rest():
  while True:
    ansiprint("You come across a <green>Rest Site</green>")
    sleep(1)
    try:
      action = int(input("1:Rest(Heal for 30 percent of your max health)\nor \n2:Upgrade a card in you deck?"))
    except ValueError:
      print("You have to enter a number")
      sleep(1)
      system("clear")
      continue
    if action == 1:
      player.heal(math.floor(player.max_health//100 * 0.30))
    elif action == 2:
      pass
combat()
