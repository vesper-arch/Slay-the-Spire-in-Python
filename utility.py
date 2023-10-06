from time import sleep
from os import system
import math
import random
import re
from ansimarkup import ansiprint


active_enemies = []
combat_turn = 1
combat_potion_dropchance = 40
duration_effects = ("Frail", "Poison", "Vulnerable", "Weak", "Draw Reduction", 'Lock On', "No Block", "Intangible", "Blur", "Collect", 'Double Damage',
                   "Equilibrium", "Phantasmal", "Regeneration", "Fading")
non_stacking_effects = ("Confused", "No Draw", "Entangled", "Barricade", "Back Attack", "Life Link", "Minion", "Reactive", "Shifting", "Split",
                        "Stasis", "Unawakened", "Blasphemer", "Corruption", "Electro", "Master Reality", "Pen Nib", "Simmering Rage",
                        "Surrounded")
player_buffs = {"Artifact": "Negate the next X debuffs",
                "Barricade": "<bold>Block</bold> is not removed at the start of your turn",
                "Buffer": "Prevent the next X times you would lose HP",
                "Dexterity": "Increases <bold>Block</bold> gained from cards by X",
                "Draw Card": "Draw X aditional cards next turn",
                "Energized": "Gain X additional <bold>Energy</bold> next turn",
                "Focus": "Increases the effectiveness of <bold>Orbs</bold> by X",
                "Intangible": "Reduce ALL damage and HP loss to 1 for X turns",
                "Mantra": "When you gain 10 Mantra, enter <bold>Divinity</bold>",
                "Metallicize": "At the end of your/its turn, gains X <bold>Block</bold>",
                "Next Turn Block": "Gain X <bold>Block</bold> next turn",
                "Plated Armor": "At the end of your/its turn, gain X <bold>Block</bold>. Recieving unblocked attack damage reduces Plated Armor by 1.",
                "Ritual": "At the end of your/its turn, gains X <bold>Strength</bold>",
                "Strength": "Increases attack damage by X",
                "Thorns": "When attacked, deal X damage back",
                "Vigor": "Your next Attack deals X additional damage",
                "Accuracy": "<bold>Shivs</bold> deal X additonal damage",
                "After Image": "Whenever you play a card, gain X <bold>Block</bold>",
                "Amplify": "Your next X Power cards are played twice",
                "Battle Hymn": "At the start of each turn, add X <bold>Smites</bold> into your hand",
                "Berzerk": "At the start of your turn, gain 1 <bold>Energy</bold>",
                "Blasphemer": "At the start of your turn, die",
                "Blur": "<bold>Block</bold> is not removed at the start of your next X turns.",
                "Brutality": "At the start of your turn, lose X HP and draw X card(s)",
                "Burst": "Your next X Skills are played twice",
                "Collect": "Put a <bold>Miracle+</bold> into your hand at the start of your next X turns",
                "Combust": "At the end of your turn, lose 1 HP for each <bold>Combust</bold> played and deal X damage to ALL enemies",
                "Corruption": "Skills cost 0. Whenever you play a Skill, <bold>Exhaust<bold> it",
                "Creative AI": "At the start of your turn, add X random Power cards into your hand",
                "Dark Embrace": "Whenever a card is <bold>Exhausted</bold>, gain X <bold>Block</bold>",
                "Demon Form": "At the start of your turn, gain X <bold>Strength</bold>",
                "Deva": "At the start of your turn, gain X <bold>Energy</bold> N times and increase X by 1",
                "Devotion": "At the start of your turn, gain X <bold>Mantra</bold>",
                "Double Damage": "Attacks deal double damage for X turns",
                "Double Tap": "Your next X Attacks are played twice",
                "Duplication": "Your next X cards are played twice",
                "Echo Form": "The first X cards you play each turn are played twice",
                "Electro": "<bold>Lightning</bold> hits ALL enemies",
                "Envenom": "Whenever you deal unblocked attack damage, apply X <bold>Poison</bold>",
                "Equilibrium": "<bold>Retain</bold> your hand for X turns",
                "Establishment": "Whenever a card is <bold>Retained</bold>, reduce its cost by X",
                "Evolve": "Whenever you draw a Status card, draw X cards",
                "Feel No Pain": "Whenever a card is <bold>Exhausted</bold>, gain X <bold>Block</bold>",
                "Fire Breathing": "Whenever you draw a Status or Curse card, deal X damage to ALL enemies",
                "Flame Barrier": "When attacked, deals X damage back. Wears off at the start of your next turn",
                "Foresight": "At the start of your turn, <bold>Scry</bold> X",
                "Free Attack Power": "The next X Attacks you play cost 0",
                "Heatsink": "Whenever you play a Power card, draw X cards",
                "Hello": "At the start of your turn, add X random Common cards into your hand",
                "Infinite Blades": "At the start of your turn, add X <bold>Shivs</bold> into your hand",
                "Juggernaut": "Whenever you gain <bold>Block</bold>, deal X damage to a random enemy",
                "Like Water": "At the end of your turn, if you are in <bold>Calm</bold>, gain X <bold>Block</bold>",
                "Loop": "At the start of your turn, trigger the passive ablity of your next orb X times",
                "Machine Learning": "At the start of your turn, draw X additional cards",
                "Magnetism": "At the start of your turn, add X random colorless cards into your hand",
                "Master Reality": "Whenever a card is created during combat, <bold>Upgrade</bold> it",
                "Mayhem": "At the start of your turn, play the top X cards of your draw pile",
                "Mental Fortress": "Whenever you switch <bold>Stances</bold>, gain X <bold>Block</bold>",
                "Nightmare": "Add X of a chosen card into your hand next turn",
                "Nirvana": "Whenever you <bold>Scry</bold>, gain X <bold>Block</bold>",
                "Noxious Fumes": "At the start of your turn, apply X <bold>Poison</bold> to ALL enemies",
                "Omega": "At the end of your turn, deal X damage to ALL enemies",
                "Panache": "Whenever you play 5 cards in a single turn, deal X damage to ALL enemies",
                "Pen Nib": "Your next Attack deals double damage",
                "Phantasmal": "Deal double damage for the next X turns",
                "Rage": "Whenever you play an Attack, gain X <bold>Block</bold>. Wears off next turn",
                "Rebound": "The next X cards you play this turn are placed on top of your draw pile",
                "Regeneration": "At the end of your turn, heal X HP and decrease Regeneration by 1",
                "Rushdown": "Whenever you enter <bold>Wrath</bold>, draw X cards",
                "Repair": "At the end of combat, heal X HP",
                "Rupture": "Whenever you lose HP from a card, gain X <bold>Strength</bold>",
                "Sadistic": "Whenever you apply a debuff to an enemy, deal X damage to that enemy",
                "Simmering Rage": "Enter <bold>Wrath</bold> next turn",
                "Static Discharge": "Whenever you take unblocked attack damage, channel X <bold>Lightning</bold>",
                "Storm": "Whenever you play a Power card, channel X <bold>Lightning</bold>",
                "Study": "At the end of your turn, shuffle X <bold>Insights<bold> into your draw pile",
                "Surrounded": "Recieve 50% more damage when attacked from behind. Use targeting cards or potions to change your orientation",
                "The Bomb": "At the end of 3 turns, deal X damage to ALL enemies",
                "Thousand Cuts": "Whenever you play a card, deal X damage to ALL enemies",
                "Tools of the Trade": "At the start of your turn, draw X cards and discard X cards",
                "Wave of the Hand": "Whenever you gain <bold>Block</bold> this turn, apply X <bold>Weak</bold> to ALL enemies",
                "Well-laid Plans": "At the end of your turn, <bold>Retain</bold> up to X cards.",
}
player_debuffs = {
    "Confused": "The costs of your cards are randomized on draw, from 0 to 3",
    "Dexterity Down": "At the end of your turn, lose X <bold>Dexterity</bold>",
    "Frail": "<bold>Block</bold> gained from cards is reduced by 25%",
    "No Draw": "You may not draw any more cards this turn",
    "Strength Down": "At the end of your turn, lose X <bold>Strength</bold>",
    "Vulnerable": "You/It takes 50% more damage from attacks",
    "Weak": "You/It deals 25% less damage from attacks",
    "Bias": "At the start of your turn, lose X <bold>Focus</bold>",
    "Contricted": "At the end of your turn, take X damage",
    "Draw Reduction": "Draw 1 less card the next X turns",
    "Entangled": "You may not play Attacks this turn",
    "Fasting": "Gain X less Energy at the start of each turn",
    "Hex": "Whenever you play a non-Attack card, shuffle X <bold>Dazed</bold> into your draw pile",
    "No Block": "You may not gain <bold>Block</bold> from cards for the next X turns",
    "Wraith Form": "At the start of your turn, lose X <bold>Dexterity</bold>"
}
enemy_buffs = {"Artifact": "Negate the next X debuffs",
                "Barricade": "<bold>Block</bold> is not removed at the start of your turn",
                "Intangible": "Reduce ALL damage and HP loss to 1 for X turns",
                "Metallicize": "At the end of your/its turn, gains X <bold>Block</bold>",
                "Plated Armor": "At the end of your/its turn, gain X <bold>Block</bold>. Recieving unblocked attack damage reduces Plated Armor by 1.",
                "Ritual": "At the end of your/its turn, gains X <bold>Strength</bold>",
                "Strength": "Increases attack damage by X",
                "Regen": "At the end of its turn, heals X HP",
                "Thorns": "When attacked, deal X damage back",
                "Angry": "Upon recieving attack damage, gains X <bold>Strength</bold>",
                "Back Attack": "Deals 50% increased damage as it is attacking you from behind",
                "Beat of Death": "Whenever you play a card, take X damage",
                "Curiosity": "Whenever you play a Power card, gains X <bold>Strength</bold>",
                "Curl Up": "On recieving attack damage, curls up and gains X <bold>Block</bold>(Once per combat)",
                "Enrage": "Whenever you play a Skill, gains X <bold>Strength</bold>",
                "Explosive": "Explodes in N turns, dealing X damage",
                "Fading": "Dies in X turns",
                "Invincible": "Can only lose X more HP this turn",
                "Life Link": "If other <bold>Darklings</bold> are still alive, revives in 2 turns",
                "Malleable": "On recieving attack damage, gains X <bold>Block</bold>. <bold>Block</bold> increases by 1 every time it's triggered. Resets to X at the start of your turn",
                "Minion": "Minions abandon combat without their leader",
                "Mode Shift": "After recieving X damage, changes to a defensive form",
                "Painful Stabs": "Whenever you recieve unblocked attack damage from this enemy, add X <bold>Wounds</bold> into your discard pile",
                "Reactive": "Upon recieving attack damage, changes its intent",
                "Sharp Hide": "Whenever you play an Attack, take X damage",
                "Shifting": "Upon losing HP, loses that much <bold>Strength</bold> until the end of its turn",
                "Split": "When its HP is at 50% or lower, splits into 2 smaller slimes with its current HP as their Max HP",
                "Spore Cloud": "On death, applies X <bold>Vulnerable</bold>",
                "Stasis": "On death, returns a stolen card to your hand",
                "Strength Up": "At the end of its turn, gains X <bold>Strength</bold>",
                "Thievery": "Steals X <yellow>Gold</yellow> when it attacks",
                "Time Warp": "Whenever you play N cards, ends your turn and gains X <bold>Strength</bold>",
                "Unawakened": "This enemy hasn't awakened yet...",
}
enemy_debuffs = {
                "Poison": "At the beginning of its turn, loses X HP and loses 1 stack of Poison",
                "Shackled": "At the end of its turn, regains X <bold>Strength</bold>",
                "Slow": "The enemy recieves (X * 10)% more damage from attacks this turn. Whenever you play a card, increase Slow by 1",
                "Vulnerable": "You/It takes 50% more damage from attacks",
                "Weak": "You/It deals 25% less damage from attacks",
                "Block Return": "Whenever you attack this enemy, gain X <bold>Block</bold>",
                "Choked": "Whenever you play a card this turn, the targeted enemy loses X HP",
                "Corpse Explosion": "On death, deals X times its Max HP worth of damage to all other enemies",
                "Lock-On": "<bold>Lightning</bold> and <bold>Dark</bold> orbs deal 50% more damage to the targeted enemy",
                "Mark": "Whenever you play <bold>Pressure Points</bold>, all enemies with Mark lose X HP"}
all_effects = []
all_effects.extend(player_buffs)
all_effects.extend(player_debuffs)
all_effects.extend(enemy_buffs)
all_effects.extend(enemy_debuffs)
all_effects = tuple(all_effects)

def generate_card_rewards(reward_tier, amount, card_pool, entity) -> list[dict]:
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

def generate_potion_rewards(amount, potion_pool, entity, chance_based=True) -> list[dict]:
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

def generate_relic_rewards(source, amount, relic_pool, entity, chance_based=True) -> list[dict]:
    common_relics = [relic for relic in relic_pool if relic.get('Rarity') == 'Common' and relic.get('Class') == entity.player_class]
    uncommon_relics = [relic for relic in relic_pool if relic.get('Rarity') == 'Uncommon' and relic.get('Class') == entity.player_class]
    rare_relics = [relic for relic in relic_pool if relic.get('Rarity') == 'Rare' and relic.get('Class') == entity.player_class]
    all_relics = [relic for relic in relic_pool if relic.get('Rarity') in ('Common', 'Uncommon', 'Rare') and relic.get('Class') == entity.player_class]
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

def claim_relics(choice, entity, relic_amount, relic_pool, rewards=None, chance_based=True):
    if not rewards:
        rewards = generate_relic_rewards('Other', relic_amount, relic_pool, entity, chance_based)
    if not choice:
        for i in range(relic_amount):
            entity.relics.append(rewards[i])
            print(f"{entity.name} obtained {rewards[i]['Name']} | {rewards[i]['Info']}")
            rewards.remove(rewards[i])
            sleep(0.6)
        sleep(1)
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
            for _ in range(min(len(skill_cards), 2)):
                entity.card_actions(random.choice(skill_cards), 'Upgrade', skill_cards)

        if rewards[option] == relic_pool.get('Whetstone'):
            attack_cards = [card for card in entity.deck if card.get('Type') == 'Attack']
            for _ in range(min(len(attack_cards), 2)):
                entity.card_actions(random.choice(attack_cards), 'Upgrade', attack_cards)
        rewards.remove(rewards[i])
        sleep(1)
        system('clear')

def claim_potions(choice, potion_amount, potion_pool, entity, rewards=None, chance_based=True):
    if not rewards:
        rewards = generate_potion_rewards(potion_amount, potion_pool, entity, chance_based)
    if not choice:
        for i in range(potion_amount):
            entity.potions.append(rewards[i])
            print(f"{entity.name} obtained {rewards[i]['Name']} | {rewards[i]['Info']}")
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

def card_rewards(tier, choice, entity, card_pool, rewards=None):
    if not rewards:
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
        rewards.clear()
        sleep(1)

def damage(dmg: int, target: object, user: object, ignore_block: bool=False, card: bool=True):
    dmg_affected_by: str = ''
    if card:
        dmg = dmg + user.strength + user.vigor
        if user.buffs["Strength"] != 0:
            dmg_affected_by += f"{'<red>' if user.buffs['Strength'] < 0 else ''}{user.strength}{'</red>' if user.buffs['Strength'] < 0 else ''} <light-cyan>Strength</light-cyan> | "
        if user.buffs["Vigor"] > 0:
            dmg_affected_by += f"{user.vigor} <light-cyan>Vigor</light-cyan> | "
        if user.debuffs["Weak"] > 0 and card:
            dmg = math.floor(dmg * 0.75)
            dmg_affected_by += "<light-cyan>Weak</light-cyan>(x0.75 dmg) | "
        if target.debuffs["Vulnerable"] > 0:
            dmg = math.floor(dmg * 1.50)
            dmg_affected_by += "<light-cyan>Vulnerable</light-cyan>(x1.5 dmg) | "
        if hasattr(user, 'pen_nib_attacks'):
            if user.buffs["Pen Nib"] > 0:
                dmg *= 2
                dmg_affected_by += "<light-cyan>Pen Nib</light-cyan>(x2 dmg) | "
    if not ignore_block:
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
            if user.dmg_reduce_by_1 is True and hasattr(target, 'dmg_reduce_by_1'):
                dmg -= 1
                dmg_affected_by += '<bold>Tungsten Rod</bold> (Reduced unblocked damage by 1)'
            target.health -= dmg
            if hasattr(user, 'taken_damage'):
                if user.taken_damage is False:
                    user.taken_damage = True
    else:
        if user.dmg_reduce_by_1 is True and hasattr(target, 'dmg_reduce_by_1'):
            dmg -= 1
            dmg_affected_by += '<bold>Tungsten Rod</bold> (Reduced unblocked damage by 1)'
        target.health -= dmg
    print('Affected by:')
    print(dmg_affected_by)
    if hasattr(user, 'player_class'):
        if user.health < math.floor(user.health * 0.5):
            ansiprint('From <bold>Red Skull</red>: ', end='')
            user.starting_strength += 3
            user.buff('Strength', 3, False)
    # Removes buffs that trigger on attack.
    if user.buffs['Vigor'] > 0:
        user.buffs['Vigor'] = 0
        ansiprint("\n<light-cyan>Vigor</light-cyan> wears off")
    if hasattr(user, 'pen_nib_attacks'):
        if user.buffs["Pen Nib"] == 10:
            user.buffs["Pen Nib"] = 0
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

def bottle_card(entity, card_type):
    valid_cards = [card for card in entity.deck if card.get('Type') == card_type]
    while True:
        for deck_card in entity.deck:
            if deck_card.get('Type') == card_type:
                ansiprint(f"<blue>{deck_card['Name']}</blue> | <light-black>{deck_card['Type']}</light-black> | <light-red>{deck_card['Energy']} Energy</light-red> | <yellow>{deck_card['Info']}</yellow>")
                sleep(0.05)

        option = list_input('What card do you want to bottle? > ', valid_cards)
        valid_cards[option]['Bottled'] = True
        print(f'{valid_cards[option].get("Name")} has been bottled.')
        sleep(1.5)
        system('clear')
        break

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

def remove_color_tags(string) -> str:
    pattern = r"<(\w+)>" # Pattern that searches for the word between < and > without symbols
    colors = re.findall(pattern, string)
    for color in colors:
        string = string.replace(color, '') # Removes all of the colors found by the findall() function
    string = string.replace('<', '').replace('>', '').replace('/', '') # Removes all color tag symbols
    return string
