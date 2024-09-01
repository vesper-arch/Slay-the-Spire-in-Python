import inspect

import pytest

import enemy_catalog
import entities
import helper
from ansi_tags import ansiprint


@pytest.fixture
def all_enemies():
  enemies = []
  for name, obj in inspect.getmembers(enemy_catalog):
    if inspect.isclass(obj) and name not in ["Enemy", "Hexaghost", "Lagavulin", "Sentry"]:
        enemies.append((name,obj))
  return enemies


class TestDisplayers():
  # TODO: Find some other thing to test because the display_actual_damage and display_actual_block functions have been removed as of 4/13/24.
  @pytest.mark.skip("These functions have been removed.")
  def test_display_actual_damage(self, all_enemies):
    disp = helper.Displayer()
    player = entities.Player(health=80, block=3, max_energy=3, deck=[])

    for name, class_obj in all_enemies:
      print(f"---> Testing: {name}")
      enemy = class_obj()
      enemy.set_intent()
      result = disp.display_actual_damage(enemy.intent, target=player, entity=enemy)
      ansiprint(result[0])
      ansiprint(result[1])
