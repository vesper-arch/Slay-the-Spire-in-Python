import inspect

import pytest

import enemy_catalog
import entities
import displayer
from ansi_tags import ansiprint


@pytest.fixture
def all_enemies():
  enemies = []
  for name, obj in inspect.getmembers(enemy_catalog):
    if inspect.isclass(obj) and name not in ["Enemy", "Hexaghost", "Lagavulin", "Sentry"]:
        enemies.append((name,obj))
  return enemies

def test_colors():
  from ansi_tags import user_tags
  for key, v in user_tags.items():
      ansiprint(f'Color {key:15s}: <{key}>1234567890abcdefghijklmnopqrstuvwxyz</{key}>')


class TestDisplayers():
  # TODO: Find some other thing to test because the display_actual_damage and display_actual_block functions have been removed as of 4/13/24.
  @pytest.mark.skip("These functions have been removed.")
  def test_display_actual_damage(self, all_enemies):
    player = player.Player(health=80, block=3, max_energy=3, deck=[])

    for name, class_obj in all_enemies:
      print(f"---> Testing: {name}")
      enemy = class_obj()
      enemy.set_intent()
      result = displayer.display_actual_damage(enemy.intent, target=player, entity=enemy)
      ansiprint(result[0])
      ansiprint(result[1])
