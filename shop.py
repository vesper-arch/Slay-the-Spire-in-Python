
# The shop contains:
# 5 Colored cards:
#  - 2 Attack cards, 2 skill cards, and 1 Power card
#    - Common: 45-55 Gold
#    - Uncommon: 68-82 Gold
#    - Rare: 135-165 Gold
#  - One card is always on sale by 50%
# 2 Colorless Cards:
# - uncommmon on the left (81-99)
# - Rare on the right (162-198)
# Relics:
# Shop Relic on the right:
#   Common: 143 - 157 Gold
#   Uncommon: 238 - 262 Gold
#   Rare: 285 - 315 Gold
#   Shop: 143 - 157 Gold
# Potions:
# Common: 48 - 52 Gold
# Uncommon: 72 - 78 Gold
# Rare: 95 - 105 Gold
# Card Removal Service
# Can only be used once per shop.
# Costs 75 Gold initially, increases cost by 25 Gold every time it is used at any shop.
# Woo.... lots of stuff to do here.

import random
import time

from ansi_tags import ansiprint
from definitions import CardCategory, Rarity
from helper import Displayer
from items import cards, potions, relics


# Helper functions for displaying cards, potions, and relics.
# These really should be inside the classes for those items
#------------------------------------------------------------
def card_pretty_string(card, valid):
  if valid:
    changed_energy = 'light-red' if not card.get('Changed Energy') else 'green'
    return f"<{card['Rarity'].lower()}>{card['Name']}</{card['Rarity'].lower()}> | <{card['Type'].lower()}>{card['Type']}</{card['Type'].lower()}> | <{changed_energy}>{card.get('Energy', 'Unplayable')}{' Energy' if card.get('Energy') is not None else ''}</{changed_energy}> | <yellow>{card['Info']}</yellow>".replace('Σ', '').replace('Ω', '')
  else:
    return f"<light-black>{card['Name']} | {card['Type']} | {card.get('Energy', 'Unplayable')}{' Energy' if card.get('Energy') else ''} | {card['Info']}</light-black>".replace('Σ', '').replace('Ω', '')

def relic_pretty_string(relic, valid):
  if valid:
    name_colors = {
      'Starter': 'starter',
      'Common': 'white',
      'Uncommon': 'uncommon',
      'Rare': 'rare',
      'Event': 'event',
      'Shop': 'rare',
      'Boss': 'rare',
      'Special': 'rare'}
    return f"<{name_colors[relic['Rarity']]}>{relic['Name']}</{name_colors[relic['Rarity']]}> | {relic['Class']} | <yellow>{relic['Info']}</yellow> | <dark-blue><italic>{relic['Flavor']}</italic></dark-blue>"
  else:
    return f"<light-black>{relic['Name']} | {relic['Class']} | {relic['Info']} | {relic['Flavor']}</light-black>"

def potion_pretty_string(potion, valid):
  if valid:
    class_colors = {'Ironclad': 'red', 'Silent': 'dark-green', 'Defect': 'true-blue', 'Watcher': 'watcher-purple', 'Any': 'white'}
    rarity_colors = {'Common': 'white', 'Uncommon': 'uncommon', 'Rare': 'rare'}
    chosen_class_color = class_colors[potion['Class']]
    chosen_rarity_color = rarity_colors[potion['Rarity']]
    return f"<{chosen_rarity_color}>{potion['Name']}</{chosen_rarity_color}> | <{chosen_class_color}>{potion['Class']}</{chosen_class_color}> | <yellow>{potion['Info']}</yellow>"
  else:
    return f"<light-black>{potion['Name']} | {potion['Class']} | {potion['Info']}</light-black>"

def determine_item_category(item):
  # A massive hack to try to figure out if we've got a card, potion, or relic
  try:
    name = item['Name']
  except KeyError as e:
    raise KeyError(f'The following item has no Name: {item}') from e
  card_names = [c['Name'] for c in cards.values()]
  potion_names = [p['Name'] for p in potions.values()]
  relic_names = [r['Name'] for r in relics.values()]
  if name in card_names:
    return CardCategory.CARD
  elif name in potion_names:
    return CardCategory.POTION
  elif name in relic_names:
    return CardCategory.RELIC
  else:
    raise ValueError(f"Item {item} not found in any category")

def category_to_pretty_string(item, valid):
  category = determine_item_category(item)
  if category == CardCategory.CARD:
    return card_pretty_string(item, valid)
  elif category == CardCategory.POTION:
    return potion_pretty_string(item, valid)
  elif category == CardCategory.RELIC:
    return relic_pretty_string(item, valid)
  else:
    raise ValueError(f"Category {category} not understood.")
#------------------------------------------------------------

class SellableItem():
    '''A class to represent an item that can be sold in the shop. This is a wrapper around the actual item, and includes a price.'''
    def __init__(self, item, price=None):
        self.item = item
        if price is not None:
          self.price = price
        else:
          self.price = self.set_price()

    def invalid_string(self):
        pretty_string = category_to_pretty_string(self.item, valid=False)
        return f"<light-black>{self.price:3d} Gold</light-black> : {pretty_string}"

    def valid_string(self):
        pretty_string = category_to_pretty_string(self.item, valid=True)
        return f"<yellow>{self.price:3d} Gold</yellow> : {pretty_string}"

    def set_price(self):
        '''Set the price of the item based on its rarity.'''
        assert "Rarity" in self.item, f"Item {self.item} has no rarity."
        if self.item["Rarity"] in (Rarity.BASIC, Rarity.COMMON, Rarity.STARTER):
            return random.randint(45, 55)
        elif self.item["Rarity"] == Rarity.UNCOMMON:
            return random.randint(68, 82)
        elif self.item["Rarity"] == Rarity.RARE:
            return random.randint(135, 165)
        elif self.item["Rarity"] in (Rarity.CURSE, Rarity.SHOP, Rarity.SPECIAL, Rarity.EVENT, Rarity.BOSS):
            # Unsure what to do with these. We'll set to some high bogus value for now.
            return 999
        else:
            raise ValueError("Item rarity broken")

class Shop():
    def __init__(self, player, items=None):
      self.player = player
      if items is None:
        self.items = self.initialize_items()
      else:
        self.items = items

    def initialize_items(self) -> list[SellableItem]:
      # TODO: Make this class-specific and include relics and potions
      items = []
      all_cards = list(cards.values())
      attack_cards = [c for c in all_cards if c["Type"] == "Attack" and c["Class"] != "Colorless"]
      skill_cards = [c for c in all_cards if c["Type"] == "Skill" and c["Class"] != "Colorless"]
      power_cards = [c for c in all_cards if c["Type"] == "Power" and c["Class"] != "Colorless"]
      if len(attack_cards) >= 2:
        items.extend(random.sample(attack_cards, 2))
      if len(skill_cards) >= 2:
        items.extend(random.sample(skill_cards, 2))
      if len(power_cards) >= 1:
        items.extend(random.sample(power_cards, 1))

      colorless_cards = [c for c in all_cards if "Class" in c and c["Class"] == "Colorless"]
      colorless_uncommon = [c for c in colorless_cards if c["Rarity"] == Rarity.UNCOMMON]
      colorless_rare = [c for c in colorless_cards if c["Rarity"] == Rarity.RARE]
      if len(colorless_uncommon) >= 1:
        items.extend(random.sample(colorless_uncommon, 1))
      if len(colorless_rare) >= 1:
        items.extend(random.sample(colorless_rare, 1))
      return [SellableItem(item) for item in items]

    def loop(self):
      while True:
        ansiprint(f"Welcome to the shop! You have {self.player.gold} gold.")
        choice = Displayer().list_input(
          input_string="Buy something?",
          choices=self.items,
          displayer=self.view_sellables,
          validator=self.validator,
          extra_allowables=['e'])
        if choice == 'e':
          break
        self.buy(choice)

    def buy(self, choice):
      self.player.gold -= self.items[choice].price
      self.player.deck.append(self.items[choice].item)
      ansiprint(f"<bold>You bought {self.items[choice].item['Name']} for {self.items[choice].price} gold</bold>.")
      time.sleep(0.5)
      input("Press Enter to continue...")

    def validator(self, item):
      return item.price <= self.player.gold

    def view_sellables(self, items, validator):
      for idx, item in enumerate(items):
        if validator(item):
          ansiprint(f"{idx+1}: {item.valid_string()}")
        else:
          ansiprint(f"{idx+1}: {item.invalid_string()}")
      ansiprint("e: Exit Shop")
