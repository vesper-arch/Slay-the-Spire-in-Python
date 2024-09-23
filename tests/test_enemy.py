import inspect

import pytest

import effects
import enemy_catalog
import entities
import player


@pytest.fixture
def sleepless(monkeypatch):
    def sleep(seconds):
        pass
    monkeypatch.setattr(effects, 'sleep', sleep)
    monkeypatch.setattr(entities, 'sleep', sleep)


def test_most_enemies_default_move(sleepless):
  test_player = player.Player.create_player()
  enemies = []
  for name, obj in inspect.getmembers(enemy_catalog):
    # These enemies are too hard to test for some reason
    if inspect.isclass(obj) and name not in ["Enemy", "Hexaghost", "Lagavulin", "Sentry", "ShieldGremlin"]:
        enemies.append((name,obj))

  print("\n\nTesting the default move for all enemies")
  for idx, (name, class_obj) in enumerate(enemies):
    print(f"--->Testing: {name} (Enemy #{idx+1} of {len(enemies)})")
    enemy = class_obj()
    enemy.set_intent()
    enemy.execute_move(player=test_player, enemies=None)
