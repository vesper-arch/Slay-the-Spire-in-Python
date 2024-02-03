
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
from definitions import Rarity
from helper import Displayer
from items import cards, potions, relics


class SellableItem():
    def __init__(self, item):
        self.item = item
        self.price = self.set_price()

    def invalid_string(self):
        card = self.item
        return f"<yellow>{self.price:3d} Gold</yellow> : <light-black>{card['Name']} | {card['Type']} | {card.get('Energy', 'Unplayable')}{' Energy' if card.get('Energy') else ''} | {card['Info']}</light-black>".replace('Σ', '').replace('Ω', '')

    def valid_string(self):
        card = self.item
        changed_energy = 'light-red' if not card.get('Changed Energy') else 'green'
        return f"<yellow>{self.price:3d} Gold</yellow> : <{card['Rarity'].lower()}>{card['Name']}</{card['Rarity'].lower()}> | <{card['Type'].lower()}>{card['Type']}</{card['Type'].lower()}> | <{changed_energy}>{card.get('Energy', 'Unplayable')}{' Energy' if card.get('Energy') is not None else ''}</{changed_energy}> | <yellow>{card['Info']}</yellow>".replace('Σ', '').replace('Ω', '')

    def __str__(self):
        return self.valid_string()

    def set_price(self):
        if self.item["Rarity"] in ("Basic", "Common"):
            return random.randint(45, 55)
        elif self.item["Rarity"] == "Uncommon":
            return random.randint(68, 82)
        elif self.item["Rarity"] == "Rare":
            return random.randint(135, 165)
        else:
            raise ValueError(f"Item {self.item} has no rarity")

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
      items.extend(random.sample(attack_cards, 2))
      items.extend(random.sample(skill_cards, 2))
      items.extend(random.sample(power_cards, 1))
      colorless_cards = [c for c in all_cards if "Class" in c and c["Class"] == "Colorless"]
      colorless_uncommon = [c for c in colorless_cards if c["Rarity"] == Rarity.UNCOMMON]
      colorless_rare = [c for c in colorless_cards if c["Rarity"] == Rarity.RARE]
      items.extend(random.sample(colorless_uncommon, 1))
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

    def __str__(self):
        return f"{self.name} has {self.stock} items in stock"

    def __add__(self, other):
        new_stock = self.stock + other.stock
        return Shop(f"{self.name} & {other.name}", new_stock)

    def __len__(self):
        return self.stock