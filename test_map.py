import game

def test_create_game_map():
    aMap = game.create_game_map()
    assert aMap is not None
    assert len(aMap) == 15
    assert aMap[0].__name__ == "normal_combat"
    assert aMap[-1].__name__ == "boss_combat"