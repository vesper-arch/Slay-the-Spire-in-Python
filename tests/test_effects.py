import random

import pytest

import enemy_catalog
import entities
import effect_catalog

from unittest.mock import Mock


@pytest.fixture
def ei():
  ei = effect_catalog.EffectInterface()
  return ei

def test_helper_effect_amount_empty():
  assert effect_catalog.effect_amount(effect_catalog.Strength, []) == 0

def test_helper_effect_amount_single():
  test_effects = [effect_catalog.Vulnerable(host=Mock(), amount=5)]
  assert effect_catalog.effect_amount(effect_catalog.Strength, test_effects) == 0
  assert effect_catalog.effect_amount(effect_catalog.Vulnerable, test_effects) == 5

def test_helper_effect_amount_multiple():
  test_effects = [effect_catalog.Vulnerable(host=Mock(), amount=5),
             effect_catalog.Strength(host=Mock(), amount=3),
             effect_catalog.Strength(host=Mock(), amount=2)]
  assert effect_catalog.effect_amount(effect_catalog.Weak, test_effects) == 0
  assert effect_catalog.effect_amount(effect_catalog.Strength, test_effects) == 5
  assert effect_catalog.effect_amount(effect_catalog.Vulnerable, test_effects) == 5


@pytest.mark.skip("init_effects was removed.")
class TestApplyEffects():
  def test_player_buffs(self, ei):
    buffs = ei.init_effects("player buffs")
    player = player.Player.create_player()
    for buff in buffs:
      ei.apply_effect(player, None, buff, random.randint(1, 5))
    # No easy asserts possible
    for tick in range(random.randint(2, 7)):
      print(f"Tick: {tick+1}")
      ei.tick_effects(player)

  def test_enemy_buffs(self, ei):
    buffs = ei.init_effects("enemy buffs")
    for buff in buffs:
      enemy = enemy_catalog.SneakyGremlin()
      ei.apply_effect(enemy, enemy, buff, 5)
    # No easy asserts possible

  def test_player_debuffs(self, ei):
    debuffs = ei.init_effects("player debuffs")
    test_player = player.Player.create_player()
    for debuff in debuffs:
      ei.apply_effect(test_player, test_player, debuff, 5)
    # No easy asserts possible

  def test_enemy_debuffs(self, ei):
    debuffs = ei.init_effects("enemy debuffs")
    for debuff in debuffs:
      enemy = enemy_catalog.SneakyGremlin()
      ei.apply_effect(enemy, enemy, debuff, 5)
    # No easy asserts possible