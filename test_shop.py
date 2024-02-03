# test the shop
import pytest

import entities
import items
from shop import SellableItem, Shop


def test_shop(monkeypatch):
  player = entities.create_player()
  cards = [SellableItem(items.cards[x]) for x in ("Strike","Body Slam","Heavy Blade","Warcry")]
  shop = Shop(player, cards)
  responses = iter(['1', '\n', 'e'])
  with monkeypatch.context() as m:
    m.setattr('builtins.input', lambda *a, **kw: next(responses))

    shop.loop()