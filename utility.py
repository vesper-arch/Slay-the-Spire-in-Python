from time import sleep
from os import system
import math
import random
from ansimarkup import ansiprint


active_enemies = []
combat_turn = 1
combat_potion_dropchance = 40

def generate_card_rewards(reward_tier, amount, card_pool, entity):
    """
    Normal combat rewards:
    Rare: 3% | Uncommon: 37% | Common: 60%
    
    Elite combat rewards:
    Rare: 10% | Uncommon: 40% | Common: 50%
    
    Boss combat rewards:
    Rare: 100% | Uncommon: 0% | Common: 0%
    """
    common_cards = {card: attr for card, attr in card_pool.items() if attr.get("Rarity") == "Common" and attr.get("Type") not in ('Status', 'Curse') and not attr.get('Upgraded') and attr.get('Class') == entity.player_class}
    uncommon_cards = {card: attr for card, attr in card_pool.items() if attr.get("Rarity") == "Uncommon" and attr.get("Type") not in ('Status', 'Curse') and not attr.get('Upgraded') and attr.get('Class') == entity.player_class}
    rare_cards = {card: attr for card, attr in card_pool.items() if attr.get("Rarity") == "Rare" and attr.get("Type") not in ('Status', 'Curse') and not attr.get('Upgraded') and attr.get('Class') == entity.player_class}

    rewards = []

    if reward_tier == "Normal":
        for _ in range(amount):
            random_num = 70 # It's set to 70 because Uncommon and Rare cards don't exist yet
            if random_num > 97:
                random_key = random.choice(list(rare_cards.keys()))
                rewards.append(rare_cards[random_key])
            elif random_num < 60:
                random_key = random.choice(list(common_cards.keys()))
                rewards.append(common_cards[random_key])
            else:
                random_key = random.choice(list(uncommon_cards.keys()))
                rewards.append(uncommon_cards[random_key])
    elif reward_tier == "Elite":
        for _ in range(amount):
            random_num = random.randint(1, 101)
            if random_num <= 10:
                random_key = random.choice(list(rare_cards.keys()))
                random_value = rare_cards[random_key]
                rewards.append(random_key[random_value])
            elif random_num > 50:
                random_key = random.choice(list(common_cards.keys()))
                random_value = common_cards[random_key]
                rewards.append(random_key[random_value])
            else:
                random_key = random.choice(list(uncommon_cards.keys()))
                random_value = uncommon_cards[random_key]
                rewards.append(random_key[random_value])
    elif reward_tier == "Boss":
        for _ in range(amount):
            random_key = random.choice(list(rare_cards.keys()))
            random_value = rare_cards[random_value]
            rewards.append(random_key[random_value])
    return rewards

def generate_potion_rewards(amount, potion_pool, entity):
    """You have a 40% chance to get a potion at the end of combat.
    -10% when you get a potion.
    +10% when you don't get a potion."""
    common_potions = {potion: attr for potion, attr in potion_pool.items() if attr.get("Rarity") == "Common" and (attr.get("Class") == "All" or entity.entity_class in attr.get('Class'))}
    uncommon_potions = {potion: attr for potion, attr in potion_pool.items() if attr.get("Rarity") == "Uncommon" and (attr.get("Class") == "All" or entity.entity_class in attr.get('Class'))}
    rare_potions = {potion: attr for potion, attr in potion_pool.items() if attr.get("Rarity") == "Rare" and (attr.get("Class") == "All" or entity.entity_class in attr.get('Class'))}

    rewards = []
    for _ in range(amount):
        random_num = random.randint(1, 101)
        if random_num > 65:
            random_key = random.choice(list(common_potions.keys()))
            rewards.append(common_potions[random_key])
        elif random_num < 25:
            random_key = random.choice(list(uncommon_potions.keys()))
            rewards.append(uncommon_potions[random_key])
        else:
            random_key = random.choice(list(rare_potions.keys()))
            rewards.append(rare_potions[random_key])
    return rewards

def obtain_potions(choice, potion_amount, potion_pool, entity):
    rewards = generate_potion_rewards(potion_amount, potion_pool, entity)
    if not choice:
        for i in range(potion_amount):
            entity.potions.append(rewards[i])
            print(f"{entity.name} obtained {rewards[i]['Name']}")
            rewards.remove(rewards[i])
        sleep(1.5)
        system("clear")
    while len(rewards) > 0:
        counter = 1
        print("Potion Bag:")
        for potion in entity.potions:
            ansiprint(f"{counter}: <light-black>{potion['Rarity']}</light-black> | <green>{potion['Class']}</green> | <blue>{potion['Name']}</blue> | <yellow>{potion['Info']}")
            counter += 1
        print(f"{len(entity.potions)} / {entity.potion_bag}")
        print()
        print("Potion reward(s):")
        counter = 1
        for potion in rewards:
            ansiprint(f"{counter}: <light-black>{potion['Rarity']}</light-black> | Class: <green>{potion['Class']}</green> | <blue>{potion['Name']}</blue> | <yellow>{potion['Info']}</yellow>")
            counter += 1
        print()
        option= integer_input('What potion you want? >', rewards)
        if len(entity.potions) == entity.potion_bag:
            ansiprint("<red>Potion bag full!")
            sleep(1)
            option = input("Discard a potion?(y|n) > ")
            if option == 'y':
                counter = 1
                for potion in entity.potions:
                    ansiprint(f"{counter}: <light-black>{potion['Rarity']}</light-black> | <green>{potion['Class']}</green> | <blue>{potion['Name']}</blue> | <yellow>{potion['Info']}</yellow>")
                    counter += 1
                try:
                    option = int(input("What potion do you want to discard? > ")) - 1
                except ValueError:
                    print("You have to enter a number")
                    sleep(1.5)
                    system("clear")
                    continue
                print(f"Discarded {entity.potions[option]['Name']}.")
                entity.potions.remove(entity.potions[option])
                sleep(1.5)
                system("clear")
            else:
                sleep(1.5)
                system("clear")
            continue
        else:
            entity.potions.append(rewards[option])
            print(f"{entity.name} obtained {rewards[option]['Name']}")
            rewards.remove(rewards[option])
            sleep(1.5)
            system("clear")

def card_rewards(tier, entity, card_pool):
    rewards = generate_card_rewards(tier, entity.card_reward_choices, card_pool, entity)
    while True:
        counter = 1
        for card in rewards:
            ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            counter += 1
        chosen_reward = integer_input('What card do you want? > ', rewards)
        entity.deck.append(rewards[chosen_reward])
        print(f"{entity.name} obtained {rewards[chosen_reward]['Name']}")
        rewards = []
        sleep(1.5)
        system("clear")
        break

def damage(dmg: int, target: object, user, card=True):
    dmg = dmg + user.strength + user.vigor
    if user.weak > 0 and card:
        dmg = math.floor(dmg * 0.75)
    if target.vulnerable > 0:
        dmg = math.floor(dmg * 1.50)
    # Manages Block
    if dmg < target.block:
        target.block -= dmg
    elif dmg > target.block:
        target.health -= dmg - target.block
        target.block = 0
    elif dmg == target.block:
        target.block -= dmg

    print(f"{user.name} dealt {dmg:.0f} damage to {target.name}")
    # Removes debuffs that trigger on attack.
    if user.vigor > 0:
        user.vigor = 0
        ansiprint("<light-cyan>Vigor</light-cyan> wears off")
    target.health = max(target.health, 0)
    if target.health <= 0:
        target.die()
    sleep(1)



def display_ui(entity, target_list, combat=True):
    # Repeats for every card in the entity's hand
    print("Potions: ")
    counter = 1
    for potion in entity.potions:
        ansiprint(f"{counter}: {potion['Name']} | {potion['Class']} | <light-black>{potion['Rarity']}</light-black> | <yellow>{potion['Info']}</yellow>")
        counter += 1
        sleep(0.05)
    for _ in range(entity.potion_bag - len(entity.potions)):
        ansiprint(f"<light-black>{counter}: (Empty)</light-black>")
        counter += 1
        sleep(0.05)
    print()
    ansiprint("<bold>Hand: </bold>")
    counter = 1
    if entity.strength > 0:
        print()
        ansiprint(f"<green>Strength = {entity.strength}:<green>")
    for card in target_list:
        # Prints in red if the entity doesn't have enough energy to use the card
        if card["Energy"] > entity.energy:
            ansiprint(f"{counter}: <blue>{card['Name']}</blue> | <light-black>{card['Type']}</light-black> | <italic><red>{card['Energy']} Energy</red></italic> | <yellow>{card['Info']}</yellow>")
        # Otherwise, print in full color
        else:
            ansiprint(f"{counter}: <blue>{card['Name']}</blue> | <light-black>{card['Type']}</light-black> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
        # Adds one to the counter to make a numbered list(Ex. 1: Defend// 2: Strike...)
        counter += 1
        sleep(0.05)
    print()
    if combat is True:
        for enemy in active_enemies:
            enemy.show_status()
        # Displays the number of cards in the draw and discard pile
        print(f"Draw pile: {len(entity.draw_pile)}\nDiscard pile: {len(entity.discard_pile)}\n")
        # Displays the entity's current health, block, and energy
        entity.show_status()
    else:
        entity.show_status(False)
    print()
    counter = 1


def start_combat(entity, enemy_list):
    print("Starting combat")
    entity.draw_pile = random.sample(entity.deck, len(entity.deck))
    encounter_enemies = random.choice(enemy_list)
    for enemy in encounter_enemies:
        active_enemies.append(enemy)
        enemy.health = random.randint(enemy.health[0], enemy.health[1])
        enemy.max_health = enemy.health

def integer_input(input_string, array=None):
    try:
        if array:
            option = int(input(input_string)) - 1
            array[option] = array[option] # Checks that the number is in range
        else:
            option = int(input(input_string))
    except ValueError:
        print("You have to enter a number")
        sleep(1.5)
        return None
    except IndexError:
        print("Option not in range")
        sleep(1.5)
        return None
    return option
