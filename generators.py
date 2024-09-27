from __future__ import annotations

import random
from time import sleep
from typing import TYPE_CHECKING

import displayer as view
from ansi_tags import ansiprint
from definitions import (
    CardType,
    CombatTier,
    PlayerClass,
    Rarity,
)
from message_bus_tools import Message, bus

# Generators module
# Generates relic_pool, potions, and cards

def generate_card_rewards(reward_tier: CombatTier, amount: int, entity: object, card_pool: dict) -> list[dict]:
    """
    Normal combat rewards:
    Rare: 3% | Uncommon: 37% | Common: 60%

    Elite combat rewards:
    Rare: 10% | Uncommon: 40% | Common: 50%

    Boss combat rewards:
    Rare: 100% | Uncommon: 0% | Common: 0%
    """
    common_cards = [card for card in card_pool if card.rarity == Rarity.COMMON and card.type not in (CardType.STATUS, CardType.CURSE) and card.player_class == entity.player_class]
    uncommon_cards = [card for card in card_pool if card.rarity == Rarity.UNCOMMON and card.type not in (CardType.STATUS, CardType.CURSE) and card.player_class == entity.player_class]
    rare_cards = [card for card in card_pool if card.rarity == Rarity.RARE and card.type not in (CardType.STATUS, CardType.CURSE) and card.player_class == entity.player_class]
    assert len(common_cards) > 0, "Common pool is empty."
    assert len(uncommon_cards) > 0, "Uncommon pool is empty."
    assert len(rare_cards) > 0, "Rare pool is empty."

    rarities = [common_cards, uncommon_cards, rare_cards]
    rewards = []
    if reward_tier == CombatTier.NORMAL:
        chances = [0.60, 0.37, 0.03]
    elif reward_tier == CombatTier.ELITE:
        chances = [0.5, 0.4, 0.1]
    elif reward_tier == CombatTier.BOSS:
        chances = [0, 0, 1]
    for _ in range(amount):
        chosen_pool = random.choices(rarities, chances, k=1)[0]
        rewards.append(random.choice(chosen_pool))
    return rewards

def generate_potion_rewards(amount: int, entity: object, potion_pool: dict, chance_based=True) -> list[dict]:
    """You have a 40% chance to get a potion at the end of combat.
    -10% when you get a potion.
    +10% when you don't get a potion."""
    common_potions: list[dict] = [potion for potion in potion_pool if potion.rarity == Rarity.COMMON and (potion.player_class == PlayerClass.ANY or potion.player_class == entity.player_class)]
    uncommon_potions: list[dict] = [potion for potion in potion_pool if potion.rarity == Rarity.UNCOMMON and (potion.player_class == PlayerClass.ANY or potion.player_class == entity.player_class)]
    rare_potions: list[dict] = [potion for potion in potion_pool if potion.rarity == Rarity.RARE and (potion.player_class == PlayerClass.ANY or potion.player_class == entity.player_class)]
    assert len(common_potions) > 0, "Common potions pool is empty."
    assert len(uncommon_potions) > 0, "Uncommon potions pool is empty."
    assert len(rare_potions) > 0, "Rare potions pool is empty."

    all_potions = common_potions + uncommon_potions + rare_potions
    rarities = [common_potions, uncommon_potions, rare_potions]
    rewards = []
    for _ in range(amount):
        if chance_based:
            rewards.append(random.choice(random.choices(rarities, [0.65, 0.25, 0.1], k=1)[0]))
        else:
            rewards.append(random.choice(all_potions))
    return rewards

def generate_relic_rewards(source: str, amount: int, entity, relic_pool: dict, chance_based=True) -> list[dict]:
    claimed_relics = [relic.name for relic in entity.relics]

    common_relics = [relic for relic in relic_pool if relic.rarity == Rarity.COMMON and relic.player_class == entity.player_class and relic not in entity.relics and relic.name not in claimed_relics]
    uncommon_relics = [relic for relic in relic_pool if relic.rarity == Rarity.UNCOMMON and relic.player_class == entity.player_class and relic not in entity.relics and relic.name not in claimed_relics]
    rare_relics = [relic for relic in relic_pool if relic.rarity == Rarity.RARE and relic.player_class == entity.player_class and relic not in entity.relics and relic.name not in claimed_relics]

    all_relic_pool = common_relics + uncommon_relics + rare_relics
    rarities = [common_relics, uncommon_relics, rare_relics]

    assert len(common_relics) > 0, "Common relics pool is empty."
    assert len(uncommon_relics) > 0, "Uncommon relics pool is empty."
    assert len(rare_relics) > 0, "Rare relics pool is empty."

    rewards = []
    if source == "Chest":
        percent_common = 0.49
        percent_uncommon = 0.42
        percent_rare = 0.09
    else:
        percent_common = 0.50
        percent_uncommon = 0.33
        percent_rare = 0.17
    for _ in range(amount):
        if chance_based:
            rewards.append(random.choice(random.choices(rarities, [percent_common, percent_uncommon, percent_rare], k=1)[0]))
        else:
            rewards.append(random.choice(all_relic_pool))
    return rewards

def claim_relics(choice: bool, entity: object, relic_amount: int, relic_pool: dict = None, rewards: list = None, chance_based=True):
    relic_pool = relic_pool if relic_pool else relic_pool
    if not rewards:
        rewards = generate_relic_rewards("Other", relic_amount, entity, relic_pool, chance_based)
    if not choice:
        for i in range(relic_amount):
            entity.relics.append(rewards[i])
            entity.on_relic_pickup(rewards[i])
            ansiprint(f"{entity.name} obtained {rewards[i].name}.")
            rewards.remove(rewards[i])
            sleep(0.5)
        sleep(0.5)
    while len(rewards) > 0 and choice:
        option = view.list_input("Choose a relic", rewards, view.view_relics)
        if not option:
            sleep(1.5)
            view.clear()
            continue
        entity.relics.append(rewards[option])
        bus.publish(Message.ON_RELIC_ADD, (rewards[option], entity))
        print(f"{entity.name} obtained {rewards[option].name}.")
        rewards.remove(rewards[i])

def claim_potions(choice: bool, potion_amount: int, entity, potion_pool: dict, rewards=None, chance_based=True):
    for relic in entity.relics:
        if relic.name == "Sozu":
            return
    if not rewards:
        rewards = generate_potion_rewards(potion_amount, entity, potion_pool, chance_based)
    if not choice:
        for i in range(potion_amount):
            if len(entity.potions) <= entity.max_potions:
                entity.potions.append(rewards[i])
                print(f"{entity.name} obtained {rewards[i].name} | {rewards[i].info}")
                rewards.remove(rewards[i])
        sleep(1)
        view.clear()
    while len(rewards) > 0:
        print(f"Potion Bag: ({len(potion_pool)} / {entity.max_potions})")
        view.view_potions(entity.potions)
        print()
        print("Potion reward(s):")
        option = view.list_input("Choose a potion", rewards, lambda potion_pool, validator: view.view_potions(potion_pool, True, validator=validator))
        if len(potion_pool) == entity.max_potions:
            ansiprint("<red>Potion bag full!</red>")
            sleep(0.5)
            option = input("Discard a potion?(y|n) > ")
            if option == "y":
                option = view.list_input("Choose a potion to discard", entity.potions, view.view_potions,)
                print(f"Discarded {entity.potions[option]['Name']}.")
                del entity.potions[option]
                sleep(1)
                view.clear()
            else:
                sleep(1)
                view.clear()
            continue
        entity.potions.append(rewards.pop(option))
        sleep(0.2)
        view.clear()

def card_rewards(tier: str, choice: bool, entity, card_pool: dict, rewards=None):
    if not rewards:
        rewards = generate_card_rewards(tier, entity.card_reward_choices, entity, card_pool)
    while True:
        if choice:
            chosen_reward = view.list_input("Choose a card", rewards, view.view_piles)
            if (
                entity.upgrade_attacks and rewards[chosen_reward].type == CardType.ATTACK
                or (entity.upgrade_skills and rewards[chosen_reward].type == CardType.SKILL
                or entity.upgrade_powers and rewards[chosen_reward].type == CardType.POWER
            )):
                rewards[chosen_reward].upgrade()
            entity.deck.append(rewards[chosen_reward])
            ansiprint(f"{entity.name} obtained <bold>{rewards[chosen_reward].name}</bold>")
            rewards.clear()
            break
        for card in rewards:
            bus.publish(Message.ON_CARD_ADD, (entity, card))
            entity.deck.append(card)
            print(f"{entity.name} obtained {card.name}")
            rewards.remove(card)
        break
    rewards.clear()
    sleep(1)
