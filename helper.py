import math
import random
import re
from copy import deepcopy
from os import name, system
from time import sleep
from typing import Callable

from ansi_tags import ansiprint, strip
from definitions import CardType, CombatTier, EnemyState, PlayerClass, Rarity
from message_bus_tools import Message, bus

active_enemies = []


class Displayer:
    """Displays important info to the player during combat"""

    def __init__(self):
        pass

    def view_piles(self, pile: list[dict], shuffle=False, end=False, validator: Callable = lambda placehold: bool(placehold)):
        """Prints a numbered list of all the cards in a certain pile."""
        if len(pile) == 0:
            ansiprint("<red>This pile is empty</red>.")
            sleep(1.5)
            self.clear()
            return
        if shuffle is True:
            pile = random.sample(pile, len(pile))
            ansiprint("<italic>Cards are not shown in order.</italic>")
        counter = 1
        for card in pile:
            if validator(card):
                ansiprint(f"{counter}: {card.pretty_print()}")
                counter += 1
                sleep(0.05)
            else:
                ansiprint(f"{counter}: <light-black>{strip(card.pretty_print())}</light-black>")
                counter += 1
                sleep(0.05)
        if end:
            input("Press enter to continue > ")
            sleep(0.5)
            self.clear()

    def view_relics(self, relic_pool, end=False, validator: Callable = lambda placehold: bool(placehold)):
        counter = 1
        for relic in relic_pool:
            if validator(relic):
                name_colors = {"Starter": "starter", "Common": "white", "Uncommon": "uncommon", "Rare": "rare", "Event": "event"}
                ansiprint(f"{counter}: <{name_colors[relic['Rarity']]}>{relic['Name']}</{name_colors[relic['Rarity']]}> | {relic['Class']} | <yellow>{relic['Info']}</yellow> | <dark-blue><italic>{relic['Flavor']}</italic></dark-blue>")
                counter += 1
                sleep(0.05)
        if end:
            input("Press enter to continue > ")
            sleep(1.5)
            self.clear()

    def view_potions(self, potion_pool, max_potions=3, numbered_list=True, validator: Callable = lambda placehold: bool(placehold)):
        class_colors = {"Ironclad": "red", "Silent": "dark-green", "Defect": "true-blue", "Watcher": "watcher-purple", "Any": "white"}
        rarity_colors = {"Common": "white", "Uncommon": "uncommon", "Rare": "rare"}
        counter = 1
        for potion in potion_pool:
            if validator(potion):
                chosen_class_color = class_colors[potion["Class"]]
                chosen_rarity_color = rarity_colors[potion["Rarity"]]
                ansiprint(f"{f'{counter}: ' if numbered_list else ''}<{chosen_rarity_color}>{potion.name}</{chosen_rarity_color}> | <{chosen_class_color}>{potion.player_class}</{chosen_class_color}> | <yellow>{potion.info}</yellow>")
                counter += 1
        for _ in range(max_potions - len(potion_pool)):
            ansiprint(f"<light-black>{f'{counter}: ' if numbered_list else ''}(Empty)</light-black>")
            counter += 1

    def view_map(self, game_map):
        game_map.pretty_print()
        print("\n")
        sleep(0.2)
        input("Press enter to leave > ")

    def display_ui(self, entity, enemies, combat=True):
        # Repeats for every card in the entity's hand
        ansiprint("<bold>Relics: </bold>")
        self.view_relics(entity.relics)
        ansiprint("<bold>Hand: </bold>")
        self.view_piles(entity.hand, entity, False, lambda card: (card.energy_cost if card.energy_cost != -1 else entity.energy) <= entity.energy)
        if combat is True:
            counter = 1
            ansiprint("\n<bold>Enemies:</bold>")
            viewable_enemies = [enemy for enemy in enemies if enemy.state in (EnemyState.ALIVE, EnemyState.INTANGIBLE)]
            for enemy in viewable_enemies:
                ansiprint(f"{counter}: " + repr(enemy))
                counter += 1
            ansiprint("\n" + repr(entity))
        else:
            ansiprint(str(entity))
        print()

    def list_input(self, input_string: str, choices: list, displayer: Callable, validator: Callable = lambda placehold: bool(placehold), message_when_invalid: str = None, extra_allowables=None) -> int | None:
        """Allows the player to choose from a certain list of options. Includes validation."""
        if extra_allowables is None:
            extra_allowables = []
        while True:
            try:
                displayer(choices, validator=validator)
                ansiprint(input_string + " > ", end="")
                response = input()
                if response in extra_allowables:
                    return response
                option = int(response) - 1
                if not validator(choices[option]):
                    ansiprint(f"\u001b[1A\u001b[1000D<red>{message_when_invalid}</red>", end="")
                    sleep(1.5)
                    print("\u001b[2K")
                    continue
            except (IndexError, ValueError):
                ansiprint(f"\u001b[1A\u001b[100D<red>You have to enter a whole number between 1 and {len(choices)}.</red>", end="")
                sleep(1)
                print("\u001b[2K\u001b[100D", end="")
                continue
            break
        return option

    def display_actual_damage(self, string: str, target, entity, card=None) -> tuple[str, str]:
        if not card:
            card = {}
        match = re.search(r"Σ(\d+)", string)
        affected_by = ""
        if match:
            original_damage: str = match.group()
            damage_value = int(original_damage.replace("Σ", ""))
            if "Body Slam" in card.get("Name", ""):
                damage_value += entity.block
            if "Perfected Strike" in card.get("Name", ""):
                perfected_strike_dmg = len([card for card in entity.deck if "strike" in card.get("Name")]) * card.get('Damage Per "Strike"')
                damage_value += perfected_strike_dmg
                affected_by += f"Perfected Strike(+{perfected_strike_dmg} dmg)"
            if entity.buffs["Strength"] != 0:
                damage_value += entity.buffs["Strength"] * card.get("Strength Multi", 1)
                affected_by += f"<{'<light-cyan>' if entity.buffs['Strength'] > 0 else '<red>'}Strength{'</light-cyan>' if entity.buffs['Strength'] > 0 else '</red>'}>({'+' if entity.buffs['Strength'] > 0 else '-'}{abs(entity.buffs['Strength']) * card.get('Strength Multi', 1)} dmg) | "
                if card.get("Strength Multi", 1) > 1:
                    affected_by += (f"Heavy Blade(x{card.get('Strength Multi')} Strength gain)")
            if entity.buffs.get("Vigor", 0) > 0:
                damage_value += entity.buffs.get("Vigor")
                affected_by += f"<light-cyan>Vigor</light-cyan>(+{entity.buffs.get('Vigor')} dmg) | "
            if target.debuffs["Vulnerable"] > 0:
                damage_value = math.floor(damage_value * 1.5)
                affected_by += f'{"Target" if hasattr(entity, "player_class") else "Your"} <debuff>Vulnerable</debuff>(x1.50 dmg) | '
            if entity.debuffs["Weak"] > 0:
                damage_value = math.floor(damage_value * 0.75)
                affected_by += "<red>Weak</red>(x0.75 dmg)"
            string = string.replace(original_damage, str(damage_value))
        return string, affected_by

    def display_actual_block(self, string: str, entity) -> tuple[str, str]:
        match = re.search(r"Ω(\d+)", string)
        affected_by = ""
        if match:
            original_damage = match.group()
            block_value = int(original_damage.replace("Ω", ""))
            if entity.buffs["Dexterity"] != 0:
                block_value += entity.buffs["Dexterity"]
                affected_by += f"{'<light-cyan>' if entity.buffs['Dexterity'] > 0 else '<red>'}Dexterity{'</light-cyan>' if entity.buffs['Dexterity'] > 0 else '<red>'}({'+' if entity.buffs['Dexterity'] > 0 else '-'}{abs(entity.buffs['Dexterity'])} block)"
            if entity.debuffs["Frail"] > 0:
                block_value = math.floor(block_value * 0.75)
                affected_by += "<red>Frail</red>(x0.75 block)"
            string = string.replace(original_damage, str(block_value))
        return string, affected_by

    def clear(self):
        system("cls" if name == "nt" else "clear")


class Generators:
    """Generates relic_pool, potions, and cards"""

    def __init__(self):
        pass

    def generate_card_rewards(self, reward_tier: CombatTier, amount: int, entity: object, card_pool: dict) -> list[dict]:
        """
        Normal combat rewards:
        Rare: 3% | Uncommon: 37% | Common: 60%

        Elite combat rewards:
        Rare: 10% | Uncommon: 40% | Common: 50%

        Boss combat rewards:
        Rare: 100% | Uncommon: 0% | Common: 0%
        """
        common_cards = [deepcopy(card) for card in card_pool if card.rarity == Rarity.COMMON and card.type not in (CardType.STATUS, CardType.CURSE) and card.player_class == entity.player_class]
        uncommon_cards = [deepcopy(card) for card in card_pool if card.rarity == Rarity.UNCOMMON and card.type not in (CardType.STATUS, CardType.CURSE) and card.player_class == entity.player_class]
        rare_cards = [deepcopy(card) for card in card_pool if card.rarity == Rarity.RARE and card.type not in (CardType.STATUS, CardType.CURSE) and card.player_class == entity.player_class]
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

    def generate_potion_rewards(self, amount: int, entity: object, potion_pool: dict, chance_based=True) -> list[dict]:
        """You have a 40% chance to get a potion at the end of combat.
        -10% when you get a potion.
        +10% when you don't get a potion."""
        common_potions: list[dict] = [potion() for potion in potion_pool if potion.rarity == Rarity.COMMON and (potion.player_class == PlayerClass.ANY or potion.player_class == entity.player_class)]
        uncommon_potions: list[dict] = [potion() for potion in potion_pool if potion.rarity == Rarity.UNCOMMON and (potion.player_class == PlayerClass.ANY or potion.player_class == entity.player_class)]
        rare_potions: list[dict] = [potion() for potion in potion_pool if potion.rarity == Rarity.RARE and (potion.player_class == PlayerClass.ANY or potion.player_class == entity.player_class)]
        assert len(common_potions) > 0, "Common potions pool is empty."
        assert len(uncommon_potions) > 0, "Uncommon potions pool is empty."
        assert len(rare_potions) > 0, "Rare potions pool is empty."

        all_potions = common_potions + uncommon_potions + rare_potions
        rarities = [common_potions, uncommon_potions, rare_potions]
        rewards = []
        for _ in range(amount):
            if chance_based:
                rewards.append(
                    random.choice(random.choices(rarities, [0.65, 0.25, 0.1], k=1)[0])
                )
            else:
                rewards.append(random.choice(all_potions))
        return rewards

    def generate_relic_rewards(self, source: str, amount: int, entity, relic_pool: dict, chance_based=True) -> list[dict]:
        claimed_relics = [relic.name for relic in entity.relics]

        common_relics = [relic() for relic in relic_pool if relic.get("Rarity") == "Common" and relic.get("Class") == entity.player_class and relic not in entity.relics and relic.name not in claimed_relics]
        uncommon_relics = [relic() for relic in relic_pool if relic.get("Rarity") == "Uncommon" and relic.get("Class") == entity.player_class and relic not in entity.relics and relic.name not in claimed_relics]
        rare_relics = [relic() for relic in relic_pool if relic.get("Rarity") == "Rare" and relic.get("Class") == entity.player_class and relic not in entity.relics and relic.name not in claimed_relics]

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

    def claim_relics(self, choice: bool, entity: object, relic_amount: int, relic_pool: dict = None, rewards: list = None, chance_based=True):
        relic_pool = relic_pool if relic_pool else relic_pool
        if not rewards:
            rewards = self.generate_relic_rewards("Other", relic_amount, entity, relic_pool, chance_based)
        if not choice:
            for i in range(relic_amount):
                entity.relics.append(rewards[i])
                entity.on_relic_pickup(rewards[i])
                ansiprint(f"{entity.name} obtained {rewards[i]['Name']} | {rewards[i]['Info']}")
                rewards.remove(rewards[i])
                sleep(0.5)
            sleep(0.5)
        while len(rewards) > 0 and choice:
            option = view.list_input("What relic do you want? > ", rewards, view.view_relics)
            if not option:
                sleep(1.5)
                view.clear()
                continue
            entity.relics.append(rewards[option])
            entity.on_relic_pickup(rewards[option])
            print(f"{entity.name} obtained {rewards[option]['Name']}.")
            rewards.remove(rewards[i])

    def claim_potions(self, choice: bool, potion_amount: int, entity, potion_pool: dict, rewards=None, chance_based=True):
        for relic in entity.relics:
            if relic.name == "Sozu":
                return
        if not rewards:
            rewards = self.generate_potion_rewards(
                potion_amount, entity, potion_pool, chance_based
            )
        if not choice:
            for i in range(potion_amount):
                if len(entity.potions) <= entity.max_potions:
                    entity.potions.append(rewards[i])
                    print(
                        f"{entity.name} obtained {rewards[i].name} | {rewards[i].info}"
                    )
                    rewards.remove(rewards[i])
            sleep(1.5)
            view.clear()
        while len(rewards) > 0:
            print(f"Potion Bag: ({len(potion_pool)} / {entity.max_potions})")
            view.view_potions(entity, False)
            print()
            print("Potion reward(s):")
            option = view.list_input(
                "What potion you want? >", rewards, view.view_potions
            )
            if len(potion_pool) == entity.max_potions:
                ansiprint("<red>Potion bag full!</red>")
                sleep(1)
                option = input("Discard a potion?(y|n) > ")
                if option == "y":
                    option = view.list_input(
                        "What potion do you want to discard? > ",
                        potion_pool,
                        view.view_potions,
                    )
                    print(f"Discarded {potion_pool[option]['Name']}.")
                    potion_pool.remove(potion_pool[option])
                    sleep(1.5)
                    view.clear()
                else:
                    sleep(1.5)
                    view.clear()
                continue
            potion_pool.append(rewards[option])
            rewards.remove(rewards[option])
            sleep(0.2)
            view.clear()

    def card_rewards(self, tier: str, choice: bool, entity, card_pool: dict, rewards=None):
        if not rewards:
            rewards = self.generate_card_rewards(
                tier, entity.card_reward_choices, entity, card_pool
            )
        while True:
            if choice:
                chosen_reward = view.list_input("What card do you want? > ", rewards, view.view_piles)
                if (
                    entity.upgrade_attacks
                    and rewards[chosen_reward].type == "Attack"
                    or (
                        entity.upgrade_skills
                        and rewards[chosen_reward].type == "Skill"
                        or entity.upgrade_powers
                        and rewards[chosen_reward].type == "Power"
                    )
                ):
                    rewards[chosen_reward].upgrade()
                entity.deck.append(rewards[chosen_reward])
                ansiprint(
                    f"{entity.name} obtained <bold>{rewards[chosen_reward].name}</bold>"
                )
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


class EffectInterface:
    """Responsible for applying effects, creating buff/debuff dictionaries, and counting down certain effects"""

    # I'm gonna leave this alone for now because that's a lot of changes to be made
    def __init__(self):
        # Effects that wear off at the start of your turn despite not being duration effects
        self.REMOVE_ON_TURN = (
            "Next Turn Block",
            "Energized",
            "Amplify",
            "Burst",
            "Double Tap",
            "Duplication",
            "Flame Barrier",
            "Rebound",
            "Simmering Rage",
            "No Draw",
            "Slow",
            "Choked",
            "Entangled",
        )
        self.DURATION_EFFECTS = (
            "Frail",
            "Poison",
            "Vulnerable",
            "Weak",
            "Draw Reduction",
            "Lock On",
            "No Block",
            "Intangible",
            "Blur",
            "Collect",
            "Double Damage",
            "Equilibrium",
            "Phantasmal",
            "Regeneration",
            "Fading",
        )
        self.NON_STACKING_EFFECTS = (
            "Confused",
            "No Draw",
            "Entangled",
            "Barricade",
            "Back Attack",
            "Life Link",
            "Minion",
            "Reactive",
            "Shifting",
            "Split",
            "Stasis",
            "Unawakened",
            "Blasphemer",
            "Corruption",
            "Electro",
            "Master Reality",
            "Pen Nib",
            "Simmering Rage",
            "Surrounded",
        )
        self.PLAYER_BUFFS = {
            "Artifact": "Negate the next X debuffs",
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
            "Corruption": "Skills cost 0. Whenever you play a Skill, <bold>Exhaust</bold> it",
            "Creative AI": "At the start of your turn, add X random <power>Power</power cards into your hand",
            "Dark Embrace": "Whenever a card is <bold>Exhausted</bold>, draw 1 card.",
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
        self.PLAYER_DEBUFFS = {
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
            "Wraith Form": "At the start of your turn, lose X <bold>Dexterity</bold>",
        }
        self.ENEMY_BUFFS = {
            "Artifact": "Negate the next X debuffs",
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
            "Life Link": "If other Darklings are still alive, revives in 2 turns",
            "Malleable": "On recieving attack damage, gains X <keyword>Block</keyword>. <keyword>Block</keyword> increases by 1 every time it's triggered. Resets to X at the start of your turn",
            "Minion": "Minions abandon combat without their leader",
            "Mode Shift": "After recieving X damage, changes to a defensive form",
            "Painful Stabs": "Whenever you recieve unblocked attack damage from this enemy, add X <status>Wounds</status> into your discard pile",
            "Reactive": "Upon recieving attack damage, changes its intent",
            "Sharp Hide": "Whenever you play an Attack, take X damage",
            "Shifting": "Upon losing HP, loses that much <buff>Strength</buff> until the end of its turn",
            "Split": "When its HP is at 50% or lower, splits into 2 smaller slimes with its current HP as their Max HP",
            "Spore Cloud": "On death, applies X <debuff>Vulnerable</debuff>",
            "Stasis": "On death, returns a stolen card to your hand",
            "Strength Up": "At the end of its turn, gains X <buff>Strength</buff>",
            "Thievery": "Steals X <yellow>Gold</yellow> when it attacks",
            "Time Warp": "Whenever you play N cards, ends your turn and gains X <buff>Strength</buff>",
            "Unawakened": "This enemy hasn't awakened yet...",
        }
        self.ENEMY_DEBUFFS = {
            "Poison": "At the beginning of its turn, loses X HP and loses 1 stack of Poison",
            "Shackled": "At the end of its turn, regains X <bold>Strength</bold>",
            "Slow": "The enemy recieves (X * 10)% more damage from attacks this turn. Whenever you play a card, increase Slow by 1",
            "Vulnerable": "You/It takes 50% more damage from attacks",
            "Weak": "You/It deals 25% less damage from attacks",
            "Block Return": "Whenever you attack this enemy, gain X <bold>Block</bold>",
            "Choked": "Whenever you play a card this turn, the targeted enemy loses X HP",
            "Corpse Explosion": "On death, deals X times its Max HP worth of damage to all other enemies",
            "Lock-On": "<bold>Lightning</bold> and <bold>Dark</bold> orbs deal 50% more damage to the targeted enemy",
            "Mark": "Whenever you play <bold>Pressure Points</bold>, all enemies with Mark lose X HP",
        }

        self.ALL_EFFECTS = {
            **self.PLAYER_BUFFS,
            **self.PLAYER_DEBUFFS,
            **self.ENEMY_BUFFS,
            **self.ENEMY_DEBUFFS,
        }

    def init_effects(self, effect_pool: str) -> dict:
        effect_pool = effect_pool.lower()
        initialized_effects = {}
        effect_groups = {
            "player debuffs": self.PLAYER_DEBUFFS,
            "player buffs": self.PLAYER_BUFFS,
            "enemy debuffs": self.ENEMY_DEBUFFS,
            "enemy buffs": self.ENEMY_BUFFS,
        }
        for buff in effect_groups[effect_pool]:
            if buff not in self.NON_STACKING_EFFECTS:
                initialized_effects[buff] = 0
            else:
                initialized_effects[buff] = False
        return initialized_effects

    def apply_effect(self, target, user, effect_name: str, amount=0, recursion_tag=False) -> None:
        """recurstion_tag is only meant for internal use to stop infinite loops with Champion Belt."""
        assert (effect_name in self.ALL_EFFECTS), f"{effect_name} is not a valid debuff or buff."
        champion_belt_activated = False
        current_relic_pool = (
            [relic.get("Name") for relic in user.relics]
            if getattr(user, "player_class", "placehold") in str(user)
            else []
        )
        color = ("debuff" if amount < 0 or (effect_name in self.ENEMY_DEBUFFS or effect_name in self.PLAYER_DEBUFFS) else "buff")
        if str(user) == "Player" and effect_name in ("Weak", "Frail"):
            if "Turnip" in current_relic_pool and effect_name == "Frail":
                ansiprint("<debuff>Frail</debuff> was blocked by your <bold>Turnip</bold>.")
            elif "Ginger" in current_relic_pool and effect_name == "Weak":
                ansiprint("<debuff>Weak</debuff> was blocked by <bold>Ginger</bold>")
            return
        if ((effect_name in self.ENEMY_DEBUFFS or effect_name in self.PLAYER_DEBUFFS) or amount < 0) and target.buffs["Artifact"] > 0:
            subject = getattr(target, "third_person_ref", "Your")
            ansiprint(f"<debuff>{effect_name}</debuff> was blocked by {subject} <buff>Artifact</buff>.")
        else:
            if effect_name in (*self.ENEMY_DEBUFFS, *self.PLAYER_DEBUFFS):
                if effect_name in self.NON_STACKING_EFFECTS:
                    target.debuffs[effect_name] = True
                else:
                    target.debuffs[effect_name] += amount
            elif effect_name in (*self.ENEMY_BUFFS, *self.PLAYER_BUFFS):
                if effect_name in self.NON_STACKING_EFFECTS:
                    target.buffs[effect_name] = True
                else:
                    target.buffs[effect_name] += amount
            if target == user and getattr(target, "player_class", "") in ("Ironclad", "Silent", "Defect", "Watcher"):
                ansiprint(f"You gained {f'{amount} ' if effect_name not in self.NON_STACKING_EFFECTS else ''}<{color}>{effect_name}</{color}>")
            elif target == user and str(user) == "Enemy":
                ansiprint(f"{target.name} gained {f'{amount} ' if effect_name not in self.NON_STACKING_EFFECTS else ''}<{color}>{effect_name}</{color}>")
            elif str(user) == "Enemy" and str(target) != "Enemy":
                ansiprint(f"{user.name} applied {f'{amount} ' if effect_name not in self.NON_STACKING_EFFECTS else ''}<{color}>{effect_name}</{color}> to you.")
            elif (getattr(user, "player_class", "") in ("Ironclad", "Silent", "Defect", "Watcher") and str(target) == "Enemy"):
                ansiprint(f"You applied {f'{amount} ' if effect_name not in self.NON_STACKING_EFFECTS else ''}<{color}>{effect_name}</{color}> to {target.name}")
            elif str(user) == str(target) and user != target:
                ansiprint(f"{user.name} applied {f'{amount} ' if effect_name not in self.NON_STACKING_EFFECTS else ''}<{color}>{effect_name}</{color}> to {target.name}.")
            if (
                "Champion Belt" in current_relic_pool
                and "Player" in str(user)
                and not recursion_tag
            ):
                self.apply_effect(target, user, "Weak", 1, True)
            if str(user) == "Enemy" and hasattr(target, "fresh_effects"):
                target.fresh_effects.append(effect_name)

    def tick_effects(self, subject):
        for buff in subject.buffs:
            if (buff in self.REMOVE_ON_TURN and subject.buffs.get(buff, 0) > 0 and buff not in getattr(subject, "fresh_effects", [])):
                subject.buffs[buff] = 0
                ansiprint(f"<buff>{buff}</buff> wears off.")
            elif (buff in self.DURATION_EFFECTS and subject.buffs.get(buff, 0) > 0 and buff not in getattr(subject, "fresh_effects", [])):
                subject.buffs[buff] -= 1
                if subject.buffs[buff] == 0:
                    ansiprint(f"<buff>{buff}</buff> wears off.")
        for debuff in subject.debuffs:
            if (debuff in self.REMOVE_ON_TURN and subject.debuffs.get(debuff, 0) > 0 and debuff not in getattr(subject, "fresh_effects", [])):
                subject.debuffs[debuff] = 0
                ansiprint(f"<debuff>{debuff}</debuff> wears off.")
                continue
            if (debuff in self.DURATION_EFFECTS and subject.debuffs.get(debuff, 0) > 0 and debuff not in getattr(subject, "fresh_effects", [])):
                subject.debuffs[debuff] -= 1
                if subject.debuffs[debuff] == 0:
                    ansiprint(f"<debuff>{debuff}</debuff> wears off.")

    def full_view(self, entity, enemies):
        ansiprint(f"<bold>{entity.name}</bold>")
        for buff in entity.buffs:
            if int(entity.buffs[buff]) > 0:
                ansiprint(f"<buff>{buff}</buff>: {self.ALL_EFFECTS[buff].replace('X', str(entity.buffs[buff]))}")
        for debuff in entity.debuffs:
            if int(entity.debuffs[debuff]) > 0:
                ansiprint(f"<debuff>{debuff}</debuff>: {self.ALL_EFFECTS[debuff].replace('X', str(entity.debuff[debuff]))}")
        for enemy in enemies:
            ansiprint(f"<bold>{enemy.name}</bold>:")
            for buff in enemy.buffs:
                if int(enemy.buffs[buff]) > 0:
                    ansiprint(f"<buff>{buff}</buff>: {self.ALL_EFFECTS[buff].replace('X', str(enemy.buffs[buff]))}")
            for debuff in enemy.debuffs:
                if int(enemy.debuffs[debuff]) > 0:
                    ansiprint(f"<debuff>{debuff}</debuff>: {self.ALL_EFFECTS[debuff].replace('X', str(enemy.debuffs[debuff]))}")


ei = EffectInterface()
gen = Generators()
view = Displayer()
