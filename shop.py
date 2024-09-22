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
from helper import Displayer, get_attribute, sleep
from items import create_all_cards, create_all_potions, create_all_relics
from message_bus_tools import Relic, Potion, Card


# Helper functions for displaying cards, potions, and relics.
# These really should be inside the classes for those items
#------------------------------------------------------------
def relic_pretty_string(relic: Relic, valid):
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
    # print(f"<{name_colors[relic.rarity]}>{relic.name}</{name_colors[relic.rarity]}> | {relic.player_class} | <yellow>{relic.info}</yellow> | <dark-blue><italic>{relic.flavor_text}</italic></dark-blue>")
    return f"<{name_colors[relic.rarity]}>{relic.name}</{name_colors[relic.rarity]}> | {relic.player_class} | <yellow>{relic.info}</yellow> | <dark-blue><italic>{relic.flavor_text}</italic></dark-blue>"
  else:
    return f"<light-black>{relic.name} | {relic.player_class} | {relic.info} | {relic.flavor_text}</light-black>"

def potion_pretty_string(potion: Potion, valid):
  if valid:
    class_colors = {'Ironclad': 'red', 'Silent': 'dark-green', 'Defect': 'true-blue', 'Watcher': 'watcher-purple', 'Any': 'white'}
    rarity_colors = {'Common': 'white', 'Uncommon': 'uncommon', 'Rare': 'rare'}
    chosen_class_color = class_colors[potion.player_class]
    chosen_rarity_color = rarity_colors[potion.rarity]
    return f"<{chosen_rarity_color}>{potion.name}</{chosen_rarity_color}> | <{chosen_class_color}>{potion.player_class}</{chosen_class_color}> | <yellow>{potion.info}</yellow>"
  else:
    return f"<light-black>{potion.name} | {potion.player_class} | {potion.info}</light-black>"

def determine_item_category(item):
  # A massive hack to try to figure out if we've got a card, potion, or relic
  try:
    name = get_attribute(item, 'Name')
  except KeyError as e:
    raise KeyError(f'The following item has no Name: {item}') from e
  card_names = [c.name for c in create_all_cards()]
  potion_names = [p.name for p in create_all_potions()]
  relic_names = [r.name for r in create_all_relics()]
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
    return item.pretty_print()
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

    def get_rarity(self, item):
      '''Gets the rarity of an item. Items can be cards which have rarity as a property, or relics which have rarity as a key in the dictionary.'''
      return get_attribute(item, 'Rarity')

    def set_price(self):
        '''Set the price of the item based on its rarity.'''
        assert self.get_rarity(self.item), f"Item {self.item} has no rarity."
        rarity = self.get_rarity(self.item)
        if rarity in (Rarity.BASIC, Rarity.COMMON, Rarity.STARTER):
            return random.randint(45, 55)
        elif rarity == Rarity.UNCOMMON:
            return random.randint(68, 82)
        elif rarity == Rarity.RARE:
            return random.randint(135, 165)
        elif rarity in (Rarity.CURSE, Rarity.SHOP, Rarity.SPECIAL, Rarity.EVENT, Rarity.BOSS):
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
      all_cards:list[Card] = create_all_cards()
      attack_cards = [c for c in all_cards if c.type == "Attack" and c.player_class != "Colorless"]
      skill_cards = [c for c in all_cards if c.type == "Skill" and c.player_class != "Colorless"]
      power_cards = [c for c in all_cards if c.type == "Power" and c.player_class != "Colorless"]
      if len(attack_cards) >= 2:
        items.extend(random.sample(attack_cards, 2))
      if len(skill_cards) >= 2:
        items.extend(random.sample(skill_cards, 2))
      if len(power_cards) >= 1:
        items.extend(random.sample(power_cards, 1))

      colorless_cards = [c for c in all_cards if c.player_class == "Colorless"]
      colorless_uncommon = [c for c in colorless_cards if c.rarity == Rarity.UNCOMMON]
      colorless_rare = [c for c in colorless_cards if c.rarity == Rarity.RARE]
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
      name = get_attribute(self.items[choice].item, "Name")
      price = self.items[choice].price
      ansiprint(f"<bold>You bought {name} for {price} gold</bold>.")
      sleep(0.5)
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
