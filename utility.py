from time import sleep
from os import system
from copy import deepcopy
import math
import random
import re
from ansi_tags import ansiprint


active_enemies = []
combat_turn = 1
combat_potion_dropchance = 40
DURATION_EFFECTS = ("Frail", "Poison", "Vulnerable", "Weak", "Draw Reduction", 'Lock On', "No Block", "Intangible", "Blur", "Collect", 'Double Damage',
                   "Equilibrium", "Phantasmal", "Regeneration", "Fading")
NON_STACKING_EFFECTS = ("Confused", "No Draw", "Entangled", "Barricade", "Back Attack", "Life Link", "Minion", "Reactive", "Shifting", "Split",
                        "Stasis", "Unawakened", "Blasphemer", "Corruption", "Electro", "Master Reality", "Pen Nib", "Simmering Rage",
                        "Surrounded")
PLAYER_BUFFS = {"Artifact": "Negate the next X debuffs",
                "Barricade": "<bold>Block</bold> is not removed at the start of your turn",
                "Buffer": "Prevent the next X times you would lose HP",
                "Dexterity": "Increases <bold>Block</bold> gained from cards by X",
                "Draw Card": "Draw X aditional cards next turn",
                "Draw Up": "Draw X additional cards each turn",
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
PLAYER_DEBUFFS = {
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
ENEMY_BUFFS = {"Artifact": "Negate the next X debuffs",
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
ENEMY_DEBUFFS = {
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
all_effects.extend(PLAYER_BUFFS)
all_effects.extend(PLAYER_DEBUFFS)
all_effects.extend(ENEMY_BUFFS)
all_effects.extend(ENEMY_DEBUFFS)
all_effects = tuple(all_effects)

def generate_card_rewards(reward_tier: str, amount: int, entity: object, card_pool: dict) -> list[dict]:
    """
    Normal combat rewards:
    Rare: 3% | Uncommon: 37% | Common: 60%
    
    Elite combat rewards:
    Rare: 10% | Uncommon: 40% | Common: 50%
    
    Boss combat rewards:
    Rare: 100% | Uncommon: 0% | Common: 0%
    """
    common_cards = [card for card in card_pool.values() if card.get("Rarity") == "Common" and card.get("Type") not in ('Status', 'Curse') and not card.get('Upgraded') and card.get('Class') == entity.player_class]
    uncommon_cards = [card for card in card_pool.values() if card.get("Rarity") == "Uncommon" and card.get("Type") not in ('Status', 'Curse') and not card.get('Upgraded') and card.get('Class') == entity.player_class]
    rare_cards = [card for card in card_pool.values() if card.get("Rarity") == "Rare" and card.get("Type") not in ('Status', 'Curse') and not card.get('Upgraded') and card.get('Class') == entity.player_class]

    rewards = []

    if reward_tier == "Normal":
        for _ in range(amount):
            random_num = 70 # It's set to 70 because Uncommon and Rare cards don't exist yet
            if random_num > 97:
                rewards.append(deepcopy(random.choice(rare_cards)))
            elif 60 < random_num < 97:
                rewards.append(deepcopy(random.choice(uncommon_cards)))
            else:
                rewards.append(deepcopy(random.choice(common_cards)))
    elif reward_tier == "Elite":
        for _ in range(amount):
            random_num = random.randint(1, 100)
            if random_num >= 90:
                rewards.append(deepcopy(random.choice(rare_cards)))
            elif 90 > random_num > 50:
                rewards.append(deepcopy(random.choice(uncommon_cards)))
            else:
                rewards.append(deepcopy(random.choice(common_cards)))
    elif reward_tier == "Boss":
        for _ in range(amount):
            rewards.append(deepcopy(random.choice(rare_cards)))
    return rewards


def generate_potion_rewards(amount: int, entity: object, potion_pool: dict, chance_based=True) -> list[dict]:
    """You have a 40% chance to get a potion at the end of combat.
    -10% when you get a potion.
    +10% when you don't get a potion."""
    common_potions = [potion for potion in potion_pool.values() if potion.get("Rarity") == "Common" and (potion.get("Class") == "All" or entity.player_class in potion.get('Class'))]
    uncommon_potions = [potion for potion in potion_pool.values() if potion.get("Rarity") == "Uncommon" and (potion.get("Class") == "All" or entity.player_class in potion.get('Class'))]
    rare_potions = [potion for potion in potion_pool.values() if potion.get("Rarity") == "Rare" and (potion.get("Class") == "All" or entity.player_class in potion.get('Class'))]
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


def generate_relic_rewards(source: str, amount: int, entity, relic_pool: dict, chance_based=True) -> list[dict]:
    common_relics = [relic for relic in relic_pool.values() if relic.get('Rarity') == 'Common' and relic.get('Class') == entity.player_class]
    uncommon_relics = [relic for relic in relic_pool.values() if relic.get('Rarity') == 'Uncommon' and relic.get('Class') == entity.player_class]
    rare_relics = [relic for relic in relic_pool.values() if relic.get('Rarity') == 'Rare' and relic.get('Class') == entity.player_class]
    all_relics = [relic for relic in relic_pool.values() if relic.get('Rarity') in ('Common', 'Uncommon', 'Rare') and relic.get('Class') == entity.player_class]
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

def claim_relics(choice: bool, entity: object, relic_amount: int, relic_pool: dict, rewards: list=None, chance_based=True):
    if not rewards:
        rewards = generate_relic_rewards('Other', relic_amount, entity, relic_pool, chance_based)
    if not choice:
        for i in range(relic_amount):
            entity.relics.append(rewards[i])
            entity.on_relic_pickup(rewards[i])
            ansiprint(f"{entity.name} obtained {rewards[i]['Name']} | {rewards[i]['Info']}")
            rewards.remove(rewards[i])
            sleep(0.5)
        sleep(0.5)
    while len(rewards) > 0 and choice:
        counter = 1
        for relic in rewards:
            ansiprint(f"{counter}: {relic['Name']} | {relic['Class']} | <light-black>{relic['Rarity']}</light-black> | <yellow>{relic['Info']}</yellow> | <blue><italic>{relic['Flavor']}</italic></blue>")
            counter += 1
            sleep(0.05)
        option = list_input('What relic do you want? > ', rewards)
        if not option:
            sleep(1.5)
            clear()
            continue
        entity.relics.append(rewards[option])
        entity.on_relic_pickup(rewards[option])
        print(f"{entity.name} obtained {rewards[option]['Name']}.")
        rewards.remove(rewards[i])

def claim_potions(choice: bool, potion_amount: int, potion_pool: dict, entity, rewards=None, chance_based=True):
    if not rewards:
        rewards = generate_potion_rewards(potion_amount, entity, potion_pool, chance_based)
    if not choice:
        for i in range(potion_amount):
            entity.potions.append(rewards[i])
            print(f"{entity.name} obtained {rewards[i]['Name']} | {rewards[i]['Info']}")
            rewards.remove(rewards[i])
        sleep(1.5)
        clear()
    while len(rewards) > 0:
        counter = 1
        print(f"Potion Bag: ({len(entity.potions)} / {entity.max_potions})")
        for potion in entity.potions:
            ansiprint(f"{counter}: <blue>{potion['Name']}</blue> | <light-black>{potion['Rarity']}</light-black> | <green>{potion['Class']}</green> | <yellow>{potion['Info']}</yellow>")
            counter += 1
        print()
        print("Potion reward(s):")
        counter = 1
        for potion in rewards:
            ansiprint(f"{counter}: <blue>{potion['Name']}</blue> | <light-black>{potion['Rarity']}</light-black> | <green>{potion['Class']}</green> | <yellow>{potion['Info']}</yellow>")
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
                clear()
            else:
                sleep(1.5)
                clear()
            continue
        entity.potions.append(rewards[option])
        rewards.remove(rewards[option])
        sleep(0.2)
        clear()

def card_rewards(tier: str, choice: bool, entity, card_pool: dict, rewards=None):
    if not rewards:
        rewards = generate_card_rewards(tier, entity.card_reward_choices, entity, card_pool)
    while True:
        if choice:
            view_piles(rewards, entity)
            chosen_reward = list_input('What card do you want? > ', rewards)
            if entity.upgrade_attacks and rewards[chosen_reward]['Type'] == 'Attack':
                entity.card_actions(rewards[chosen_reward], 'Upgrade')
            elif entity.upgrade_skills and rewards[chosen_reward]['Type'] == 'Skill':
                entity.card_actions(rewards[chosen_reward], 'Upgrade')
            elif entity.upgrade_powers and rewards[chosen_reward]['Type'] == 'Power':
                entity.card_actions(rewards[chosen_reward], 'Upgrade')
            entity.deck.append(rewards[chosen_reward])
            print(f"{entity.name} obtained {rewards[chosen_reward]['Name']}")
            rewards.clear()
            break
        for card in rewards:
            if card.get('Type') == 'Curse' and entity.block_curses > 0:
                ansiprint(f"{card['Name']} was negated by <bold>Omamori</bold>.")
                entity.block_curses -= 1
                if entity.block_curses == 0:
                    ansiprint('<bold>Omamori</bold> is depleted.')
                continue
            if card.get('Type') == 'Curse' and entity.darkstone_health:
                ansiprint("<bold>Darkstone Periapt</bold> activated.")
                entity.health_actions(6, "Max Health")
            entity.deck.append(card)
            print(f"{entity.name} obtained {card['Name']}")
            rewards.remove(card)
        if entity.gold_on_card_add:
            entity.gold += 9
            ansiprint('You gained 9 <yellow>Gold</yellow> from <bold>Ceramic Fish</bold>.')
        rewards.clear()
        sleep(1)

def view_piles(pile: list[dict], entity, end=False, condition='True'):
    """Prints a numbered list of all the cards in a certain pile."""
    if pile == entity.draw_pile:
        pile = random.sample(pile, len(pile))
    counter = 1
    for card in pile:
        upgrades = card.get('Upgrade Count', '')
        upgrade_check = card.get('Upgraded') or card.get('Upgrade Count', 0) > 0
        changed_energy = 'light-red' if not card.get('Changed Energy') else 'green'
        if eval(condition):
            ansiprint(f"{counter}: <{card['Type'].lower()}>{card['Name']}</{card['Type'].lower()}>{f'<green>+{upgrades}</green>' if upgrade_check else ''} | <{changed_energy}>{card['Energy']}{' Energy' if isinstance(card.get('Energy'), int) else ''}</{changed_energy}> | <yellow>{card['Info']}</yellow>".replace('Σ', '').replace('꫱', ''))
            counter += 1
            sleep(0.05)
        else:
            ansiprint(f"{counter}: <light-black>{card['Name']} | {card['Type']} | {card['Energy']}{' Energy' if isinstance(card.get('Energy'), int) else ''} | {card['Info']}</light-black>".replace('Σ', '').replace('꫱', ''))
            counter += 1
            sleep(0.05)
    if end:
        input("Press enter to continue > ")
    sleep(1.0)
    if end:
        sleep(0.5)
        clear()

def display_ui(entity, combat=True):
    # Repeats for every card in the entity's hand
    ansiprint("<bold>Hand: </bold>")
    view_piles(entity.hand, entity, False, "card.get('Energy', float('inf')) <= entity.energy")
    if combat is True:
        for enemy in active_enemies:
            enemy.show_status()
        # Displays the number of cards in the draw and discard pile
        # Displays the entity's current health, block, energy, debuffs and buffs.
        entity.show_status()
    else:
        entity.show_status(False)
    print()



def list_input(input_string: str, array: list) -> int | None:
    try:
        ansiprint(input_string, end='')
        option = int(input()) - 1
        array[option] = array[option] # Checks that the number is in range but doesn't really do anything
    except ValueError:
        return None
    except IndexError:
        return None
    return option

def remove_color_tags(string: str) -> str:
    pattern = r"<(\w+)>" # Pattern that searches for the word between < and > without symbols
    colors = re.findall(pattern, string)
    for color in colors:
        string = string.replace(color, '') # Removes all of the colors found by the findall() function
    string = string.replace('<', '').replace('>', '').replace('/', '') # Removes all color tag symbols
    return string

def calculate_actual_damage(string: str, target, entity, card: dict) -> tuple[str, str]:
    match = re.search(r"Σ(\d+)", string)
    affected_by = ''
    if match:
        original_damage: str = match.group()
        damage_value = int(original_damage.replace('Σ', ''))
        if "Body Slam" in card.get('Name'):
            damage_value += entity.block
        if "Perfected Strike" in card.get('Name'):
            perfected_strike_dmg = len([card for card in entity.deck if 'strike' in card.get('Name')]) * card.get('Damage Per "Strike"')
            damage_value += perfected_strike_dmg
            affected_by += f"Perfected Strike(+{perfected_strike_dmg} dmg)"
        if entity.buffs['Strength'] != 0:
            damage_value += entity.buffs['Strength'] * card.get("Strength Multi", 1)
            affected_by += f"<{'<light-cyan>' if entity.buffs['Strength'] > 0 else '<red>'}Strength{'</light-cyan>' if entity.buffs['Strength'] > 0 else '</red>'}>({'+' if entity.buffs['Strength'] > 0 else '-'}{abs(entity.buffs['Strength']) * card.get('Strength Multi', 1)} dmg) | "
            if card.get("Strength Multi", 1) > 1:
                affected_by += f"Heavy Blade(x{card.get('Strength Multi')} Strength gain)"
        if entity.buffs['Vigor'] > 0:
            damage_value += entity.buffs['Vigor']
            affected_by += f"<light-cyan>Vigor</light-cyan>(+{entity.buffs['Vigor']} dmg) | "
        if target.debuffs['Vulnerable'] > 0:
            damage_value = math.floor(damage_value * 1.5)
            affected_by += "Target's <light-cyan>Vulnerable</light-cyan>(x1.50 dmg) | "
        if entity.debuffs['Weak'] > 0:
            damage_value = math.floor(damage_value * 0.75)
            affected_by += "<red>Weak</red>(x0.75 dmg)"
        string = string.replace(original_damage, str(damage_value))
    return string, affected_by

def calculate_actual_block(string: str, entity) -> tuple[str, str]:
    match = re.search(r"꫱(\d+)", string)
    affected_by = ''
    if match:
        original_damage = match.group()
        block_value = int(original_damage.replace('꫱', ''))
        if entity.buffs["Dexterity"] != 0:
            block_value += entity.buffs['Dexterity']
            affected_by += f"{'<light-cyan>' if entity.buffs['Dexterity'] > 0 else '<red>'}Dexterity{'</light-cyan>' if entity.buffs['Dexterity'] > 0 else '<red>'}({'+' if entity.buffs['Dexterity'] > 0 else '-'}{abs(entity.buffs['Dexterity'])} block)"
        if entity.debuffs['Frail'] > 0:
            block_value = math.floor(block_value * 0.75)
            affected_by += "<red>Frail</red>(x0.75 block)"
        string = string.replace(original_damage, str(block_value))
    return string, affected_by

def modify_energy_cost(amount: int, modify_type: str, card: dict):
    if (modify_type == 'Set' and amount != card['Energy']) or (modify_type == 'Adjust' and amount != 0):
        card['Changed Energy'] = True
    if modify_type == 'Set':
        card['Energy'] = amount
        ansiprint(f"{card['Name']} has its energy cost set to {amount}")
    elif modify_type == 'Adjust':
        card['Energy'] += amount
        ansiprint(f"{card['Name']} got its energy cost {'<green>reduced</green>' if amount < 0 else '<red>increased</red>'} by {abs(amount)}")
    return card

def clear():
    system('clear')
