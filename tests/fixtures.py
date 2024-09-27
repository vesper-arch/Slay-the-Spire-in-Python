import pytest



@pytest.fixture
def sleepless(monkeypatch):
    '''A fixture that patches all sleep functions so the test runs super fast'''
    def sleep(seconds):
        pass
    import displayer
    import game
    import events
    import generators
    import player
    import shop
    import enemy
    monkeypatch.setattr(game, 'sleep', sleep)
    monkeypatch.setattr(displayer, 'sleep', sleep)
    monkeypatch.setattr(events, 'sleep', sleep)
    monkeypatch.setattr(generators, 'sleep', sleep)
    monkeypatch.setattr(player, 'sleep', sleep)
    monkeypatch.setattr(shop, 'sleep', sleep)
    monkeypatch.setattr(enemy, 'sleep', sleep)
