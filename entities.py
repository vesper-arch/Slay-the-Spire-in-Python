import math
import sys
import random
from time import sleep
from os import system
from ansimarkup import parse, ansiprint
from utility import damage, active_enemies, combat_turn


class Player:
    """
    Attributes:::
    health: Player's current health
    block: Block reduces the damage deal by attacks and is removed at the start of their turn
    max_health: Maximum amount of health the player can have
    energy: Used to play cards
    max_energy: Maximum amount of energy the player can have
    deck: All the cards that can appear in game. Players can collect cards to add to the deck
    hand: The cards availible to play at any given time
    draw_pile: A randomized instance of the deck, cards are drawn in order from it.(All cards from the discard pile are shuffled into this when the draw pile is empty)
    discard_pile: Cards get put here when they are played
    exhaust_pile: List of exhausted cards
    draw_strength: Amount of cards the player draws at the start of their turn
    weak: Deals 25% less damage with Attacks(duration stack, rounded down)
    frail: Gains 25% less block from cards(duration stack, rounded down)
    vulnerable: Takes 50% more damage from attacks(duration stack, rounded down)
    entangled: You cannot play Attacks this turn(Does not stack)
    strength: Deal X more damage(intensity stack, can be negative)
    strength_down: Lose X Strength next turn(intensity stack, completely removed at the start of turn)
    """

    def __init__(self, health: int, block: int, max_energy: int, deck: list):
        self.health = health
        self.block = block
        self.name = "Ironclad"
        self.max_health = health
        self.energy = 0
        self.max_energy = max_energy
        self.energy_gain = max_energy
        self.energized = 0
        self.deck = deck
        self.hand = []
        self.draw_pile = []
        self.discard_pile = []
        self.draw_strength = 5
        self.exhaust_pile = []
        self.gold = 0
        self.barricade = False
        self.weak = 0
        self.frail = 0
        self.vulnerable = 0
        self.entangled = False
        self.strength = 0
        self.strength_down = 0
        self.confused = False
        self.dexterity = 0
        self.dexterity_down = 0
        self.focus = 0
        self.no_draw = False
        self.poison = 0
        self.shackled = False
        self.artifact = 0
        self.block_next_turn = 0
        self.vigor = 0
        self.thorns = 0

    def use_card(self, card: dict, target: object):
        """
        Uses a card
        Wow!
        """
        if "Strike" in card["Name"]:
            self.use_strike(target, card)
        elif "Bash" in card["Name"]:
            self.use_bash(target, card)
        elif "Defend" in card["Name"]:
            self.use_defend(card)
        elif "Cleave" in card["Name"]:
            self.use_cleave(active_enemies, card)
        elif "Clash" in card["Name"]:
            self.use_clash(target, card)
        elif "Perfected Strike" in card["Name"]:
            self.use_perfectedstrike(target, card)
        elif "Body Slam" in card["Name"]:
            self.use_bodyslam(target, card)

    def use_strike(self, targeted_enemy: object, using_card):
        base_damage = using_card["Damage"]
        if "+" in using_card["Name"]:
            base_damage += 3
        print()
        # If the enemy has the Vulnerable debuff applied to it, multiply the damage by 1.5 and round it up to the nearest whole number
        damage(base_damage, targeted_enemy, player)
        # Takes the card's energy cost away from the player's energy
        self.move_card(using_card, self.discard_pile, self.hand, True)
        print()
        sleep(1)
        system("clear")

    def use_bash(self, targeted_enemy: object, using_card):
        base_damage = using_card["Damage"]
        base_vulnerable = using_card["Vulnerable"]
        if "+" in using_card["Name"]:
            base_damage += 2
            base_vulnerable += 1
        print()
        # If the enemy has the Vulnerable debuff applied to it, multiply the damage by 1.5 and round it up to the nearest whole number
        damage(base_damage, targeted_enemy, player)
        self.debuff("Vulnerable", base_vulnerable, targeted_enemy, True)
        # prevents the enemy's health from going below 0
        self.move_card(using_card, self.discard_pile, self.hand, True)
        print()
        sleep(1.5)
        system("clear")

    def use_defend(self, using_card):
        base_block = using_card["Block"]
        if "+" in using_card["Name"]:
            base_block += 3
        print()
        self.blocking(base_block)
        self.move_card(using_card, self.discard_pile, self.hand, True)
        print()
        sleep(1.5)
        system("clear")
    def use_bodyslam(self, targeted_enemy, using_card):
        base_energy = using_card["Energy"]
        if "+" in using_card["Name"]:
            base_energy -= 1
        print()
        damage(using_card["Damage"], targeted_enemy, self)
        self.move_card(using_card, self.discard_pile, self.hand, True)
        print()
        sleep(1.5)
        system("clear")
    def use_clash(self, targeted_enemy, using_card):
        base_damage = using_card["Damage"]
        if "+" in using_card["Name"]:
            base_damage += 4
        print()
        while True:
            for card in self.hand:
                if card.get("Type") is None:
                    ansiprint("<light-red>PythonRail, *sigh* you forgot the 'Type' key-value pair")
                    sys.exit(2)
                elif card.get("Type") != "Attack":
                    ansiprint("<light-red>You have non-attack cards in your hand</light-red>")
                    break
            damage(base_damage, targeted_enemy, self)
            self.move_card(using_card, self.discard_pile, self.hand, True)
            break
        sleep(1.5)
        system("clear")
    def use_cleave(self, enemies, using_card):
        base_damage = using_card["Damage"]
        if "+" in using_card["Name"]:
            base_damage += 3
        print()
        for enemy in enemies:
            damage(base_damage, enemy, self)
        self.move_card(using_card, self.discard_pile, self.hand, True)
        sleep(1.5)
        system("clear")
    def use_perfectedstrike(self, targeted_enemy, using_card):
        damage_per_strike = using_card["Damage Per 'Strike'"]
        base_damage = using_card["Damage"]
        if "+" in using_card["Name"]:
            damage_per_strike = using_card["Damage Per 'Strike'"] + 1
        print()
        for card in self.deck:
            if "strike" in card["Name"].lower():
                base_damage += damage_per_strike
        damage(base_damage, targeted_enemy, self)
        self.move_card(using_card, self.discard_pile, self.hand, True)
        sleep(1.5)
        system("clear")

    def draw_cards(self):
        if len(player.draw_pile) < self.draw_strength:
            player.draw_pile.extend(random.sample(player.discard_pile, len(player.discard_pile)))
            player.discard_pile = []
        player.hand = player.draw_pile[-self.draw_strength:]
        # Removes those cards
        player.draw_pile = player.draw_pile[:-self.draw_strength]

    def blocking(self, block: int):
        if self.frail > 0:
            block = math.floor(block * 0.75)
        self.block += block
        ansiprint(f"{self.name} gained {block} <light-blue>Block</light-blue>")    

    def heal(self, heal):
        self.health += heal
        self.health = min(self.health, self.max_health)
        ansiprint(f"<green>{self.name} healed for {min(self.max_health - self.health, heal)} Health</green>")
        self.show_status(False)

    def RemoveCardFromDeck(self, card: dict, action: str):
        while True:
            if action == "Remove":
                counter = 1
                for using_card in player.deck:
                    ansiprint(f"{counter}: <light-black>{using_card['Type']}</light-black> | <blue>{using_card['Name']}</blue> | <light-red>{using_card['Energy']} Energy</light-red> | <yellow>{using_card['Info']}</yellow>")
                    counter += 1
                try:
                    remove_index = int(input("What card do you want to remove?")) - 1
                except ValueError:
                    print("You have to enter a number")
                    sleep(1)
                    system("clear")
                    continue
                player.deck.remove(remove_index)
            elif action == 'Upgrade':
                player.deck.remove(card)
                player.deck.append(cards[card["Name", '+']])

    def show_status(self, combat=True):
        if combat is True:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)"
            if self.weak > 0:
                status += f" | <light-cyan>Weak: {self.weak}</light-cyan>"
            if self.frail > 0:
                status += f" | <light-cyan>Frail: {self.frail}</light-cyan>"
            if self.vulnerable > 0:
                status += f" | <light-cyan>Vulnerable: {self.vulnerable}</light-cyan>"
            if self.energized > 0:
                status += f" | <light-cyan>Energized: {self.energized}</light-cyan>"
            if self.artifact > 0:
                status += f" | <light-cyan>Artifact: {self.artifact}</light-cyan>"
        else:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <yellow>{self.gold} Gold</yellow>)"
        ansiprint(status, "\n")

    def end_player_turn(self):
        player.discard_pile.extend(player.hand)
        player.hand = []
        player.draw_cards()
        player.energy = player.max_energy
        sleep(1.5)
        system("clear")

    def move_card(self, card, to, from_loc, cost_energy):
        if cost_energy is True:
            self.energy -= card["Energy"]
        from_loc.remove(card)
        to.append(card)

    def debuff(self, debuff_name, amount, target, end):
        if target.artifact == 0:
            if debuff_name == "Weak":
                target.weak += amount
            elif debuff_name == "Poison":
                target.poison += amount
            elif debuff_name == "Vulnerable":
                target.vulnerable += amount
            elif debuff_name == "Weakened":
                target.weakened += amount
            elif debuff_name == "Strength":
                target.strength -= amount
            elif debuff_name == "Shackled":
                target.shackled += amount
            ansiprint(f"{self.name} applied {amount} <light-cyan>{debuff_name}</light-cyan> to {target.name}")
        else:
            ansiprint(f"{debuff_name} was blocked by {target.name}'s <light-cyan>Artifact</light-cyan")
            target.artifact -= 1
        if end is False:
            sleep(1)
        else:
            sleep(1.5)
            system("clear")
    def buff(self, buff_name, amount, end):
        if buff_name == "Strength":
            self.strength += amount
        elif buff_name == "Dexterity":
            self.dexterity += amount
        elif buff_name == "Artifact":
            self.artifact += amount
        elif buff_name == "Energized":
            self.energy_gain += amount
        elif buff_name == "Draw Card":
            self.draw_strength += amount
        elif buff_name == "Barricade":
            self.barricade = True
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)
    def gain_gold(self, gold):
        self.gold += gold
        ansiprint(f"{self.name} gained <green>{gold}</green> <yellow>Gold</yellow>")
        sleep(1)
    def debuff_tick(self):
        if self.vulnerable > 0:
            self.vulnerable -= 1
            ansiprint("<light-cyan>-1 Vulnerable</light-cyan>")
        if self.weak > 0:
            self.weak -= 1
            ansiprint("<light-cyan>-1 Weak</light-cyan>")
        


class Enemy:
    def __init__(self, health: list, block: int, name: str, past_moves: dict):
        '''
        Attributes::
        health: Current health[int]
        max_health: Maximum health[int]
        block: Current block[int]
        name: Enemy name[str]
        order: Order of moves(planning on using parsing to run)[list]
        moves: All moves the enemy can use[2D dict]
        barricade: Block is not removed at the start of combat[bool]
        artifact: Blocks the next debuff[int]
        vulnerable: Takes 50% more damage from attacks[int](duration stack)
        weak: Deals 25% less damage with attacks[int](duration stack)
        strength: Deal X more damage[int](intensity stack)
        ritual: At the end of it's turn, gains X Strength(intensity stack)
        '''
        self.health = health
        self.max_health = health
        self.block = block
        self.name = name
        self.past_moves = past_moves
        self.barricade = False
        self.artifact = 0
        if self.name == "Spheric Guardian":
            self.barricade = True
            self.artifact = 3
        self.vulnerable = 0
        self.weak = 0
        self.strength = 0
        self.ritual = 0
        self.weakened = 0
        self.shackled = 0
        self.strength = 0
        self.active_turns = 1
        # PArsing to determine the order of moves
        #for item in self.order:
        #    # Contains all the items with percent symbols in them
        #    parsed_order = []
        #    # Adds the respective items
        #    if "%" in item:
        #        parsed_order.append(item)
        #    # Dictionary is basically (The text before the % symbol: the number after the % symbol)
        #    # Contains the percent chances for each move
        #    percent_chances = {text[:text.index("%")]: int(
        #        text[text.index("%") + 1]) for text in parsed_order}
        #    # Checks if the first character is a right facing arrow
        #    if item[:1] == ">":
        #        # List of all the indexes and extras instructions in between ()s
        #        repeats = [
        #            item[item.index["("] + 1: item[item.index[")"]]].split(",")]
        #        for index in repeats:
        #            if index.isdigit() is True:
        #                int(index)
        #            else:
        #                if index == "inf":
        #                    rep_inf = True
        #                    repeats.remove(index)

    def die(self):
        """
        Dies.
        """
        print(f"{self.name} has died.")
        active_enemies.remove(self)

    def debuff_and_buff_check(self):
        """
        Not finished
        """
        pass

    def enemy_turn(self):
        global combat_turn
        if self.name == "Blue Slaver":
            random_num = random.randint(0, 100)
            if random_num >= 60 and self.past_moves[-2] != "Stab":
                # Stab: Deal 12 damage
                self.attack(12, 1, True, True, "Stab")
                self.past_moves.append("Stab")
            elif random_num < 60 and self.past_moves[-2] != "Rake":
                # Rake: Deal 7 damage, apply 1 Weak
                self.attack(7, 1, True, False, "Rake")
                self.debuff("Weak", 1, False, True)
                self.past_moves.append("Rake")
            self.active_turns += 1
        if self.name == "Acid Slime (L)" or self.name == "Acid Slime (M)":
            random_num = random.randint(0, 100)
            if self.health < math.floor(self.max_health * 0.5) and self.name == "Acid Slime (L)":
                ansiprint("<bold>Split<bold>")
                self.die()
                active_enemies.append(Enemy([self.health, self.health], 0, "Acid Slime (M)", []))
                print("Acid Slime (M) spawned!")
                active_enemies.append(Enemy([self.health, self.health], 0, "Acid Slime (M)", []))
                print("Acid Slime (M) spawned!")
                sleep(1.5)
                system("clear")
            elif random_num < 30 and self.past_moves[-2] != "Corrosive Spit":
                self.attack(11, 1, True, False, "Corrosive Spit")
                self.status(cards["Slimed"], 2, player.discard_pile, False, True)
                self.past_moves.append("Corrosive Spit")
            elif random_num > 70 and self.past_moves[-1] != "Lick":
                self.debuff("Weak", 2, True, True, "Lick")
                self.past_moves.append("Lick")
            elif self.past_moves[-1] != "Tackle":
                self.attack(16, 1, True, True, "Tackle")
                self.past_moves.append("Tackle")
            self.active_turns += 1
        elif self.name == "Acid Slime (S)":
            random_num = random.randint(0, 100)
            if random_num < 50 and self.active_turns == 1:
                self.debuff("Weak", 1, True, True, "Lick")
                self.past_moves.append("Lick")
            elif random_num > 50 and self.active_turns == 1:
                self.attack(3, 1, True, True, "Tackle")
                self.past_moves.append("Tackle")
            elif self.past_moves[-1] == "Lick":
                self.attack(3, 1, True, True, "Tackle")
                self.past_moves.append("Tackle")
            elif self.past_moves[-1] == "Tackle":
                self.debuff("Weak", 1, True, True, "Lick")
                self.past_moves.append("Lick")
            self.active_turns += 1

        combat_turn += 1

    def show_status(self):
        status = f"{self.name} (<red>{self.health} / {self.max_health}</red> | <light-blue>{self.block} Block</light-blue>)"
        if self.barricade is True:
            status += " | <light-cyan>Barricade</light-cyan>"
        if self.artifact > 0:
            status += f" | <light-cyan>Artifact: {self.artifact}</light-cyan>"
        if self.vulnerable > 0:
            status += f" | <light-cyan>Vulnerable: {self.vulnerable}</light-cyan>"
        ansiprint(status, "\n")
    def attack(self, dmg, times, start, end, name=""):
        if start is True:
            ansiprint(f"<bold>{name}</bold>")
            sleep(1)
        for i in range(times):
            damage(dmg, player, self)
            sleep(0.5)
        if end is True:
            sleep(1)
            system("clear")
        else:
            sleep(0.5)
    def buff(self, buff, amount, start, end, name=""):
        if start is True:
            if name == "":
                ansiprint("<light-red>The starting function of a move MUST have a name!</light-red>")
                sys.exit(1)
        if buff == "Strength":
            self.strength += amount
            ansiprint(f"{self.name} gained <light-red>{amount} Strength</light-red>(Deals X more damage)")
        elif buff == "Ritual":
            self.ritual += amount
            ansiprint(f"{self.name} gained <cyan>{amount} Ritual</cyan>(Gains X <light-red>Strength</light-red> at the end of its turn)")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)
    def debuff(self, debuff, amount, start, end, name=""):
        if start is True:
            if name == "":
                ansiprint("<light-red>The starting function of a move MUST have a name!</light-red>")
                sys.exit(1)
            ansiprint(f"<bold>{name}</bold>")
            sleep(1)
        if debuff == "Weak":
            player.weak += amount
            ansiprint(f"{player.name} gained {amount} <yellow>Weak</yellow>(Deal 25% less damage with attacks)")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)
    def blocking(self, block, start, end, name=""):
        if start is True:
            if name == "":
                ansiprint("<light-red>The starting function of a move MUST have a name!</light-red>")
                sys.exit(1)
            ansiprint(f"<bold>{name}</bold>")
            sleep(1)
        self.block += block
        ansiprint(f"{self.name} gained {block} <blue>Block</blue>")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)
    def status(self, status_card, amount, location, start, end, name=""):
        if start is True:
            if name == "":
                ansiprint("<light-red>The starting function of a move MUST have a name!</light-red>")
                sys.exit()
            ansiprint(f"<bold>{name}</bold>")
            sleep(1)
        for i in range(amount):
            location.append(status_card)
        print(f"{player.name} gained {amount} {status_card['Name']}({status_card['Info']}) \nPlaced into {location}")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)


# Characters
player = Player(80, 0, 70, [])
cards = {
    "Strike": {"Name": "Strike", "Damage": 100, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 6 damage"},
    "Strike+": {"Name": "<green>Strike+</green>", "Upgraded": True, "Damage": 9, "Energy": 1, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 9 damage"},

    "Defend": {"Name": "Defend", "Block": 5, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain 5 <yellow>Block</yellow>"},
    "Defend+": {"Name": "<green>Defend+</green>", "Upgraded": True, "Block": 8, "Energy": 1, "Rarity": "Starter", "Type": "Skill", "Info": "Gain 8 <yellow>Block</yellow>"},

    "Bash": {"Name": "Bash", "Damage": 8, "Vulnerable": 2, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 8 damage. Apply 2 <yellow>Vulnerable</yellow>"},
    "Bash+": {"Name": "<green>Bash+</green>", "Upgraded": True, "Damage": 10, "Vulnerable": 3, "Energy": 2, "Rarity": "Starter", "Type": "Attack", "Info": "Deal 10 damage. Apply 3 <yellow>Vulnerable</yellow>"},

    "Body Slam": {"Name": "Body Slam", "Damage": player.block, "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Deal damage equal to your <yellow>Block</yellow>"},
    "Body Slam+": {"Name": "<green>Body Slam+</green>", "Upgraded": True, "Damage": player.block, "Energy": 0, "Rarity": "Common", "Type": "Attack", "Info": "Deal damage equal to your <yellow>Block</yellow>"},

    "Clash": {"Name": "Clash", "Damage": 14, "Energy": 0, "Rarity": "Common", "Type": "Attack", "Info": "Can only be played is every card in your hand is an Attack. Deal 14 damage."},
    "Clash+": {"Name": "<green>Clash+</green>", "Upgraded": True, "Damage": 18, "Energy": 0, "Rarity": "Common", "Type": "Attack", "Info": "Can only be player if every card in your hand is an Attack. Deal 18 damage."},

    "Cleave": {"Name": "Cleave", "Damage": 8, "Target": "All", "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Deal 8 damage to ALL enemies"},
    "Cleave+": {"Name": "<green>Cleave+</green>", "Damage": 11, "Target": "All", "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Deal 11 Damage to ALL enemies"},

    "Clothesline": {"Name": "Clothesline", "Energy": 2, "Damage": 12, "Weak": 2, "Rarity": "Common", "Type": "Attack", "Info": "Deal 12 damage. Apply 2 <yellow>Weak</yellow>"},
    "Clothesline+": {"Name": "<green>Clothesline+</green>", "Energy": 2, "Damage": 14, "Weak": 3, "Upgraded": True, "Rarity": "Common", "Type": "Attack", "Info": "Deal 14 damage. Apply 3 <yellow>Weak</yellow>"},

    "Flex": {"Name": "Flex", "Strength": 2, "Strength Down": 2, "Energy": 0, "Rarity": "Common", "Type": "Skill", "Info": "Gain 2 <yellow>Strength</yellow>. At the end of your turn, lose 2 <yellow>Strength</yellow>"},
    "Flex+": {"Name": "<green>Flex+</green>", "Upgraded": True, "Strength": 4, "Strength Down": 4, "Energy": 0, "Rarity": "Common", "Type": "Skill", "Info": "Gain 4 <yellow>Strength</yellow>. At the end of your turn lose 4 <yellow>Strength</yellow>"},

    "Heavy Blade": {"Name": "Heavy Blade", "Damage": 14, "Strength Multi": 3, "Energy": 2, "Rarity": "Common", "Type": "Attack", "Info": "Deal 14 damage. <yellow>Strength</yellow> affects this card 3 times."},
    "Heavy Blade+": {"Name": "<green>Heavy Blade+</green>", "Damage": 14, "Strength Multi": 5, "Energy": 2, "Rarity": "Common", "Type": "Attack", "Info": "Deal 14 damage. <yellow>Strength</yellow> affects this card 5 times"},

    "Iron Wave": {"Name": "Iron Wave", "Damage": 5, "Block": 5, "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Gain 5 <yellow>Block</yellow>. Deal 5 damage."},
    "Iron Wave+": {"Name": "<green>Iron Wave+</green>", "Damage": 7, "Block": 7, "Energy": 1, "Rarity": "Common", "Type": "Attack", "Info": "Gain 7 <yellow>Block</yellow>. Deal 7 damage."},

    "Perfected Strike": {"Name": "Perfected Strike", "Damage": 6, "Damage Per 'Strike'": 2, "Energy": 2, "Rarity": "Common", "Type": "Attack", "Info": "Deal 6 damage. Deals 2 additional damage for ALL your cards containing 'Strike'"},
    "Perfected Strike+": {"Name": "<green>Perfected Strike+</green>", "Damage": 6, "Damage Per 'Strike'": 3, "Energy": 2, "Rarity": "Common", "Type": "Attack", "Info": "Deal 6 damage. Deals 3 additional damage for ALL your cards containing 'Strike'"},

    "Slimed": {"Name": "Slimed", "Energy": 1, "Rarity": "Common", "Type": "Status", "Info": "<yellow>Exhaust</yellow>"}
}
player.deck = [cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Bash']]
# Enemies
encounters = [[Enemy([65, 69], 0, "Acid Slime (L)", ['PlAce', "Place", "place"])]]

def generate_card_rewards(reward_tier, amount):
    """
    Normal combat rewards:
    Rare: 3% | Uncommon: 37% | Common: 60%
    
    Elite combat rewards:
    Rare: 10% | Uncommon: 40% | Common: 50%
    
    Boss combat rewards:
    Rare: 100% | Uncommon: 0% | Common: 0%
    """
    common_cards = {card: attr for card, attr in cards.items() if attr.get("Rarity") == "Common" and attr.get("Type") != "Status" and '+' not in attr.get("Name")}
    uncommon_cards = {card: attr for card, attr in cards.items() if attr.get("Rarity") == "Uncommon" and attr.get("Type") != "Status" and '+' not in attr.get("Name")}
    rare_cards = {card: attr for card, attr in cards.items() if attr.get("Rarity") == "Rare" and attr.get("Type") != "Status" and '+' not in attr.get("Name")}

    rewards = []

    if reward_tier == "Normal":
        for i in range(amount):
            random_num = 70 # It's set to 1 because Uncommon and Rare cards don't exist yet
            if random_num < 3:
                random_key = random.choice(list(rare_cards.keys()))
                rewards.append(rare_cards[random_key])
            elif random_num > 60:
                random_key = random.choice(list(common_cards.keys()))
                rewards.append(common_cards[random_key])
            else:
                random_key = random.choice(list(uncommon_cards.keys()))
                rewards.append(uncommon_cards[random_key])
    elif reward_tier == "Elite":
        for i in range(amount):
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
        for i in range(amount):
            random_key = random.choice(list(rare_cards.keys()))
            random_value = rare_cards[random_value]
            rewards.append(random_key[random_value])
    while True:
        counter = 1
        for card in rewards:
            ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            counter += 1
        try:
             chosen_reward = int(input("What card do you want? > ")) - 1
        except ValueError:
            print("You have to enter a number")
            sleep(1.5)
            system("clear")
            continue
        player.deck.append(rewards[chosen_reward])
        print(f"{player.name} obtained {rewards[chosen_reward]['Name']}")
        rewards = []
        sleep(1.5)
        system("clear")
        break
#def potion_reward(amount, chance):
#    random_num = random.randint(1, 100)
#    if random_num < chance:
#        random_num = random.randint(1, 100)
#        if random_num > 65:

