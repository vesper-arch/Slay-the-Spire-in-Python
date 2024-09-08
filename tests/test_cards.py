from copy import deepcopy

import pytest

import items
from ansi_tags import ansiprint


# Dynamically generate a list of all the cards.
# Avoids interference with other tests by not using the global items.cards.
def get_all_cards() -> list[items.Card]:
    return [card() for card in items.Card.__subclasses__()]


local_copy_of_cards = get_all_cards()

@pytest.mark.parametrize("card", local_copy_of_cards, ids=[card.name for card in local_copy_of_cards])
def test_all_cards_can_upgrade(card):
    print(f"Upgrading   {card.name}")
    ansiprint(f"  - IsUpgradeble: {card.is_upgradeadble()}")
    if not card.is_upgradeadble():
        return
    ansiprint(f"  - Before : {card.pretty_print()}")
    ansiprint(f"  - Preview: {card.upgrade_preview}")
    card.upgrade()
    ansiprint(f"  - After  : {card.pretty_print()}")
    assert card.upgraded, "Card should have upgraded property set to True"