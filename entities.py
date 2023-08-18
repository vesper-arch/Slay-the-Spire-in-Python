import math
import sys
import random
from time import sleep
from os import system
from ansimarkup import ansiprint

from utility import damage, active_enemies, combat_turn, integer_input


class Player:
    """
    Attributes:::
    health: The player's current health
    block: The amount of damage the player can take before losing health. Removed at the start of their turn
    name: The player's name
    player_class: Ironclad, Silent, Defect, and Watcher
    max_health: The max amount health the player can have
    energy: Resource used to play cards. Replenished at the start of their turn
    max_energy/energy_gain: The base amount of energy the player gains at the start of their turn
    deck: All the cards the player has
    potions: Consumables that have varying effects.
    potion_bag: The max amount of potions the player can have
    """

    def __init__(self, health: int, block: int, max_energy: int, deck: list):
        self.health = health
        self.block = block
        self.name = "Ironclad"
        self.player_class = "Ironclad"
        self.max_health = health
        self.energy = 0
        self.max_energy = max_energy
        self.energy_gain = max_energy
        self.energized = 0
        self.deck = deck
        self.potions = []
        self.relics = []
        self.potion_bag = 3
        self.hand = []
        self.draw_pile = []
        self.discard_pile = []
        self.card_reward_choices = 3
        self.draw_strength = 5
        self.draw_up = 0
        self.no_draw = False
        self.exhaust_pile = []
        self.orbs = []
        self.orb_slots = 3
        self.next_turn_block = 0
        self.regen = 0
        self.regeneration = 0
        self.gold = 0
        self.barricade = False
        self.hex = 0
        self.weak = 0
        self.frail = 0
        self.vulnerable = 0
        self.metallicize = 0
        self.entangled = False
        self.strength = 0
        self.strength_down = 0
        self.confused = False
        self.dexterity = 0
        self.dexterity_down = 0
        self.ritual = 0 # Gain X Strength at the end of your turn
        self.focus = 0
        self.no_draw = False
        self.poison = 0
        self.shackled = False
        self.artifact = 0
        self.intangible = 0
        self.vigor = 0
        self.thorns = 0
        self.plated_armor = 0

    def use_card(self, card: dict, target: object, exhaust, pile):
        """
        Uses a card
        Wow!
        """
        if card.get('Name') == 'Slimed':
            self.move_card(card, self.exhaust_pile, pile, True)
        if card.get('Target') == 'Single':
            card['Function'](target, card)
        elif card.get('Target') in ('Area', 'Random'):
            card['Function'](active_enemies, card)
        else:
            card['Function'](card)

        if exhaust is True:
            ansiprint(f"{card['Name']} was <bold>Exhausted</bold>.")
            self.move_card(card, self.exhaust_pile, pile, True)
        else:
            self.move_card(card, self.discard_pile, pile, True)

    def use_strike(self, targeted_enemy: object, using_card):
        '''Deals 6(9) damage.'''
        base_damage = using_card['Damage']
        if "+" in using_card['Name']:
            base_damage += 3
        print()
        damage(base_damage, targeted_enemy, player)
        # Takes the card's energy cost away from the player's energy
        print()
        sleep(1)
        system("clear")

    def use_bash(self, targeted_enemy: object, using_card):
        '''Deals 8(10) damage. Apply 2(3) Vulnerable'''
        base_damage = using_card['Damage']
        base_vulnerable = using_card['Vulnerable']
        # Checks if the card is upgraded
        if "+" in using_card['Name']:
            base_damage += 2
            base_vulnerable += 1
        print()
        damage(base_damage, targeted_enemy, player)
        self.debuff("Vulnerable", base_vulnerable, targeted_enemy, True)
        # prevents the enemy's health from going below 0
        print()
        sleep(1.5)
        system("clear")

    def use_defend(self, using_card):
        '''Gain 5(8) Block'''
        base_block = using_card['Block']
        if "+" in using_card['Name']:
            base_block += 3
        print()
        self.blocking(base_block)
        print()
        sleep(1.5)
        system("clear")
    def use_bodyslam(self, targeted_enemy, using_card):
        '''Deals damage equal to your Block. Exhaust.(Don't Exhaust)'''
        base_energy = using_card['Energy']
        if "+" in using_card['Name']:
            base_energy -= 1
        print()
        damage(using_card['Damage'], targeted_enemy, self)
        print()
        sleep(1.5)
        system("clear")
    def use_clash(self, targeted_enemy, using_card):
        '''Can only be played if there are no non-attack cards in your hand. Deal 14(18) damage.'''
        base_damage = using_card['Damage']
        if "+" in using_card['Name']:
            base_damage += 4
        print()
        while True:
            for card in self.hand:
                if card.get("Type") is None:
                    system("clear")
                    ansiprint("<light-red>PythonRail, *sigh* you forgot the 'Type' key-value pair")
                    sys.exit(2)
                elif card.get("Type") != "Attack":
                    ansiprint("<light-red>You have non-attack cards in your hand</light-red>")
                    break
            damage(base_damage, targeted_enemy, self)
            break
        sleep(1.5)
        system("clear")

    def use_heavyblade(self, targeted_enemy, using_card):
        '''Deal 14(18) damage. Strength affects this card 3(5) times'''
        strength_multi = 3
        if '+' in using_card['Name']:
            strength_multi += 2
        damage(using_card['Damage'] * strength_multi, targeted_enemy, self)
        sleep(1.5)
        system("clear")

    def use_cleave(self, enemies, using_card):
        '''Deal 8 damage to ALL enemies.'''
        base_damage = using_card['Damage']
        if "+" in using_card['Name']:
            base_damage += 3
        print()
        for enemy in enemies:
            damage(base_damage, enemy, self)
        sleep(1.5)
        system("clear")

    def use_perfectedstrike(self, targeted_enemy, using_card):
        '''Deal 6 damage. Deals 2(3) additional damage for ALL your cards containing "Strike"'''
        damage_per_strike = using_card['Damage Per "Strike"']
        base_damage = using_card['Damage']
        if "+" in using_card['Name']:
            damage_per_strike = using_card['Damage Per "Strike"'] + 1
        print()
        for card in self.deck:
            if "strike" in card['Name'].lower():
                base_damage += damage_per_strike
        damage(base_damage, targeted_enemy, self)
        sleep(1.5)
        system("clear")

    def use_anger(self, targeted_enemy, using_card):
        '''Deal 6(8) damage. Add a copy of this card to your discard pile.'''
        base_damage = using_card['Damage']
        if '+' in using_card['Name']:
            base_damage += 2
        print()
        damage(base_damage, targeted_enemy, self)
        self.discard_pile.append(using_card)
        sleep(1.5)
        system("clear")

    def use_clothesline(self, targeted_enemy, using_card):
        '''Deal 12(14) damage. Apply 2(3) Weak'''
        base_damage = using_card['Damage']
        base_weak = using_card['Weak']
        if '+' in using_card['Name']:
            base_damage += 2
            base_weak += 1
        print()
        damage(base_damage, targeted_enemy, self)
        self.debuff("Weak", base_weak, targeted_enemy, True)
        sleep(1.5)
        system("clear")

    def use_havoc(self, using_card):
        '''Play the top card of your draw pile and Exhaust it.'''
        base_energy = using_card['Energy']
        if '+' in using_card['Name']:
            base_energy -= 1
        print()
        self.use_card(self.draw_pile[-1], random.choice(active_enemies), True, self.draw_pile)
        sleep(1.5)
        system("clear")

    def use_flex(self, using_card):
        '''Gain 2(4) Strength. At the end of your turn, lose 2(4) Strength'''
        base_temp_strength = 2
        if '+' in using_card['Name']:
            base_temp_strength += 2
        self.buff("Strength(Temp)", base_temp_strength, True)

    def use_headbutt(self, targeted_enemy, using_card):
        '''Deal 9(12) damage. Put a card from your discard pile on top of your draw pile.'''
        base_damage = 9
        if '+' in using_card['Name']:
            base_damage += 3
        counter = 1
        damage(base_damage, targeted_enemy, self)
        while True:
            for card in self.discard_pile:
                ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                counter += 1
                sleep(0.05)
            choice = integer_input('What card do you want to put on top of your draw pile? > ', self.discard_pile)
            if choice is False:
                system("clear")
                continue
            self.move_card(self.discard_pile[choice], self.discard_pile, self.draw_pile, True)
            break
        sleep(1.5)
        system("clear")

    def use_shrugitoff(self, using_card):
        '''Gain 8(11) Block. Draw 1 card.'''
        base_block = 8
        if '+' in using_card['Name']:
            base_block += 3
        self.blocking(base_block)
        self.draw_cards(True, 1)
        sleep(1.5)
        system("clear")

    def use_swordboomerang(self, enemies, using_card):
        '''Deal 3 damage to a random enemy 3(4) times.'''
        base_times = 3
        if '+' in using_card['Name']:
            base_times += 1
        for _ in range(base_times):
            damage(using_card['Damage'], random.choice(enemies), self)
        sleep(1.5)
        system("clear")

    def use_thunderclap(self, enemies, using_card):
        '''Deal 4(7) damage and apply 1 Vulnerable to ALL enemies.'''
        base_damage = 4
        if '+' in using_card['Name']:
            base_damage += 3
        for enemy in enemies:
            damage(base_damage, enemy, self)
            self.debuff("Vulnerable", 1, enemy, True)
        sleep(0.5)
        system("clear")

    def use_ironwave(self, targeted_enemy, card):
        '''Gain 5(7) Block. Deal 5(7) damage.'''
        base_block = 5
        base_damage = 5
        if '+' in card['Name']:
            base_block += 2
            base_damage += 2
        damage(base_damage, targeted_enemy, self)
        self.blocking(base_block)
        sleep(1.5)
        system("clear")

    def use_pommelstrike(self, targeted_enemy, using_card):
        '''Deal 9(10) damage. Draw 1(2) cards.'''
        base_damage = 9
        base_cards = 1
        if '+' in using_card['Name']:
            base_damage += 1
            base_cards += 1
        damage(base_damage, targeted_enemy, self)
        self.draw_cards(True, base_cards)
        sleep(1.5)
        system("clear")

    def draw_cards(self, middle_of_turn, draw_cards):
        '''Draws [draw_cards] cards.'''
        if draw_cards == 0:
            draw_cards = self.draw_strength
        while True:
            if self.no_draw is True:
                print("You can't draw any more cards")
                break
            if middle_of_turn is False:
                draw_cards += self.draw_up
            if len(player.draw_pile) < draw_cards:
                player.draw_pile.extend(random.sample(player.discard_pile, len(player.discard_pile)))
                player.discard_pile = []
                ansiprint("<bold>Discard pile shuffled into draw pile.</bold>")
            player.hand.extend(player.draw_pile[-draw_cards:])
            # Removes those cards
            player.draw_pile = player.draw_pile[:-draw_cards]
            print(f"{self.name} drew {draw_cards} cards.")
            break

    def blocking(self, block: int, card=True):
        '''Gains [block] Block. Cards are affected by Dexterity and Frail.'''
        block += self.dexterity
        if self.frail > 0:
            block = math.floor(block * 0.75)
        self.block += block
        if self.dexterity > 0 and card is True:
            ansiprint(f"{self.name} gained <green>{block}</green> <light-blue>Block</light-blue>")
        elif self.dexterity < 0 or self.frail > 0 and card is True:
            ansiprint(f"{self.name} gained <red>{block}</red> <light-blue>Block</light-blue>")
        else:
            ansiprint(f"{self.name} gained {block} <light-blue>Block</light-blue>")

    def health_actions(self, heal, heal_type):
        '''If [heal_type] is 'Heal', you heal for [heal] HP. If [heal_type] is 'Max Health', increase your max health by [heal].'''
        if heal != self.max_health and heal_type == "Heal":
            self.health += heal
            self.health = min(self.health, self.max_health)
            ansiprint(f"You heal <green>{min(self.max_health - self.health, heal)}</green> <light-blue>HP</light-blue")
            self.show_status(False)
        elif heal == self.max_health and heal_type == "Heal":
            self.health += heal
            self.health = min(self.health, self.max_health)
            ansiprint("You are <green>healed</green> to full HP")
            self.show_status(False)
        elif heal_type == "Max Health":
            self.max_health += heal
            self.health += heal
            ansiprint(f"Your Max HP is increased by <light-blue>{heal}</light-blue>")
            self.show_status(False)

    def card_actions(self, card, action: str):
        '''[action] == 'Remove', remove [card] from your deck.
        [action] == 'Upgrade', Upgrade [card]
        [action] == 'Transform', transform a card into another random card.
        [action] == 'Store', (Only in the Note From Yourself event) stores a card to be collected from the event in another run.
        [action] == 'Offer', (Only in the Bonfire Spirits event) offers a card. You recieve a reward based on the rarity.'''
        while True:
            if action == "Remove":
                player.deck.remove(card)
            elif action == 'Upgrade':
                pass

    def show_status(self, full_view=False, combat=True):
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
        ansiprint(status)
        print()
        if full_view is True:
            if self.vulnerable > 0:
                print(f"Vulnerable: You take 50% more damage for {self.vulnerable} turns.")
            if self.weak > 0:
                print(f"Weakened: You deal 25% less damage with Attacks for {self.weak} turns.")
            if self.frail > 0:
                print(f"Frail: You gain 25% less Block from cards for {self.frail} turns")
            if self.strength < 0:
                print(f"Strength: You deal {-self.strength} less damage with Attacks.")
            if self.dexterity < 0:
                print(f"Dexterity: You gain {-self.dexterity} less Block from cards.")
            if self.artifact > 0:
                print(f"Artifact: Negate the next {self.artifact} debuffs.")
            if self.strength > 0:
                print(f"Strength: You deal {self.strength} more damage with Attacks.")
            if self.dexterity > 0:
                print(f"Dexterity: You gain {self.dexterity} more Block from cards.")
            if self.barricade is True:
                print("Barricade: Block is not removed at the start of your turn.")

    def end_player_turn(self):
        player.discard_pile.extend(player.hand)
        player.hand = []
        sleep(1.5)
        system("clear")

    def move_card(self, card, move_to, from_location, cost_energy, shuffle=False):
        if cost_energy is True:
            self.energy -= card["Energy"]
        from_location.remove(card)
        if shuffle is True:
            move_to.insert(random.randint(0, len(move_to) - 1), card)
        else:
            move_to.append(card)

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
            elif debuff_name == "Strength(1 turn)":
                target.strength -= amount
                target.shackled += amount
            elif debuff_name == "Strength":
                target.strength -= amount
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
        elif buff_name == 'Strength(Temp)':
            self.strength += amount
            self.strength_down += amount
        if buff_name == 'Strength(Temp)':
            ansiprint(f"+{amount} <light-cyan>Strength</light-cyan>")
            ansiprint(f"+{amount} <light-cyan>Strength Down</light-cyan>")
        else:
            ansiprint(f"+{amount} <light-cyan>{buff_name}</light-cyan>")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)

    def gain_gold(self, gold, dialogue=True):
        self.gold += gold
        if dialogue is True:
            ansiprint(f"{self.name} gained <green>{gold}</green> <yellow>Gold</yellow>")
        sleep(1)

    def start_turn(self):
        print(f"{self.name}:")
        # Start of turn effects
        self.draw_cards(False, 0)
        if self.barricade is False: # Barricade: Block is not remove at the start of your turn
            self.block = 0
        else:
            if self.block > 0 and combat_turn > 1:
                ansiprint("Your Block was not removed because of <light-cyan>Barricade</light-cyan>")
        if self.next_turn_block > 0:
            self.blocking(self.next_turn_block, False)
            self.next_turn_block = 0
        self.energy += self.energy_gain + self.energized
        if self.energized > 0: # Energized: Gain X Energy next turn
            ansiprint(f"You gained {self.energized} extra energy because of <light-cyan>Energized</light-cyan>")
            self.energized = 0
            ansiprint("<light-cyan>Energized wears off.")

        # //////Debuffs\\\\\\
        if self.vulnerable > 0: # Vulnerable: Take 50% more damage from attacks
            self.vulnerable -= 1
            ansiprint("<light-cyan>-1 Vulnerable</light-cyan>")
            if self.vulnerable == 0:
                ansiprint("<green>Vulnerable wears off.</green>")
            sleep(0.8)
        if self.weak > 0: # Weak: Deal 25% less damage with attacks
            self.weak -= 1
            ansiprint("<light-cyan>-1 Weak</light-cyan>")
            if self.weak == 0:
                ansiprint("<green>Weak wears off.</green")
            sleep(0.8)
        if self.frail > 0: # Frail: Gain 25% less block from cards
            self.frail -= 1
            ansiprint("<light-cyan>-1 Frail</light-cyan>")
            if self.frail == 0:
                ansiprint("<green>Frail wears off</green>")
            sleep(0.8)
        if self.strength_down > 0: # Strength Down: Lose X Strength at the end of your turn
            self.strength -= self.strength_down
            ansiprint(f"<red>Strength</red> was reduced by {self.strength_down} because of <red>Strength Down</red>")
            sleep(0.7)
            self.strength_down = 0
            print("Strength Down wears off.")
            sleep(0.8)
        if self.shackled > 0: # Shackled: Regain X Strength at the end of your turn
            self.strength += self.shackled
            ansiprint(f"Regained {self.shackled} Strength because of Shackled")
            sleep(1)
            self.shackled = 0
            print("Shackled wears off")
            sleep(0.8)

        # //////Buffs\\\\\\
        if self.intangible > 0: # Intangible: Reduce ALL damage and HP loss to 1 for X turns
            self.intangible -= 1
            ansiprint("<light-cyan>-1 Intangible</light-cyan>")
            if self.intangible == 0:
                print("Intangible wears off.")
    def end_turn(self):
        if self.regen > 0: # Regen: Heal for X HP at the end of your turn.
            self.ChangeHealth(self.regen, "Heal")
            sleep(0.8)
        if self.regeneration > 0:
            self.ChangeHealth(self.regeneration, False)
        if self.metallicize > 0: # Metallicize: At the end of your turn, gain X Block
            print("Metallicize: ", end='')
            self.blocking(self.metallicize, False)
            sleep(0.8)
        if self.plated_armor > 0: # Plated Armor: At the end of your turn, gain X Block. Decreases by 1 when recieving unblocked attack damage
            print("Plated Armor: ", end='')
            self.blocking(self.plated_armor, False)
            sleep(0.8)
        if self.ritual > 0:
            print("Ritual: ", end='')
            self.buff("Strength", self.ritual, True)

    # def print_list(self, display_type, target_list, combat=True):
    #     counter = 1
    #     if display_type == "Potions":
    #         for potion in target_list:
    #             ansiprint(f"{counter}: <blue>{potion['Name']}</blue> | {potion['Class']} | <light-black>{potion['Rarity']}</light-black> | <yellow>{potion['Info']}</yellow>")
    #             counter += 1
    #             sleep(0.05)
    #     elif display_type == "Relics":
    #         for relic in target_list:
    #             ansiprint(f"{counter}: <blue>{relic['Name']}</blue> | {relic['Class']} |<light-black>{relic['Rarity']}</light-black> | <yellow>{relic['Info']}</yellow>", end='')
    #             if combat is True:
    #                 print("\n")
    #             else:
    #                 ansiprint(f" | <light-blue><italic>{relic['Flavor']}</italic></light-blue>")
    #             counter += 1
    #             sleep(0.05)



class Enemy:
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
    def __init__(self, health: list, block: int, name: str, past_moves: dict):
        self.health = health
        self.max_health = health
        self.block = block
        self.name = name
        if 'louse' in self.name:
            self.damage = [5, 7]
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
        self.curl_up = 0
        if 'louse' in self.name:
            self.curl_up = random.randint(3, 7)
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

    def enemy_turn(self):
        if self.name == "Cultist":
            if self.active_turns == 1:
                self.buff("Ritual", 3, True, True, "Incantation")
            else:
                self.attack(6, 1, True, True, "Dark Strike")
        elif self.name in ('Acid Slime (L)', 'Acid Slime (M)'):
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
        elif self.name == "Jaw Worm":
            random_num = random.randint(0, 100)
            if self.active_turns == 1 or (random_num > 75 and self.past_moves != "Chomp"):
                self.attack(11, 1, True, True, "Chomp")
                self.past_moves.append("Chomp")
            elif random_num < 45 and self.past_moves[-1] != "Bellow":
                self.buff("Strength", 3, True, False, "Bellow")
                self.blocking(6, False, True)
                self.past_moves.append("Bellow")
            elif self.past_moves[-2] != "Thrash":
                self.attack(7, 1, True, False, "Thrash")
                self.blocking(5, False, True)
                self.past_moves.append("Thrash")
        elif 'louse' in self.name.lower():
            random_num = random.randint(0, 100)
            if random_num < 75 and self.past_moves[-2] != "Bite":
                self.attack(self.damage, 1, True, True, "Bite")
                self.past_moves.append("Bite")
            elif self.past_moves[-2] != "Grow" and self.name == "Red Louse":
                self.buff("Strength", 3, True, True, "Grow")
                self.past_moves.append("Grow")
            elif self.past_moves[-2] != "Spit Web" and self.name == "Green Louse":
                self.debuff("Weak", 2, True, True, "Spit Web")
                self.past_moves.append("Spit Web")


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
        for _ in range(times):
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
        for _ in range(amount):
            location.append(status_card)
        print(f"{player.name} gained {amount} {status_card['Name']}({status_card['Info']}) \nPlaced into {location}")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)
    def start_turn(self):
        print(f"{self.name}:")
        if self.barricade is False:
            self.block = 0
        else:
            if self.active_turns > 1 and self.block > 0:
                ansiprint(f"{self.name}'s Block was not removed because of <light-cyan>Barricade</light-cyan")
        if self.vulnerable > 0:
            self.vulnerable -= 1
            ansiprint("<light-cyan>-1 Vulnerable</light-cyan>")
            if self.vulnerable == 0:
                print("Vulnerable wears off.")
        if self.weak > 0:
            self.weak -= 1
            ansiprint("<light-cyan>-1 Weak</light-cyan>")
            if self.weak == 0:
                print("Weak wears off")


# Characters
player = Player(80, 0, 3, [])
cards = {
    # Ironclad cards
    'Strike': {'Name': 'Strike', 'Damage': 6, 'Energy': 1, 'Rarity': 'Basic', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {6 + player.strength} damage', 'Function': player.use_strike},
    'Strike+': {'Name': '<green>Strike+</green>', 'Upgraded': True, 'Damage': 9, 'Energy': 1, 'Rarity': 'Basic', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {9 + player.strength} damage', 'Function': player.use_strike},

    'Defend': {'Name': 'Defend', 'Block': 5, 'Energy': 1, 'Target': 'Yourself', 'Rarity': 'Basic', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.dexterity} <yellow>Block</yellow>', 'Function': player.use_defend},
    'Defend+': {'Name': '<green>Defend+</green>', 'Upgraded': True, 'Block': 8, 'Energy': 1, 'Target': 'Yourself', 'Rarity': 'Basic', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {8 + player.dexterity} <yellow>Block</yellow>', 'Function': player.use_defend},

    'Bash': {'Name': 'Bash', 'Damage': 8, 'Vulnerable': 2, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Basic', 'Class': 'Ironclad', 'Type': 'Attack', 'Info': f'Deal {8 + player.strength} damage. Apply 2 <yellow>Vulnerable</yellow>', 'Function': player.use_bash},
    'Bash+': {'Name': '<green>Bash+</green>', 'Upgraded': True, 'Damage': 10, 'Vulnerable': 3, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Basic', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {10 + player.strength} damage. Apply 3 <yellow>Vulnerable</yellow>', 'Function': player.use_bash},

    'Anger': {'Name': 'Anger', 'Damage': 6, 'Energy': 0, 'Location': player.discard_pile, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {6 + player.strength} damage. Add a copy of this card to your discard pile.', 'Function': player.use_anger},
    'Anger+': {'Name': '<green>Anger+</green>', 'Upgraded': True, 'Damage': 8, 'Energy': 0, 'Location': player.discard_pile, 'Target': 'Single', 'Rarity': 'Common', 'Class': 'Ironclad', 'Type': 'Attack', 'Info': f'Deal {8 + player.strength} damage. Add a copy of this card to your discard pile.', 'Function': player.use_anger},

    'Armaments': {'Name': 'Armaments', 'Block': 5, 'Upgrade Target': 'Single', 'Target': 'Yourself', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.dexterity} <yellow>Block</yellow>. <yellow>Upgrade</yellow> a card in your hand for the rest of combat.'},
    'Armaments+': {'Name': '<green>Armaments+</green>', 'Upgraded': True, 'Block': 5, 'Upgrade Target': 'All', 'Target': 'Yourself', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.dexterity} <yellow>Block</yellow>. <yellow>Upgrade</yellow> ALL cards in your hand for the rest of combat.'},

    'Body Slam': {'Name': 'Body Slam', 'Damage': player.block, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': 'Deal damage equal to your <yellow>Block</yellow>', 'Function': player.use_bodyslam},
    'Body Slam+': {'Name': '<green>Body Slam+</green>', 'Upgraded': True, 'Damage': player.block, 'Energy': 0, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': 'Deal damage equal to your <yellow>Block</yellow>', 'Function': player.use_bodyslam},

    'Clash': {'Name': 'Clash', 'Damage': 14, 'Energy': 0, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Can only be played is every card in your hand is an Attack. Deal {14 + player.strength} damage.', 'Function': player.use_clash},
    'Clash+': {'Name': '<green>Clash+</green>', 'Upgraded': True, 'Damage': 18, 'Energy': 0, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Can only be played if every card in your hand is an Attack. Deal {18 + player.strength} damage.', 'Function': player.use_clash},

    'Cleave': {'Name': 'Cleave', 'Damage': 8, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {8 + player.strength} damage to ALL enemies', 'Function': player.use_cleave},
    'Cleave+': {'Name': '<green>Cleave+</green>', 'Upgraded': True, 'Damage': 11, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {11 + player.strength} damage to ALL enemies', 'Function': player.use_cleave},

    'Clothesline': {'Name': 'Clothesline', 'Energy': 2, 'Damage': 12, 'Weak': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {12 + player.strength} damage. Apply 2 <yellow>Weak</yellow>', 'Function': player.use_clothesline},
    'Clothesline+': {'Name': '<green>Clothesline+</green>', 'Upgraded': True, 'Energy': 2, 'Damage': 14, 'Weak': 3, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {14 + player.strength} damage. Apply 3 <yellow>Weak</yellow>', 'Function': player.use_clothesline},

    'Flex': {'Name': 'Flex', 'Strength': 2, 'Strength Down': 2, 'Energy': 0, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Gain 2 <yellow>Strength</yellow>. At the end of your turn, lose 2 <yellow>Strength</yellow>'},
    'Flex+': {'Name': '<green>Flex+</green>', 'Upgraded': True, 'Strength': 4, 'Strength Down': 4, 'Energy': 0, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Gain 4 <yellow>Strength</yellow>. At the end of your turn lose 4 <yellow>Strength</yellow>', 'Function': player.use_flex},

    'Havoc': {'Name': 'Havoc', 'Energy': 1, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Play the top card of your draw pile and <yellow>Exhaust</yellow> it.', 'Function': player.use_havoc},
    'Havoc+': {'Name': '<green>Havoc+</green>', 'Upgraded': True, 'Energy': 0, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Play the top card of your draw pile and <yellow>Exhaust</yellow> it.', 'Function': player.use_havoc},

    'Headbutt': {'Name': 'Headbutt', 'Damage': 9, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {9 + player.strength} damage. Place a card from your discard pile on top of your draw pile.', 'Function': player.use_headbutt},
    'Headbutt+': {'Name': '<green>Headbutt+</green>', 'Upgraded': True, 'Damage': 12, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {12 + player.strength} damage. Place a card from your discard pile on top of your draw pile.', 'Function': player.use_headbutt},

    'Heavy Blade': {'Name': 'Heavy Blade', 'Damage': 14, 'Strength Multi': 3, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {14 + player.strength} damage. <yellow>Strength</yellow> affects this card 3 times.', 'Function': player.use_heavyblade},
    'Heavy Blade+': {'Name': '<green>Heavy Blade+</green>', 'Upgraded': True, 'Damage': 14, 'Strength Multi': 5, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {14 + player.strength} damage. <yellow>Strength</yellow> affects this card 5 times', 'Function': player.use_heavyblade},

    'Iron Wave': {'Name': 'Iron Wave', 'Damage': 5, 'Block': 5, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.dexterity} <yellow>Block</yellow>. Deal {5 + player.strength} damage.', 'Function': player.use_ironwave},
    'Iron Wave+': {'Name': '<green>Iron Wave+</green>', 'Upgraded': True, 'Damage': 7, 'Block': 7, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Gain {7 + player.dexterity} <yellow>Block</yellow>. Deal {7 + player.strength} damage.', 'Function': player.use_ironwave},

    'Perfected Strike': {'Name': 'Perfected Strike', 'Damage': 6, 'Damage Per "Strike"': 2, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 
                         'Info': f'Deal {6 + player.strength + len([card for card in player.deck if "strike" in card.get("Name").lower()]) * 2} damage. Deals 2 additional damage for ALL your cards containing "Strike".', 'Function': player.use_perfectedstrike},
    'Perfected Strike+': {'Name': '<green>Perfected Strike+</green>', 'Upgraded': True, 'Damage': 6, 'Damage Per "Strike"': 3, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 
                          'Info': f'Deal {6 + player.strength + len([card for card in player.deck if "strike" in card.get("Name").lower()]) * 3} damage. Deals 3 additional damage for ALL your cards containing "Strike".', 'Function': player.use_perfectedstrike},

    'Pommel Strike': {'Name': 'Pommel Strike', 'Damage': 9, 'Cards': 2, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {9 + player.strength} damage. Draw 1 card.', 'Function': player.use_pommelstrike},
    'Pommel Strike+': {'Name': '<green>Pommel Strike+</green>', 'Upgraded': True, 'Damage': 10, 'Cards': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {10 + player.strength} damage. Draw 2 cards.', 'Function': player.use_pommelstrike},

    'Shrug it Off': {'Name': 'Shrug it Off', 'Block': 8, 'Cards': 1, 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {8 + player.dexterity} <yellow>Block</yellow>. Draw 1 card.', 'Function': player.use_shrugitoff},
    'Shrug it Off+': {'Name': '<green>Shrug it Off+</green>', 'Upgraded': True, 'Block': 11, 'Cards': 1, 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {11 + player.dexterity} <yellow>Block</yellow>. Draw 1 card.', 'Function': player.use_shrugitoff},

    'Sword Boomerang': {'Name': 'Sword Boomerang', 'Damage': 3, 'Times': 3, 'Target': 'Random', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {3 + player.strength} damage to a random enemy 3 times.', 'Function': player.use_swordboomerang},
    'Sword Boomerang+': {'Name': '<green>Sword Boomerang+</green>', 'Upgraded': True, 'Damage': 3, 'Times': 4, 'Target': 'Random', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {3 + player.strength} damage to a random enemy 4 times.', 'Function': player.use_swordboomerang},

    'Thunderclap': {'Name': 'Thunderclap', 'Damage': 4, 'Vulnerable': 1, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {4 + player.strength} damage and apply 1 <yellow>Vulnerable</yellow> to ALL enemies.', 'Function': player.use_thunderclap},
    'Thunderclap+': {'Name': '<green>Thunderclap+</green>', 'Upgraded': True, 'Damage': 7, 'Vulnerable': 1, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {7 + player.strength} damage and apply 1 <yellow>Vulnerable</yellow> to ALL enemies.', 'Function': player.use_thunderclap},

    # Status cards
    'Slimed': {'Name': 'Slimed', 'Energy': 1, 'Target': 'Nothing', 'Rarity': 'Common', 'Type': 'Status', 'Info': '<yellow>Exhaust</yellow>'},
    'Burn': {'Name': 'Burn', 'Playable': False, 'Energy': 'Unplayable', 'Damage': 2, 'Rarity': 'Common', 'Type': 'Status', 'Info': '<yellow>Unplayable.</yellow> At the end of your turn, take 2 damage.'},
    'Burn+': {'Name': '<green>Burn+</green>', 'Upgraded': True, 'Playable': False, 'Energy': 'Unplayable', 'Damage': 4, 'Rarity': 'Common', 'Type': 'Status', 'Info': '<yellow>Unplayable.</yellow> At the end of your turn, take 4 damage.'},
    'Dazed': {'Name': 'Dazed', 'Playable': False, 'Ethereal': True, 'Energy': 'Unplayable', 'Rarity': 'Common', 'Type': 'Status', 'Info': '<yellow>Unplayable. Ethereal.</yellow>'},
    'Wound': {'Name': 'Wound', 'Playable': False, 'Rarity': 'Common', 'Type': 'Status', 'Info': '<yellow>Unplayable.</yellow>'},
    'Void': {'Name': 'Void', 'Playable': False, 'Ethereal': True, 'Energy Loss': 1, 'Rarity': 'Common', 'Type': 'Status', 'Info': '<yellow>Unplayable. Ethereal.</yellow> When this card is drawn, lose 1 Energy.'},

    # Curses
    'Regret': {'Name': 'Regret', 'Playable': False, 'Damage': len(player.hand), 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable</yellow>. At the end of your turn, lose 1 HP for each card in your hand.'},
    "Ascender's Bane": {'Name': "Ascender's Bane", 'Playable': False, 'Ethereal': True, 'Removable': False, 'Energy': 'Unplayable', 'Rarity': 'Special', 'Type': 'Curse', 'Info': '<yellow>Unplayable. Ethereal.</yellow> Cannot be removed from your deck'},
    'Clumsy': {'Name': 'Clumsy', 'Playable': False, 'Ethereal': True, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable. Ethereal.</yellow>'},
    'Curse of the Bell': {'Name': 'Curse of the Bell', 'Playable': False, 'Removable': False, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.</yellow> Cannot be removed from your deck.'},
    'Decay': {'Name': 'Decay', 'Playable': False, 'Damage': 2, 'Type': 'Curse', 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Info': '<yellow>Unplayable.</yellow> At the end of your turn, take 2 damage.'},
    'Doubt': {'Name': 'Doubt', 'Playable': False, 'Weak': 1, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.</yellow> At the end of your turn, gain 1 <yellow>Weak</yellow>.'},
    'Injury': {'Name': 'Injury', 'Playable': False, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.</yellow>'},
    'Necronomicurse': {'Name': 'Necronomicurse', 'Playable': False, 'Energy': 'Unplayable', 'Exhaustable': False, 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.</yellow> There is no escape from this <yellow>Curse</yellow>.'},
    'Normality': {'Name': 'Normality', 'Playable': False, 'Cards Limit': 3, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.</yellow> You cannot play more than 3 cards this turn.'},
    'Pain': {'Name': 'Pain', 'Playable': False, 'Damage': 1, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.<yellow> While in hand, lose 1 HP when other cards are played.'},
    'Parasite': {'Name': 'Parasite', 'Playable': False, 'Max Hp Loss': 3, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.</yellow> If transformed or removed from your deck, lose 3 Max HP.'},
    'Pride': {'Name': 'Pride', 'Innate': True, 'Exhaust': True, 'Energy': 1, 'Location': player.draw_pile, 'Rarity': 'Special', 'Type': 'Curse', 'Info': '<yellow>Innate.</yellow> At the end of your turn, put a copy of this card on top of your draw pile. <yellow>Exhaust.</yellow>'},
    'Shame': {'Name': 'Shame', 'Playable': False, 'Frail': 1, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable.</yellow> At the end of your turn, gain 1 <yellow>Frail</yellow>.'},
    'Writhe': {'Name': 'Writhe', 'Playable': False, 'Innate': True, 'Energy': 'Unplayable', 'Rarity': 'Curse', 'Type': 'Curse', 'Info': '<yellow>Unplayable. Innate.</yellow>'}
}
potions = {
    # Common | All Classes
    'Attack Potion': {'Name': 'Attack Potion', 'Cards': 1, 'CardTtype': 'Attack', 'Class': 'All', 'Rarity': 'Common', 'Info': 'Add 1 of 3 random Attack cards to your hand, it costs 0 this turn'},
    'Power Potion': {'Name': 'Power Potion', 'Cards': 1, 'Card Type': 'Power', 'Class': 'All', 'Rarity': 'Common', 'Info': 'Add 1 of 3 random Power cards to your hand, it costs 0 this turn'},
    'Skill Potion': {'Name': 'Skill Potion', 'Cards': 1, 'Card Type': 'Skill', 'Class': 'All', 'Rarity': 'Common', 'Info': 'Add 1 of 3 random Skill cards to your hand, it costs 0 this turn'},
    'Colorless Potion': {'Name': 'Colorless Potion', 'Cards': 1, 'Card Type': 'Colorless', 'Class': 'All', 'Rarity': 'Common', 'Info': 'Choose 1 of 3 random Colorless cards to add to your hand, it costs 0 this turn'},
    'Block Potion': {'Name': 'Block Potion', 'Block': 12, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Gain 12 Block'},
    'Dexterity Potion': {'Name': 'Dexterity Potion', 'Dexterity': 2, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Gain 2 Dexterity'},
    'Energy Potion': {'Name': 'Energy Potion', 'Energy': 2, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Gain 2 Energy'},
    'Explosive Potion': {'Name': 'Explosive Potion', 'Damage': 10, 'Target': 'All', 'Class': 'All', 'Rarity': 'Common', 'Info': 'Deal 10 damage to ALL enemies'},
    'Fear Potion': {'Name': 'Fear Potion', 'Vulnerable': 3, 'Target': 'Enemy', 'Class': 'All', 'Rarity': 'Common', 'Info': 'Apply 3 Vulnerable'},
    'Fire Potion': {'Name': 'Fire Potion', 'Damage': 20, 'Target': 'Enemy', 'Class': 'All', 'Rarity': 'Common', 'Info': 'Deal 20 damage to target enemy'},
    'Flex Potion': {'Name': 'Flex Potion', 'Strength': 5, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Gain 5 Strength. At the end of your turn lose 5 Strength'},
    'Speed Potion': {'Name': 'Speed Potion', 'Dexterity': 5, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Gain 5 Dexterity. At the end of your turn, lose 5 Dexterity'},
    'Strength Potion': {'Name': 'Strength Potion', 'Strength': 2, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Gain 2 Strength'},
    'Swift Potion': {'Name': 'Swift Potion', 'Cards': 3, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Draw 3 cards'},
    # Uncommon | All Classes
    'Ancient Potion': {'Name': 'Ancient Potion', 'Artifact': 1, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'Gain 1 Artifact'},
    'Distilled Chaos': {'Name': 'Distilled Chaos', 'Cards': 3, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'Play the top 3 cards of your draw pile'},
    'Duplication Potion': {'Name': 'Duplication Potion', 'Cards': 1, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'This turn, the next card is played twice.'},
    'Essence of Steel': {'Name': 'Essence of Steel', 'Plated Armor': 4, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'Gain 4 Plated Armor'},
    "Gambler's Brew": {'Name': "Gambler's Brew", 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'Discard any number of cards, then draw that many'},
    'Liquid Bronze': {'Name': 'Liquid Bronze', 'Thorns': 3, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'Gain 3 Thorns'},
    'Liquid Memories': {'Name': 'Liquid Memories', 'Cards': 1, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'Choose a card in your discard pile and return it to your hand. It costs 0 this turn'},
    'Regen Potion': {'Name': 'Regen Potion', 'Regen': 5, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Gain 5 Regeneration'},
    # Rare | All Classes
    'Cultist Potion': {'Name': 'Cultist Potion', 'Ritual': 1, 'Class': 'All', 'Rarity': 'Rare', 'Info': 'Gain 1 Ritual'},
    'Entropic Brew': {'Name': 'Entropic Brew', 'Potions': player.potion_bag - len(player.potions), 'Class': 'All', 'Rarity': 'Rare', 'Info': 'Fill all your empty potion slots with random potions'},
    'Fairy in a Bottle': {'Name': 'Fairy in a Bottle', 'Playable': False, 'Health': 30, 'Class': 'All', 'Rarity': 'Rare', 'Info': f'When you would die, heal to 30 percent of your Max HP({math.floor(player.max_health * 0.30)}) instead and discard this potion'},
    'Fruit Juice': {'Name': 'Fruit Juice', 'Playable Everywhere?': True, 'Max Health': 5, 'Class': 'All', 'Rarity': 'Rare', 'Info': 'Gain 5 Max HP'},
    'Smoke Bomb': {'Name': 'Smoke Bomb', 'Escape from boss': False, 'Target': 'Nothing', 'Class': 'All', 'Rarity': 'Rare', 'Info': 'Escape from a non-boss combat. You recieve no rewards.'},
    'Sneko Oil': {'Name': 'Snecko Oil', 'Cards': 5, 'Range': (0, player.max_energy), 'Class': 'All', 'Rarity': 'Rare', 'Info': 'Draw 5 cards. Randomized the costs of all cards in your hand for the rest of combat.'},
    # Ironclad Potions                       (In percent)
    'Blood Potion': {'Name': 'Blood Potion', 'Health': 20, 'Class': '<red>Ironclad</red>', 'Rarity': 'Uncommon', 'Info': f'Heal for 20 percent of your Max HP({math.floor(player.max_health * 0.20)})'},
    'Elixir': {'Name': 'Elixir', 'Class': '<red>Ironclad</red>', 'Rarity': 'Uncommon', 'Info': 'Exhaust any number of cards in your hand'},
    'Heart of Iron': {'Name': 'Heart of Iron', 'Metallicize': 8, 'Class': '<red>Ironclad</red>', 'Rarity': 'Rare', 'Info': 'Gain 8 <light-cyan>Metallicize</light-cyan>'},
    # Silent potion
    'Poison Potion': {'Name': 'Poison Potion', 'Poison': 6, 'Target': 'Enemy', 'Class': '<light-green>Silent</light-green>', 'Rarity': 'Common', 'Info': 'Apply 6 Poison to target enemy'},
    'Cunning Potion': {'Name': 'Cunning Potion', 'Shivs': 3, 'Card': 'placehold', 'Class': '<light-green>Silent</light-green>', 'Rarity': 'Uncommon', 'Info': 'Add 3 Upgraded Shivs to your hand'}, # Shiv card doesn't not exist yet
    'Ghost in a Jar': {'Name': 'Ghost in a Jar', 'Intangible': 1, 'Class': '<light-green>Silent</light-green>', 'Rarity': 'Rare', 'Info': 'Gain 1 Intangible'},
    # Defect Potions
    'Focus Potion': {'Name': 'Focus Potion', 'Focus': 2, 'Class': '<blue>Defect</blue>', 'Rarity': 'Common', 'Info': 'Gain 2 Focus'},
    'Potion of Capacity': {'Name': 'Potion of Capacity', 'Orb Slots': 2, 'Class': '<blue>Defect</blue>', 'Rarity': 'Uncommon', 'Info': 'Gain 2 Orb slots'},
    'Essence of Darkness': {'Name': 'Essence of Darkness', 'Dark': player.orb_slots, 'Class': '<blue>Defect</blue>', 'Rarity': 'Rare', 'Info': 'Channel 1 Dark for each orb slot'},
    # Watcher Potions
    'Bottled Miracle': {'Name': 'Bottled Miracle', 'Miracles': 2, 'Card': 'placehold', 'Class': '<magenta>Watcher</magenta>', 'Rarity': 'Common', 'Info': 'Add 2 Miracles to your hand'},
    'Stance Potion': {'Name': 'Stance Potion', 'Stances': ['Calm', 'Wrath'], 'Class': '<magenta>Watcher</magenta>', 'Rarity': 'Uncommon', 'Info': 'Enter Calm or Wrath'},
    'Ambrosia': {'Name': 'Ambrosia', 'Stance': 'Divinity', 'Class': '<magenta>Watcher</magenta>', 'Rarity': 'Rare', 'Info': 'Enter Divinity Stance'}
}
relics = {
    # Starter Relics
    'Burning Blood': {'Name': 'Burning Blood', 'Class': 'Ironclad', 'Rarity': 'Starter', 'Health': 6, 'Info': 'At the end of combat, heal 6 HP', 'Flavor': "Your body's own blood burns with an undying rage."},
    'Ring of the Snake': {'Name': 'Ring of the Snake', 'Class': 'Silent', 'Rarity': 'Starter', 'Cards': 2, 'Info': 'At the start of each combat, draw 2 additional cards.', 'Flavor': 'Made from a fossilized snake, represents great skill as a huntress.'},
    'Cracked Core': {'Name': 'Cracked Core', 'Class': 'Defect', 'Rarity': 'Starter', 'Lightning': 1, 'Info': 'At the start of each combat, Channel 1 Lightning orb.', 'Flavor': 'The mysterious life force which powers the Automatons within the Spire. It appears to be cracked.'},
    'Pure Water': {'Name': 'Pure Water', 'Class': 'Watcher', 'Rarity': 'Starter', 'Miracles': 1, 'Card': 'placehold', 'Info': 'At the start of each combat, add 1 Miracle card to your hand.', 'Flavor': 'Filtered through fine sand and free of impurities.'},
    # Common Relics
    'Akabeko': {'Name': 'Akabeko', 'Class': 'Any', 'Rarity': 'Common', 'Extra Damage': 8, 'Info': 'Your first Attack each combat deals 8 additional damage.', 'Flavor': 'Muuu~'},
    'Anchor': {'Name': 'Anchor', 'Class': 'Any', 'Rarity': 'Common', 'Block': 10, 'Info': 'At the start of combat, gain 10 Block.', 'Flavor': 'Holding this miniature trinket, your feel heavier and more stable.'},
    'Ancient Tea Set': {'Name': 'Ancient Tea Set', 'Class': 'Any', 'Rarity': 'Common', 'Energy': 2, 'Info': 'Whenever you enter a Rest Site, start the next combat with 2 additional energy.', 'Flavor': "The key to a refreshing night's rest."},
    'Art of War': {'Name': 'Art of War', 'Class': 'Any', 'Rarity': 'Common', 'Energy': 1, 'Info': 'If you do not play Attacks during your turn, gain an extra Energy next turn.', 'Flavor': 'The ancient manuscript contains wisdom from a past age.'},
    'Bag of Marbles': {'Name': 'Bag of Marbles', 'Class': 'Any', 'Rarity': 'Common', 'Target': 'All', 'Vulnerable': 1, 'Info': 'At the start of each combat, apply 1 <yellow>Vulnerable</yellow> to ALL enemies.', 'Flavor': 'A once popular toy in the city. Useful for throwing enemies off balance.'},
    'Bag of Preparation': {'Name': 'Bag of Preparation', 'Class': 'Any', 'Rarity': 'Common', 'Cards': 2, 'Info': 'At the start of each combat, draw 2 additional cards.', 'Flavor': "Oversized adventurer's pack. Has many pockets and straps."},
    'Blood Vial': {'Name': 'Blood Vial', 'Class': 'Any', 'Rarity': 'Common', 'HP': 2, 'Info': 'At the start of each combat, heal 2 HP.', 'Flavor': 'A vial containing the blood of a pure and elder vampire.'},
    'Bronze Scales': {'Name': 'Bronze Scales', 'Class': 'Any', 'Rarity': 'Common', 'Thorns': 3, 'Info': 'Whenever you take damage, deal 3 damage back.', 'Flavor': 'The sharp scales of the Guardian. Rearranges itself to protect its user.'},
    'Centennial Puzzle': {'Name': 'Centennial Puzzle', 'Class': 'Any', 'Rarity': 'Common', 'Cards': 3, 'Info': 'The first time you lose HP each combat, draw 3 cards.', 'Flavor': 'Upon solving the puzzle you feel a powerful warmth in your chest.'},
    'Ceramic Fish': {'Name': 'Ceramic Fish', 'Class': 'Any', 'Rarity': 'Common', 'Gold': 9, 'Info': 'Whenever you add a card to your deck, gain 9 Gold.', 'Flavor': 'Meticulously painted, these fish were revered to bring great fortune.'},
    'Dream Catcher': {'Name': 'Dream Catcher', 'Class': 'Any', 'Rarity': 'Common', 'Info': 'Whenever you rest, you may add a card to your deck.', 'Flavor': 'The northern tribes would often use dream catchers at night, believing they led to self improvement.'},
    'Happy Flower': {'Name': 'Happy Flower', 'Class': 'Any', 'Rarity': 'Common', 'Energy': 1, 'Info': 'Every 3 turns, gain 1 Energy.', 'Flavor': 'This unceasing joyous plant is a popular novelty item among nobles.'},
    'Juzu Bracelet': {'Name': 'Juzu Bracelet', 'Class': 'Any', 'Rarity': 'Common', 'Info': 'Regular enemy combats are no longer encountered in ?(Unknown) rooms.', 'Flavor': 'A ward against the unknown.'},
    'Lantern': {'Name': 'Lantern', 'Class': 'Any', 'Rarity': 'Common', 'Energy': 1, 'Info': 'Gain 1 Energy on the first turn of each combat.', 'Flavor': 'An eerie lantern which illuminates only for the user.'},
    'Max Bank': {'Name': 'Maw Bank', 'Class': 'Any', 'Rarity': 'Common', 'Gold': 12, 'Info': 'Whenever you climb a floor, gain 12 Gold. No longer works when you spend any gold at the shop.', 'Flavor': 'Suprisingly popular, despite maw attacks being a common occurence.'},
    'Meal Ticket': {'Name': 'Meal Ticket', 'Class': 'Any', 'Rarity': 'Common', 'Health': 15, 'Info': 'Whenever you enter a shop, heal 15 HP.', 'Flavor': 'Complementary meatballs with every visit!'},
    'Nunchaku': {'Name': 'Nunchaku', 'Class': 'Any', 'Rarity': 'Common', 'Energy': 1, 'Info': 'Every time you play 10 attacks, gain 1 Energy', 'Flavor': 'A good training tool. Inproves the posture and agility of the user.'},
    'Oddly Smooth Stone': {'Name': 'Oddly Smooth Stone', 'Class': 'Any', 'Rarity': 'Common', 'Dexterity': 1, 'Info': 'At the start of each combat, gain 1 Dexterity.', 'Flavor': 'You have never seen smething so smooth and pristine. This must be the work of the Ancients.'},
    'Omamori': {'Name': 'Omamori', 'Class': 'Any', 'Rarity': 'Common', 'Curses': 2, 'Info': 'Negate the next 2 Curses you obtain.', 'Flavor': 'A common charm for staving off vile spirits. This one seems to possess a spark of divine energy.'},
    'Orichaicum': {'Name': 'Orichaicum', 'Class': 'Any', 'Rarity': 'Common', 'Block': 6, 'Info': 'If you end your turn without Block, gain 6 Block.', 'Flavor': 'A green tinted metal from an unknown origin.'},
    'Pen Nib': {'Name': 'Pen Nib', 'Class': 'Any', 'Rarity': 'Common', 'Attacks': 10, 'Info': 'Every 10th attack you play deals double damage.', 'Flavor': 'Holding the nib, you can see everyone ever slain by a previous owner of the pen. A violent history.'},
    'Potion Belt': {'Name': 'Potion Belt', "Class": 'Any', 'Rarity': 'Common', 'Potion Slots': 2, 'Info': 'Upon pickup, gain 2 potion slots.', 'Flavor': 'I can hold more potions using this belt!'},
    'Preserved Insect': {'Name': 'Preserved Insect', 'Class': 'Any', 'Rarity': 'Common', 'Hp Percent Loss': 25, 'Info': 'Enemies in Elite rooms have 20% less health.', 'Flavor': 'The insect seems to create a shrinking aura that targets particularly large enemies.'},
    'Regal Pillow': {'Name': 'Regal Pillow', 'Class': 'Any', 'Rarity': 'Common', '+Rest HP': 15, 'Info': 'Heal an additional 15 HP when you Rest.', 'Flavor': "Now you can get a proper night's rest."},
    'Smiling Mask': {'Name': 'Smiling Mask', 'Class': 'Any', 'Rarity': 'Common', 'Info': "The merchant's card removal service now always costs 50 Gold.", 'Flavor': 'Mask worn by the merchant. He must have spares...'},
    'Strawberry': {'Name': 'Strawberry', 'Class': 'Any', 'Rarity': 'Common', 'Max HP': 7, 'Flavor': "'Delicious! Haven't seen any of these since the blight.' - Ranwid"},
    'The Boot': {'Name': 'The Boot', 'Class': 'Any', 'Rarity': 'Common', 'Info': 'When you would deal 4 or less unblocked Attack damage, increase it to 5.', 'Flavor': 'When wound up, the boot grows larger in size.'},
    'Tiny Chest': {'Name': 'Tiny Chest', 'Class': 'Any', 'Rarity': 'Common', 'Info': 'Every 4th <bold>?</bold> room is a <bold>Treasure</bold> room.', 'Flavor': '"A fine prototype." - The Architect'}
}
player.deck = [cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Bash']]
# Enemies
encounters = [[Enemy([48, 54], 0, "Cultist", ['place', 'place', 'place'])], [Enemy([40, 44], 0, "Jaw Worm", ['place', 'place', 'place'])]]
