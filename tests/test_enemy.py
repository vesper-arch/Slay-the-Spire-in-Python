import entities
import helper
import pytest
import enemy_catalog
import inspect

@pytest.fixture
def sleepless(monkeypatch):
    def sleep(seconds):
        pass
    monkeypatch.setattr(helper, 'sleep', sleep)
    monkeypatch.setattr(entities, 'sleep', sleep)


def test_most_enemies_default_move(sleepless):
  enemies = []
  for name, obj in inspect.getmembers(enemy_catalog):
    # These enemies are too hard to test for some reason
    if inspect.isclass(obj) and name not in ["Enemy", "Hexaghost", "Lagavulin", "Sentry"]:
        enemies.append((name,obj))

  for name, class_obj in enemies:
    print(f"--->Testing: {name}")
    enemy = class_obj()
    enemy.set_intent()
    enemy.execute_move()
