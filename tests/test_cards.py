from copy import deepcopy

import pytest

import items
from ansi_tags import ansiprint


local_copy_of_cards = items.create_all_cards()

@pytest.mark.parametrize("card", local_copy_of_cards, ids=[card.name for card in local_copy_of_cards])
def test_all_cards_can_upgrade(card):
    print(f"Upgrading   {card.name}")
    ansiprint(f"  - IsUpgradeble: {card.is_upgradeable()}")
    if not card.is_upgradeable():
        return
    ansiprint(f"  - Before : {card.pretty_print()}")
    ansiprint(f"  - Preview: {card.upgrade_preview}")
    card.upgrade()
    ansiprint(f"  - After  : {card.pretty_print()}")
    assert card.upgraded, "Card should have upgraded property set to True"