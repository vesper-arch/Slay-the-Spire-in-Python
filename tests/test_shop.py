# test the shop
import pytest

import entities
import items
from ansi_tags import ansiprint
from shop import SellableItem, Shop
import player
import card_catalog
import potion_catalog
import relic_catalog



class TestSellableItems():
  def test_cards(self):
    '''See that we can make sellable items out of all cards and that they display correctly'''
    all_sellable_cards = card_catalog.create_all_cards()
    for card in all_sellable_cards:
      sellable = SellableItem(card)
      ansiprint(sellable.valid_string())
      ansiprint(sellable.invalid_string())

  def test_potions(self):
    '''See that we can make sellable items out of all potions and that they display correctly'''
    all_sellable_potions = list(potion_catalog.create_all_potions())
    for potion in all_sellable_potions:
      sellable = SellableItem(potion)
      ansiprint(sellable.valid_string())
      ansiprint(sellable.invalid_string())

  def test_relics(self):
    '''See that we can make sellable items out of all relics and that they display correctly'''
    all_sellable_relics = list(relic_catalog.create_all_relics())
    for relic in all_sellable_relics:
      sellable = SellableItem(relic)
      ansiprint(sellable.valid_string())
      ansiprint(sellable.invalid_string())

def test_shop(monkeypatch):
  test_player = player.Player.create_player()
  all_cards = card_catalog.create_all_cards()
  cards = [SellableItem(x) for x in all_cards if x.name in ("Strike","Body Slam","Heavy Blade","Warcry")]
  shop = Shop(test_player, cards)
  responses = iter(['1', '\n', 'e'])
  with monkeypatch.context() as m:
    m.setattr('builtins.input', lambda *a, **kw: next(responses))

    shop.loop()