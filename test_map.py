import game_map
import pytest
import random

def patched_input(*args, **kwargs):
    return random.randint(1, 4)

def test_create_game_map(monkeypatch):
    # Patch some side effects
    with monkeypatch.context() as m:
        m.setattr('builtins.input', patched_input)

        gm = game_map.create_first_map()   # should not raise an exception
        # Make sure we can itertate over the map
        gm.pretty_print()
        for encounter in gm:
            gm.pretty_print()
            assert isinstance(encounter, game_map.Encounter)

