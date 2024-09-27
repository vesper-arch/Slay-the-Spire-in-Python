import inspect
from typing import Type

import pytest

import enemy_catalog
import player
from enemy_catalog import Enemy
from tests.fixtures import sleepless


def get_all_enemies() -> list[tuple[str, Type[Enemy]]]:
  enemies = []
  for name, cls in inspect.getmembers(enemy_catalog):
    # These enemies are too hard to test
    if inspect.isclass(cls) and name not in [
       "Enemy", # base class
       "Hexaghost", # requires a reference to the player to calculate damage
       "ShieldGremlin" # requires a reference to other enemies in the battle
       ]:
        enemies.append((name,cls))
  return enemies

@pytest.mark.parametrize("name_and_class", get_all_enemies(), ids=[name for name,cls in get_all_enemies()])
def test_most_enemies_default_move(sleepless, name_and_class):
  test_player = player.Player.create_player()
  name, cls = name_and_class
  print(f"--->Testing the default move for {name}")
  enemy = cls()
  enemy.set_intent()
  enemy.execute_move(player=test_player, enemies=[enemy])
