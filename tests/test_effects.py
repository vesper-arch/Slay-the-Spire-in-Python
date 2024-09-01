import entities
import helper
import pytest
import enemy_catalog
import random

@pytest.fixture
def ei():
  ei = helper.EffectInterface()
  return ei

class TestEffectInterface():
  def test_init_effects_player_debuffs(self, ei):
    output = ei.init_effects("player debuffs")
    assert "Vulnerable" in output

  def test_init_effects_player_buffs(self, ei):
    output = ei.init_effects("player buffs")
    assert "Amplify" in output

  def test_init_effects_enemy_debuffs(self, ei):
    output = ei.init_effects("enemy debuffs")
    assert "Choked" in output

  def test_init_effects_enemy_buffs(self, ei):
    output = ei.init_effects("enemy buffs")
    assert "Sharp Hide" in output

class TestApplyEffects():
  def test_player_buffs(self, ei):
    buffs = ei.init_effects("player buffs")
    player = entities.create_player()
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
    test_player = entities.create_player()
    for debuff in debuffs:
      ei.apply_effect(test_player, test_player, debuff, 5)
    # No easy asserts possible

  def test_enemy_debuffs(self, ei):
    debuffs = ei.init_effects("enemy debuffs")
    for debuff in debuffs:
      enemy = enemy_catalog.SneakyGremlin()
      ei.apply_effect(enemy, enemy, debuff, 5)
    # No easy asserts possible