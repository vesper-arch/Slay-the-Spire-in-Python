# test the shop
import pytest

import entities
import items
from ansi_tags import ansiprint
from shop import SellableItem, Shop


class TestSellableItems():
  def test_cards(self):
    '''See that we can make sellable items out of all cards and that they display correctly'''
    all_sellable_cards = list(items.cards)
    # all_sellable_cards = [card for card in all_sellable_cards if card["Type"] in ("Attack", "Skill", "Power") and card["Rarity"] not in ("Special")]
    for card in all_sellable_cards:
      sellable = SellableItem(card)
      ansiprint(sellable.valid_string())
      ansiprint(sellable.invalid_string())

  def test_potions(self):
    '''See that we can make sellable items out of all potions and that they display correctly'''
    all_sellable_potions = list(items.potions.values())
    for potion in all_sellable_potions:
      sellable = SellableItem(potion)
      ansiprint(sellable.valid_string())
      ansiprint(sellable.invalid_string())

  def test_relics(self):
    '''See that we can make sellable items out of all relics and that they display correctly'''
    all_sellable_relics = list(items.relics.values())
    for relic in all_sellable_relics:
      sellable = SellableItem(relic)
      ansiprint(sellable.valid_string())
      ansiprint(sellable.invalid_string())


def test_shop(monkeypatch):
  player = entities.create_player()
  cards = [SellableItem(items.cards[x]) for x in ("Strike","Body Slam","Heavy Blade","Warcry")]
  shop = Shop(player, cards)
  responses = iter(['1', '\n', 'e'])
  with monkeypatch.context() as m:
    m.setattr('builtins.input', lambda *a, **kw: next(responses))

    shop.loop()