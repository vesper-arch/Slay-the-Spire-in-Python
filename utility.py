from time import sleep
from os import system
import math
import random
import re
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

def generate_potion_rewards(amount, potion_pool, entity, chance_based=True):
    """You have a 40% chance to get a potion at the end of combat.
    -10% when you get a potion.
    +10% when you don't get a potion."""
    common_potions = [potion for potion in potion_pool if potion.get("Rarity") == "Common" and (potion.get("Class") == "All" or entity.entity_class in potion.get('Class'))]
    uncommon_potions = [potion for potion in potion_pool if potion.get("Rarity") == "Uncommon" and (potion.get("Class") == "All" or entity.entity_class in potion.get('Class'))]
    rare_potions = [potion for potion in potion_pool if potion.get("Rarity") == "Rare" and (potion.get("Class") == "All" or entity.entity_class in potion.get('Class'))]
    all_potions = []
    all_potions.extend(common_potions)
    all_potions.extend(uncommon_potions)
    all_potions.extend(rare_potions)
    rewards = []
    for _ in range(amount):
        if chance_based:
            random_num = random.randint(1, 101)
            if random_num > 65:
                rewards.append(random.choice(common_potions))
            elif random_num < 25:
                rewards.append(random.choice(uncommon_potions))
            else:
                rewards.append(random.choice(rare_potions))
        else:
            rewards.append(random.choice(all_potions))
    return rewards

def generate_relic_rewards(source, amount, relic_pool, entity, chance_based=True):
    common_relics = [relic for relic in relic_pool if relic.get('Rarity') == 'Common' and relic.get('Class') == entity.player_class]
    uncommon_relics = [relic for relic in relic_pool if relic.get('Rarity') == 'Uncommon' and relic.get('Class') == entity.player_class]
    rare_relics = [relic for relic in relic_pool if relic.get('Rarity') == 'Rare' and relic.get('Class') == entity.player_class]
    all_relics = []
    all_relics.extend(common_relics)
    all_relics.extend(uncommon_relics)
    all_relics.extend(rare_relics)
    rewards = []
    if source == 'Chest':
        common_chance = 49
        uncommon_chance = 42
    else:
        common_chance = 50
        uncommon_chance = 33
    if chance_based:
        for _ in range(amount):
            random_number = random.randint(1, 100)
            if random_number in range(0, common_chance + 1):
                rewards.append(random.choice(common_relics))
            elif random_number in range(common_chance, uncommon_chance + common_chance + 1):
                rewards.append(random.choice(uncommon_relics))
            elif random_number in range(common_chance + uncommon_chance, 101):
                rewards.append(random.choice(rare_relics))
    else:
        for _ in range(amount):
            rewards.append(random.choice(all_relics))
    return rewards

def claim_relics(choice, entity, relic_amount, relic_pool, chance_based):
    rewards = generate_relic_rewards('Other', relic_amount, relic_pool, entity, chance_based)
    if not choice:
        for i in range(relic_amount):
            entity.relics.append(rewards[i])
            print(f"{entity.name} obtained {rewards[i]['Name']}")
            rewards.remove(rewards[i])
        sleep(1.5)
        system('clear')
    while len(rewards) > 0:
        counter = 1
        for relic in rewards:
            ansiprint(f"{counter}: {relic['Name']} | {relic['Class']} | <light-black>{relic['Rarity']}</light-black> | <yellow>{relic['Info']}</yellow> | <blue><italic>{relic['Flavor']}</italic></blue>")
            counter += 1
            sleep(0.05)
        option = list_input('What relic do you want? > ', rewards)
        if not option:
            sleep(1.5)
            system('clear')
        entity.relics.append(rewards[option])
        print(f"{entity.name} obtained {rewards[option]['Name']}.")
        if rewards[option] == relic_pool.get('Ceramic Fish'):
            entity.gold_on_card_add = True
        if rewards[option] == relic_pool.get('Potion Belt'):
            entity.max_potions += 2
        if rewards[option] == relic_pool.get('Vajra'):
            entity.starting_strength += 1

        if rewards[option] == relic_pool.get('War Paint'):
            skill_cards = [card for card in entity.deck if card.get('Type') == 'Skill']
            for _ in range(2):
                entity.card_actions(random.choice(skill_cards), 'Upgrade', skill_cards)

        if rewards[option] == relic_pool.get('Whetstone'):
            attack_cards = [card for card in entity.deck if card.get('Type') == 'Attack']
            for _ in range(2):
                entity.card_actions(random.choice(attack_cards), 'Upgrade', attack_cards)
        rewards.remove(rewards[i])
        sleep(1)
        system('clear')

def claim_potions(choice, potion_amount, potion_pool, entity, chance_based=True):
    rewards = generate_potion_rewards(potion_amount, potion_pool, entity, chance_based)
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
        print(f"{len(entity.potions)} / {entity.max_potions}")
        print()
        print("Potion reward(s):")
        counter = 1
        for potion in rewards:
            ansiprint(f"{counter}: <light-black>{potion['Rarity']}</light-black> | Class: <green>{potion['Class']}</green> | <blue>{potion['Name']}</blue> | <yellow>{potion['Info']}</yellow>")
            counter += 1
        print()
        option = list_input('What potion you want? >', rewards)
        if len(entity.potions) == entity.max_potions:
            ansiprint("<red>Potion bag full!")
            sleep(1)
            option = input("Discard a potion?(y|n) > ")
            if option == 'y':
                counter = 1
                for potion in entity.potions:
                    ansiprint(f"{counter}: <light-black>{potion['Rarity']}</light-black> | <green>{potion['Class']}</green> | <blue>{potion['Name']}</blue> | <yellow>{potion['Info']}</yellow>")
                    counter += 1
                option = list_input('What potion do you want to discard? > ', entity.potions)
                print(f"Discarded {entity.potions[option]['Name']}.")
                entity.potions.remove(entity.potions[option])
                sleep(1.5)
                system("clear")
            else:
                sleep(1.5)
                system("clear")
            continue
        entity.potions.append(rewards[option])
        print(f"{entity.name} obtained {rewards[option]['Name']}")
        rewards.remove(rewards[option])
        sleep(1.5)
        system("clear")

def card_rewards(tier, choice, entity, card_pool):
    rewards = generate_card_rewards(tier, entity.card_reward_choices, card_pool, entity)
    while True:
        counter = 1
        for card in rewards:
            ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            counter += 1
        if choice:
            chosen_reward = list_input('What card do you want? > ', rewards)
            entity.deck.append(rewards[chosen_reward])
            print(f"{entity.name} obtained {rewards[chosen_reward]['Name']}")
        else:
            for card in rewards:
                if card.get('Type') == 'Curse' and entity.block_curses > 0:
                    ansiprint(f"{card['Name']} was negated by <bold>Omamori</bold>.")
                    entity.block_curses -= 1
                    if entity.block_curses == 0:
                        ansiprint('<bold>Omamori</bold> is depleted.')
                entity.deck.append(rewards[chosen_reward])
                print(f"{entity.name} obtained {rewards[chosen_reward]['Name']}")
        if entity.gold_on_card_add:
            entity.gold += 9
            ansiprint('You gained 9 <yellow>Gold</yellow> from <bold>Ceramic Fish</bold>.')
        rewards = []
        sleep(1.5)
        system("clear")
        break

def damage(dmg: int, target: object, user, ignore_block=False, card=True):
    dmg_affected_by = ''
    if card:
        dmg = dmg + user.strength + user.vigor
        if user.strength != 0:
            dmg_affected_by += f"{user.strength} <light-cyan>Strength</light-cyan> | "
        if user.vigor > 0:
            dmg_affected_by += f"{user.vigor} <light-cyan>Vigor</light-cyan> | "
        if user.weak > 0 and card:
            dmg = math.floor(dmg * 0.75)
            dmg_affected_by += "<light-cyan>Weak</light-cyan>(x0.75 dmg) | "
        if target.vulnerable > 0:
            dmg = math.floor(dmg * 1.50)
            dmg_affected_by += "<light-cyan>Vulnerable</light-cyan>(x1.5 dmg) | "
        if hasattr(user, 'pen_nib_attacks'):
            if user.pen_nib_attacks == 10:
                dmg *= 2
                dmg_affected_by += "<light-cyan>Pen Nib</light-cyan>(x2 dmg) | "
    if target.block < dmg:
        print(f"{user.name} dealt {dmg:.0f}({max(dmg, target.block)} blocked) damage to {target.name}")
    else:
        ansiprint('<blue>Blocked</blue>')
    # Manages Block
    if not ignore_block:
        if dmg <= target.block:
            target.block -= dmg
            dmg = 0
        elif dmg > target.block:
            dmg -= target.block
            target.block = 0
            if dmg in (4, 3, 2, 1) and card:
                dmg = 5
                dmg_affected_by += '<bold>The Boot</bold> (Unblocked damage increased to 5) | '
            target.health -= dmg
            if hasattr(user, 'taken_damage'):
                if user.taken_damage is False:
                    user.taken_damage = True
    else:
        target.health -= dmg
    print('Affected by:')
    print(dmg_affected_by)
    if hasattr(user, 'player_class'):
        if user.health < math.floor(user.health * 0.5):
            ansiprint('From <bold>Red Skull</red>: ', end='')
            user.starting_strength += 3
            user.buff('Strength', 3, False)
    # Removes buffs that trigger on attack.
    if user.vigor > 0:
        user.vigor = 0
        ansiprint("\n<light-cyan>Vigor</light-cyan> wears off")
    if hasattr(user, 'pen_nib_attacks'):
        if user.pen_nib_attacks == 10:
            user.pen_nib_attacks = 0
            ansiprint('<light-cyan>Pen Nib</light-cyan> wears off.')
    # Makes health not able to be negative
    target.health = max(target.health, 0)
    if target.health <= 0:
        target.die()



def display_ui(entity, combat=True):
    # Repeats for every card in the entity's hand
    print("Potions: ")
    counter = 1
    for potion in entity.potions:
        ansiprint(f"{counter}: {potion['Name']} | {potion['Class']} | <light-black>{potion['Rarity']}</light-black> | <yellow>{potion['Info']}</yellow>")
        counter += 1
        sleep(0.05)
    # Fills the empty potion slots with '(Empty)'
    for _ in range(entity.max_potions - len(entity.potions)):
        ansiprint(f"<light-black>{counter}: (Empty)</light-black>")
        counter += 1
        sleep(0.05)
    print()
    ansiprint("<bold>Hand: </bold>")
    counter = 1
    for card in entity.hand:
        # Prints in the energy cost in red if the player doesn't have enough energy to use the card
        if card["Energy"] > entity.energy:
            ansiprint(f"<blue>{card['Name']}</blue> | <light-black>{card['Type']}</light-black> | <italic><red>{card['Energy']} Energy</red></italic> | <yellow>{card['Info']}</yellow>")
        # Otherwise, print in full color
        else:
            ansiprint(f"<blue>{card['Name']}</blue> | <light-black>{card['Type']}</light-black> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
        sleep(0.05)
    print()
    if combat is True:
        for enemy in active_enemies:
            enemy.show_status()
        # Displays the number of cards in the draw and discard pile
        print(f"Draw pile: {len(entity.draw_pile)}\nDiscard pile: {len(entity.discard_pile)}\n")
        # Displays the entity's current health, block, energy, debuffs and buffs.
        entity.show_status()
    else:
        entity.show_status(False)
    print()
    counter = 1


def start_combat(entity, enemy_list):
    print("Starting combat")
    # Shuffles the player's deck into their draw pile
    entity.draw_pile = random.sample(entity.deck, len(entity.deck))
    encounter_enemies = random.choice(enemy_list)
    for enemy in encounter_enemies:
        active_enemies.append(enemy)
        # Enemies have 2 health values, [min, max]. This chooses a random number between those min and max values.
        enemy.health = random.randint(enemy.health[0], enemy.health[1])
        enemy.max_health = enemy.health
    entity.start_of_combat_relics()

def list_input(input_string, array) -> None:
    try:
        if array:
            option = int(input(input_string)) - 1
            array[option] = array[option] # Checks that the number is in range but doesn't really do anything
    except ValueError:
        print("You have to enter a number")
        return None
    except IndexError:
        print("Option not in range")
        return None
    return option

def remove_color_tags(string):
    pattern = r"<(\w+)>" # Pattern that searches for the word between < and > without symbols
    colors = re.findall(pattern, string)
    for color in colors:
        string = string.replace(color, '') # Removes all of the colors found by the findall() function
    string = string.replace('<', '').replace('>', '').replace('/', '') # Removes all color tag symbols
    return string
