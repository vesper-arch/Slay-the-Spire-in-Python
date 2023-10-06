import math
import sys
import random
from time import sleep
from os import system
from ansimarkup import ansiprint

from utility import damage, active_enemies, combat_turn, list_input, remove_color_tags, duration_effects, player_buffs, player_debuffs, enemy_buffs, enemy_debuffs, non_stacking_effects, all_effects


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
    max_potions: The max amount of potions the player can have
    """

    def __init__(self, health: int, block: int, max_energy: int, deck: list):
        self.health: int = health
        self.block: int = block
        self.name: str = "Ironclad"
        self.player_class: str = "Ironclad"
        self.max_health: int = health
        self.energy: int = 0
        self.max_energy: int = max_energy
        self.energy_gain: int = max_energy
        self.deck: list[dict] = deck
        self.potions: list[dict] = []
        self.relics: list[dict] = []
        self.max_potions: int = 3
        self.hand: list[dict] = []
        self.draw_pile: list[dict] = []
        self.discard_pile: list[dict] = []
        self.card_reward_choices: int = 3
        self.draw_strength: int = 5
        self.exhaust_pile: list[dict] = []
        self.orbs = []
        self.orb_slots: int = 3
        self.gold: int = 0
        self.debuffs: dict[str: int] = {}
        for debuff in player_debuffs:
            if debuff not in non_stacking_effects:
                self.debuffs[debuff] = 0
            else:
                self.debuffs[debuff] = False
        self.buffs: dict[str: int] = {}
        for buff in player_buffs:
            if debuff not in non_stacking_effects:
                self.buffs[buff] = 0
            else:
                self.buffs[buff] = False
        # Alternate debuff/buff effects
        self.combusts_played = 0
        self.the_bomb_countdown = 3
        # Relic buffs
        self.pen_nib_attacks: int = 0
        self.ancient_tea_set: bool = False
        self.attacks_played_this_turn: bool = False # Used for the Art of War relic
        self.taken_damage: bool = False # Used for the Centennial Puzzle relic
        self.gold_on_card_add: bool = False # Used for the Ceramic Fish relic
        self.happy_flower: int = 0
        self.block_curses: int = 0 # Used for the Omamori relic
        self.nunckaku_attacks: int = 0
        self.starting_strength: int = 0 # Used for the Red Skull and Vajra relic
        self.golden_bark: bool = False # Used for the Golden Bark relic

    def use_card(self, card: dict, target: object, exhaust, pile) -> None:
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
        if card.get('Type') == 'Attack' and relics['Pen Nib'] in self.relics:
            self.pen_nib_attacks += 1
        if card.get('Type') == 'Attack' and relics['Nunchaku'] in self.relics:
            self.nunckaku_attacks += 1
            if self.nunckaku_attacks == 10:
                self.energy += 1
                ansiprint('You gained 1 Energy from <bold>Nunckaku</bold>.')
                self.nunckaku_attacks = 0

        if card.get('Type') == 'Status' and relics['Medical Kit'] in player.relics: # Medical Kit allows Status cards to played
            exhaust = True
        elif card.get('Type') == 'Curse' and relics['Blue Candle'] in player.relics:
            damage(1, self, self)
        if exhaust is True or card.get('Exhaust') is True:
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
                if not card.get("Type"):
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
        strength_multi = cards['Heavy Blade']['Strength Multi']
        if '+' in using_card['Name']:
            strength_multi += 2
        damage(using_card['Damage'] * strength_multi, targeted_enemy, self)
        sleep(1.5)
        system("clear")

    def use_cleave(self, enemies, using_card):
        '''Deal 8(11) damage to ALL enemies.'''
        base_damage = using_card['Damage'] # 8
        if "+" in using_card['Name']:
            base_damage += 3
        print()
        for enemy in enemies:
            damage(base_damage, enemy, self)
        sleep(1.5)
        system("clear")

    def use_perfectedstrike(self, targeted_enemy, using_card):
        '''Deal 6 damage. Deals 2(3) additional damage for ALL your cards containing "Strike"'''
        damage_per_strike = using_card['Damage Per "Strike"'] # 2
        base_damage = using_card['Damage'] # 6
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
        base_damage = using_card['Damage'] # 6
        if '+' in using_card['Name']:
            base_damage += 2
        print()
        damage(base_damage, targeted_enemy, self)
        self.discard_pile.append(using_card)
        sleep(1.5)
        system("clear")

    def use_clothesline(self, targeted_enemy, using_card):
        '''Deal 12(14) damage. Apply 2(3) Weak'''
        base_damage = using_card['Damage'] # 12
        base_weak = using_card['Weak'] # 2
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
        base_energy = using_card['Energy'] # 1
        if '+' in using_card['Name']:
            base_energy -= 1
        print()
        self.use_card(self.draw_pile[-1], random.choice(active_enemies), True, self.draw_pile)
        sleep(1.5)
        system("clear")

    def use_flex(self, using_card):
        '''Gain 2(4) Strength. At the end of your turn, lose 2(4) Strength'''
        base_temp_strength = 2 # Using a literal because it has 2 values
        if '+' in using_card['Name']:
            base_temp_strength += 2
        self.buff("Strength(Temp)", base_temp_strength, True)

    def use_headbutt(self, targeted_enemy, using_card):
        '''Deal 9(12) damage. Put a card from your discard pile on top of your draw pile.'''
        base_damage = using_card['Damage'] # 9
        if '+' in using_card['Name']:
            base_damage += 3
        counter = 1
        damage(base_damage, targeted_enemy, self)
        while True:
            for card in self.discard_pile:
                ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                counter += 1
                sleep(0.05)
            choice = list_input('What card do you want to put on top of your draw pile? > ', self.discard_pile)
            if choice is False:
                system("clear")
                continue
            self.move_card(self.discard_pile[choice], self.discard_pile, self.draw_pile, True)
            break
        sleep(1.5)
        system("clear")

    def use_shrugitoff(self, using_card):
        '''Gain 8(11) Block. Draw 1 card.'''
        base_block = using_card['Block'] # 8
        if '+' in using_card['Name']:
            base_block += 3
        self.blocking(base_block)
        self.draw_cards(True, 1)
        sleep(1.5)
        system("clear")

    def use_swordboomerang(self, enemies, using_card):
        '''Deal 3 damage to a random enemy 3(4) times.'''
        base_times = using_card['Times'] # 3
        if '+' in using_card['Name']:
            base_times += 1
        for _ in range(base_times):
            damage(using_card['Damage'], random.choice(enemies), self)
        sleep(1.5)
        system("clear")

    def use_thunderclap(self, enemies, using_card):
        '''Deal 4(7) damage and apply 1 Vulnerable to ALL enemies.'''
        base_damage = using_card['Damage'] # 4
        if '+' in using_card['Name']:
            base_damage += 3
        for enemy in enemies:
            damage(base_damage, enemy, self)
            self.debuff("Vulnerable", 1, enemy, True)
        sleep(0.5)
        system("clear")

    def use_ironwave(self, targeted_enemy, using_card):
        '''Gain 5(7) Block. Deal 5(7) damage.'''
        base_block = using_card['Block'] # 5
        base_damage = using_card['Damage'] # 5
        if '+' in using_card['Name']:
            base_block += 2
            base_damage += 2
        damage(base_damage, targeted_enemy, self)
        self.blocking(base_block)
        sleep(1.5)
        system("clear")

    def use_pommelstrike(self, targeted_enemy, using_card):
        '''Deal 9(10) damage. Draw 1(2) cards.'''
        base_damage = using_card['Damage'] # 9
        base_cards = using_card['Cards'] # 1
        if '+' in using_card['Name']:
            base_damage += 1
            base_cards += 1
        damage(base_damage, targeted_enemy, self)
        self.draw_cards(True, base_cards)
        sleep(1.5)
        system("clear")

    def draw_cards(self, middle_of_turn: bool, draw_cards: int):
        '''Draws [draw_cards] cards.'''
        if draw_cards == 0:
            draw_cards = self.draw_strength
        while True:
            if self.debuffs["No Draw"] is True:
                print("You can't draw any more cards")
                break
            if middle_of_turn is False:
                draw_cards += self.buffs["Draw Up"]
                if relics['Bag of Preparation'] in self.relics:
                    draw_cards += 2
                if relics['Ring of the Snake'] in self.relics:
                    draw_cards += 2
            if len(player.draw_pile) < draw_cards:
                player.draw_pile.extend(random.sample(player.discard_pile, len(player.discard_pile)))
                player.discard_pile = []
                ansiprint("<bold>Discard pile shuffled into draw pile.</bold>")
            player.hand.extend(player.draw_pile[-draw_cards:])
            # Removes those cards
            player.draw_pile = player.draw_pile[:-draw_cards]
            print(f"{self.name} drew {draw_cards} cards.")
            break

    def blocking(self, block: int, card: bool=True):
        '''Gains [block] Block. Cards are affected by Dexterity and Frail.'''
        block_affected_by = ''
        if card:
            block += self.buffs["Dexterity"]
            if self.buffs["Dexterity"] > 0:
                block_affected_by += f'{self.buffs["Dexterity"]} <light-cyan>Dexterity</light-cyan> | '
        if self.buffs["Frail"] > 0 and card:
            block = math.floor(block * 0.75)
            block_affected_by += '<light-cyan>Frail</light-cyan> (x0.75 block) | '
        self.block += block
        ansiprint(f'{self.name} gained {block} <blue>Block</blue>')
        print('Affected by:')
        ansiprint(block_affected_by)

    def health_actions(self, heal: int, heal_type: str):
        '''If [heal_type] is 'Heal', you heal for [heal] HP. If [heal_type] is 'Max Health', increase your max health by [heal].'''
        if heal_type == "Heal":
            self.health += heal
            self.health = min(self.health, self.max_health)
            ansiprint(f"You heal <green>{min(self.max_health - self.health, heal)}</green> <light-blue>HP</light-blue")
            if self.health >= math.floor(self.health * 0.5):
                ansiprint('<bold>Red Skull</bold> <red>deactivates</red>.')
                self.starting_strength -= 3
            self.show_status(False)
        elif heal_type == "Max Health":
            self.max_health += heal
            self.health += heal
            ansiprint(f"Your Max HP is increased by <light-blue>{heal}</light-blue>")
            self.show_status(False)

    def card_actions(self, card: object, action: str, card_pool: list[dict]=None):
        '''[action] == 'Remove', remove [card] from your deck.
        [action] == 'Upgrade', Upgrade [card]
        [action] == 'Transform', transform a card into another random card.
        [action] == 'Store', (Only in the Note From Yourself event) stores a card to be collected from the event in another run.
        '''
        if card_pool is None:
            card_pool = cards
        while True:
            if action == "Remove":
                player.deck.remove(card)
                break
            elif action == 'Transform':
                # Curse cards can only be transformed into other Curses
                if card.get('Type') == 'Curse':
                    options = [valid_card for valid_card in cards if valid_card.get('Type') == 'Curse' and valid_card.get('Rarity') != 'Special']
                else:
                    options = [valid_card for valid_card in cards if valid_card.get('Class') == card.get('Class') and valid_card.get('Type') not in ('Status', 'Curse') and valid_card.get('Rarity') == 'Special']
                while True:
                    new_card = random.choice(options)
                    if new_card == card:
                        continue
                    self.deck.append(new_card)
                    self.deck.remove(card)
                    break
                break
            elif action == 'Upgrade':
                upgraded_cards = [card for card in card_pool if card.get('Name') not in ('Status', 'Curse') and card.get('Upgraded')]
                for valid_card in upgraded_cards:
                    stripped_string = card.get('Name')
                    stripped_string = remove_color_tags(stripped_string)
                    if card.get('Name') == stripped_string:
                        self.deck.insert(card.index(), valid_card)
                        ansiprint(f"{valid_card['Name']} got <green>Upgraded</green>")
                        self.deck.remove(card)
                        break
                break

    def show_status(self, full_view=False, combat=True):
        if combat is True:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)"
            for buff in self.buffs:
                if buff not in non_stacking_effects and self.buffs[buff] > 0:
                    status += f" | <light-cyan>{buff}</light-cyan>: {self.buffs[buff]}"
                elif buff in non_stacking_effects and self.buffs[buff] is True:
                    status += f" | <light-cyan>{buff}</light-cyan>"
            for debuff in self.debuffs:
                if debuff not in non_stacking_effects and self.debuffs[debuff] > 0:
                    status += f" | <light-cyan>{debuff}</light-cyan>: {self.debuffs[debuff]}"
                elif debuff in non_stacking_effects and self.debuffs[debuff] is True:
                    status += f" | <light-cyan>{debuff}</light-cyan>"
        else:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <yellow>{self.gold} Gold</yellow>)"
        ansiprint(status)
        print()
        if full_view is True:
            # int() function used to account for True|False variables.
            for buff in self.buffs:
                # .replace() method is used to replace any variable values with their current values
                if int(self.buffs[buff]) > 0:
                    ansiprint(f"{buff}: {all_effects[buff]}".replace("X", self.buffs[buff]))
            for debuff in self.debuffs:
                if int(self.debuffs[debuff]) > 0:
                    ansiprint(f"{debuff}: {all_effects[debuff]}".replace("X", self.debuffs[debuff]))
        print()

    def end_player_turn(self):
        self.discard_pile.extend(self.hand)
        self.hand = []
        self.end_of_turn_relics()
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

    def debuff(self, debuff_name: str, amount: int, target: object, end: bool):
        if debuff_name not in all_effects:
            ansiprint(f"<red>{debuff_name} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if target.artifact == 0:
            if debuff_name in non_stacking_effects:
                target.debuffs[debuff_name] = True
                ansiprint(f"{self.name} applied <light-red>{debuff_name}</light-red> to {target.name}.")
            else:
                target.debuffs[debuff_name] += amount
            if self == target and debuff_name not in non_stacking_effects:
                ansiprint(f"+{amount} {debuff_name}")
            elif self == target and debuff_name in non_stacking_effects:
                ansiprint(f"<light-red>{debuff_name}</light-red>")
            else:
                ansiprint(f"{self.name} applied {amount} <light-red>{debuff_name}</light-red> to {target.name}")
        else:
            ansiprint(f"{debuff_name} was blocked by {'' if self != target else 'your'} <light-cyan>Artifact</light-cyan>")
            target.artifact -= 1
        if end is False:
            sleep(1)
        else:
            sleep(1.5)
            system("clear")

    def buff(self, buff_name, amount, end):
        if buff_name not in all_effects:
            ansiprint(f"<red>{buff_name} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if buff_name not in non_stacking_effects:
            self.buffs[buff_name] += amount
            ansiprint(f"+{amount} <light-cyan>{buff_name}</light-cyan>")
        else:
            self.buffs[buff_name] = True
            ansiprint(f"<light-cyan>{buff_name}</light-cyan>")
        if buff_name == "Strength(Temp)":
            self.debuff("Strength Down", amount, self, True)
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
        ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
        # Start of turn effects
        self.draw_cards(False, 0)
        self.debuff_buff_tick()
        self.start_of_turn_relics()
        self.energy += self.energy_gain + self.buffs["Energized"] + self.buffs["Berzerk"]
        if self.buffs["Energized"] > 0:
            ansiprint(f"You gained {self.buffs['Energized']} extra energy because of <light-cyan>Energized</light-cyan>")
            self.buffs["Energized"] = 0
            ansiprint("<light-cyan>Energized wears off.")
        if self.buffs["Berzerk"] > 0:
            ansiprint(f"You gained {self.buffs['Berzerk']} extra energy because of <light-cyan>Berzerk</light-cyan>")
        if combat_turn > 1:
            if self.buffs["Barricade"] is False: # Barricade: Block is not remove at the start of your turn
                self.block = 0
            else:
                if self.block > 0 and combat_turn > 1:
                    ansiprint("Your Block was not removed because of <light-cyan>Barricade</light-cyan>")

    def debuff_buff_tick(self):
        # ///////Buffs\\\\\\\\
        for buff in self.buffs:
            if buff in duration_effects and self.buffs[buff] > 0:
                self.buffs[buff] -= 1
                ansiprint(f"-1 <light-cyan>{buff}</light-cyan>")
                if self.buffs[buff] == 0:
                    ansiprint(f"<light-cyan>{buff}</light-cyan> wears off")
        # //////Debuffs\\\\\\
        for debuff in self.debuffs:
            if debuff not in non_stacking_effects and self.debuffs[debuff] > 0:
                self.debuffs[debuff] -= 1
                ansiprint(f"-1 <light-cyan>{debuff}</light-cyan>")
                if self.debuffs[debuff] == 0:
                    ansiprint(f"<light-cyan>{debuff}</light-cyan> wears off.")
        if self.debuffs['Strength Down'] > 0: # Strength Down: Lose X Strength at the end of your turn
            self.buffs['Strength'] -= self.debuffs['Strength Down']
            ansiprint(f"<red>Strength</red> was reduced by {self.debuffs['Strength Down']} because of <red>Strength Down</red>")
            sleep(0.7)
            self.debuffs['Strength Down'] = 0
            print("Strength Down wears off.")
            sleep(0.8)

    def end_of_turn_effects(self):
        if self.buffs["Regeneration"] > 0:
            self.health_actions(self.buffs["Regeneration"], False)
            # Regeneration gets reduced by 1 in the above function
        if self.buffs["Metallicize"] > 0: # Metallicize: At the end of your turn, gain X Block
            print("Metallicize: ", end='')
            self.blocking(self.buffs["Metallicize"], False)
            sleep(0.8)
        if self.buffs["Plated Armor"] > 0: # Plated Armor: At the end of your turn, gain X Block. Decreases by 1 when recieving unblocked attack damage
            print("Plated Armor: ", end='')
            self.blocking(self.buffs["Plated Armor"], False)
            sleep(0.8)
        if self.buffs["Ritual"] > 0:
            print("Ritual: ", end='')
            self.buff("Strength", self.buffs["Ritual"], True)
        if self.buffs["Combust"] > 0:
            damage(self.combusts_played, self, self, True, False)
            for enemy in active_enemies:
                damage(self.buffs["Combust"], enemy, self, False, False)
                sleep(0.1)
        if self.buffs["Omega"] > 0:
            for enemy in active_enemies:
                damage(self.buffs["Omega"], enemy, self, False, False)
                sleep(0.1)
        if self.buffs["The Bomb"] > 0:
            self.the_bomb_countdown -= 1
            if self.the_bomb_countdown == 0:
                for enemy in active_enemies:
                    damage(self.buffs['The Bomb'], self, self, False, False)
                    self.buffs["The Bomb"] = 0
                    ansiprint("<light-cyan>The Bomb</light-cyan> wears off")
                    self.the_bomb_countdown = 3

    def start_of_turn_effects(self):
        if self.buffs["Next Turn Block"] > 0:
            self.blocking(self.buffs["Next Turn Block"], False)
            self.buffs["Next Turn Block"] = 0
            ansiprint('<light-cyan>Next Turn Block</light-cyan> wears off')

    def start_of_turn_relics(self):
        if relics['Anchor'] in self.relics:
            self.block += 10
            ansiprint('You gained 10 <blue>Block</blue> from <bold>Anchor</bold>.')
        if self.attacks_played_this_turn is False and relics['Art of War'] in self.relics:
            self.energy += 1
            ansiprint('You gained 1 Energy from <bold>Art of War</bold>.')
        if relics['Damaru'] in self.relics:
            ansiprint('From <bold>Damaru</bold>: ', end='')
            self.buff('Mantra', 1, False)
        if relics['Lantern'] in self.relics:
            ansiprint('From <bold>Lantern</bold: ', end='')
            self.buff('Energized', 1, False)
        if relics['Happy Flower'] in self.relics:
            if self.happy_flower % 3 != 0:
                self.happy_flower += 1
                if self.happy_flower == 3:
                    ansiprint('From <bold>Happy Flower</bold>: ', end='')
                    self.buff('Energized', 1, False)

    def end_of_turn_relics(self):
        if relics['Orichaicum'] in self.relics and self.block == 0:
            ansiprint('From <bold>Orichaicum</bold>: ', end='')
            self.blocking(6, False)

    def start_of_combat_relics(self):
        if relics['Akabeko'] in self.relics:
            self.buffs["Vigor"] += 8
            ansiprint(f'+8 <light-cyan>Vigor</light-cyan> from <bold>Akabeko</bold>(Next Attack deals {self.buffs["Vigor"]} more damage.)')
        if self.ancient_tea_set is True and relics['Ancient Tea Set'] in self.relics and combat_turn == 1:
            self.energy += 2
            ansiprint('You gained 2 Energy from <bold>Ancient Tea Set</bold>')
        if relics['Bag of Marbles'] in self.relics:
            for enemy in active_enemies:
                ansiprint('From <bold>Bag of Marbles</bold>: ', end='')
                self.debuff('Vulnerable', 1, enemy, False)
        # Bag of Preparation and Ring of the Snake are coded in the .draw_cards() method above.
        if relics['Blood Vial'] in self.relics:
            ansiprint('From <bold>Blood Vial</bold>: ', end='')
            self.health_actions(2, 'Heal')
        if relics['Bronze Scales'] in self.relics:
            ansiprint('From <bold>Bronze Scales</bold>: ', end='')
            self.buff('Thorns', 3, False)
        if relics['Oddly Smooth Stone'] in self.relics:
            ansiprint('From <bold>Oddly Smooth Stone</bold>: ', end='')
            self.buff('Dexterity', 1, False)
        if relics['Data Disk'] in self.relics:
            ansiprint('From <bold>Data Disk</bold>: ', end='')
            self.buff('Focus', 1, False)



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
    def __init__(self, health: list, block: int, name: str, moves: list[str]):
        self.health = health
        self.max_health = health
        self.block = block
        self.name = name
        if 'louse' in self.name:
            self.damage = [5, 7]
        self.past_moves = ['place'] * 3
        self.moves = moves
        self.buffs = {}
        for buff in enemy_buffs:
            if buff not in non_stacking_effects:
                self.buffs[buff] = 0
            else:
                self.buffs[buff] = False
        self.debuffs = {}
        for debuff in enemy_debuffs:
            if debuff not in non_stacking_effects:
                self.debuffs[debuff] = 0
            else:
                self.debuffs[debuff] = False
        self.active_turns = 1
        if 'louse' in self.name:
            self.buffs["Curl Up"] = random.randint(3, 7)

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

    def move_spam_check(self, target_move, target_count):
        use_count = 0

        for move in self.past_moves:
            if move == target_move:
                use_count += 1
                if use_count == target_count:
                    return False
            else:
                use_count = 0

        return True

    def enemy_turn(self):
        while True:
            if self.name == "Cultist":
                if self.active_turns == 1:
                    self.buff("Ritual", 3, True, True, "Incantation")
                    break
                self.attack(6, 1, True, True, "Dark Strike")
            elif self.name in ('Acid Slime (L)', 'Acid Slime (M)'):
                random_num = random.randint(0, 100)
                if self.health < math.floor(self.max_health * 0.5) and self.name == "Acid Slime (L)":
                    ansiprint("<bold>Split<bold>")
                    self.die()
                    active_enemies.append(Enemy([self.health, self.health], 0, "Acid Slime (M)", [['self.attack(7, 1, True, False)', "self.status(cards['Slimed'], 1, player.discard_pile, False, True)"], ['self.debuff("Weak", 1, True, True, "Lick")'], ['self.attack(10, 1, True, True, "Tackle")']]))
                    print("Acid Slime (M) spawned!")
                    active_enemies.append(Enemy([self.health, self.health], 0, "Acid Slime (M)", [['self.attack(7, 1, True, False)', "self.status(cards['Slimed'], 1, player.discard_pile, False, True)"], ['self.debuff("Weak", 1, True, True, "Lick")'], ['self.attack(10, 1, True, True, "Tackle")']]))
                    print("Acid Slime (M) spawned!")
                    sleep(1.5)
                    system("clear")
                    break
                if random_num < 30 and self.move_spam_check("Corrosive", 3):
                    self.attack(11, 1, True, False, "Corrosive Spit")
                    self.status(cards["Slimed"], 2, player.discard_pile, False, True)
                    self.past_moves.append("Corrosive Spit")
                    break
                if random_num > 70 and self.move_spam_check("Lick", 3):
                    self.debuff("Weak", 2, True, True, "Lick")
                    self.past_moves.append("Lick")
                    break
                if self.move_spam_check("Tackle", 2):
                    self.attack(16, 1, True, True, "Tackle")
                    self.past_moves.append("Tackle")
                    break
                self.active_turns += 1
            elif self.name == "Acid Slime (S)":
                random_num = random.randint(0, 100)
                if random_num < 50 and self.active_turns == 1:
                    self.debuff("Weak", 1, True, True, "Lick")
                    self.past_moves.append("Lick")
                    break
                if random_num > 50 and self.active_turns == 1:
                    self.attack(3, 1, True, True, "Tackle")
                    self.past_moves.append("Tackle")
                    break
                if self.move_spam_check("Tackle", 2):
                    self.attack(3, 1, True, True, "Tackle")
                    self.past_moves.append("Tackle")
                    break
                if self.move_spam_check("Lick", 2):
                    self.debuff("Weak", 1, True, True, "Lick")
                    self.past_moves.append("Lick")
                    break
                self.active_turns += 1
            elif self.name == "Jaw Worm":
                random_num = random.randint(0, 100)
                if self.active_turns == 1 or (random_num > 75 and self.past_moves != "Chomp"):
                    self.attack(11, 1, True, True, "Chomp")
                    self.past_moves.append("Chomp")
                    break
                if random_num < 45 and self.past_moves[-1] != "Bellow":
                    self.buff("Strength", 3, True, False, "Bellow")
                    self.blocking(6, False, True)
                    self.past_moves.append("Bellow")
                    break
                if self.past_moves[-2] != "Thrash":
                    self.attack(7, 1, True, False, "Thrash")
                    self.blocking(5, False, True)
                    self.past_moves.append("Thrash")
                    break
            elif 'louse' in self.name.lower():
                random_num = random.randint(0, 100)
                if random_num < 75 and self.past_moves[-2] != "Bite":
                    self.attack(self.damage, 1, True, True, "Bite")
                    self.past_moves.append("Bite")
                    break
                if self.past_moves[-2] != "Grow" and self.name == "Red Louse":
                    self.buff("Strength", 3, True, True, "Grow")
                    self.past_moves.append("Grow")
                    break
                if self.past_moves[-2] != "Spit Web" and self.name == "Green Louse":
                    self.debuff("Weak", 2, True, True, "Spit Web")
                    self.past_moves.append("Spit Web")
                    break


    def show_status(self):
        status = f"{self.name} (<red>{self.health} / {self.max_health}</red> | <light-blue>{self.block} Block</light-blue>)"
        if self.buffs["Barricade"] is True:
            status += " | <light-cyan>Barricade</light-cyan>"
        if self.buffs['Artifact'] > 0:
            status += f" | <light-cyan>Artifact: {self.buffs['Artifact']}</light-cyan>"
        if self.buffs["Vulnerable"] > 0:
            status += f" | <light-cyan>Vulnerable: {self.buffs['Vulnerable']}</light-cyan>"
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
                ansiprint("<red>The starting function of a move MUST have a name!</red>")
                sys.exit(1)
            ansiprint(f"<bold>{name}</bold>")
            sleep(1)
        if buff not in all_effects:
            ansiprint(f"<red>{buff} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if buff not in non_stacking_effects:
            self.buffs[buff] += amount
            ansiprint(f"{self.name} gained {amount} <light-cyan>{buff}</light-cyan>")
        else:
            self.buffs[buff] = True
            ansiprint(f"{self.name} gained <light-cyan>{buff}</light-cyan>")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)
    def debuff(self, debuff, amount, start, end, name=""):
        if start is True:
            if name == "":
                ansiprint("<red>The starting function of a move MUST have a name!</red>")
                sys.exit(1)
            ansiprint(f"<bold>{name}</bold>")
            sleep(1)
        if debuff not in all_effects:
            ansiprint(f"<red>{debuff} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if debuff not in non_stacking_effects:
            player.debuffs[debuff] += amount
            ansiprint(f"{self.name} applied {amount} <light-cyan>{debuff}</light-cyan> to you")
        else:
            player.debuffs[debuff] = True
            ansiprint(f"{self.name} applied <light-cyan>{debuff}</light-cyan> to you")
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
    def status(self, status_card: dict, amount: int, location: list, start: bool, end: bool, name=""):
        if start is True:
            if name == "":
                ansiprint("<light-red>The starting function of a move MUST have a name!</light-red>")
                sys.exit()
            ansiprint(f"<bold>{name}</bold>")
            sleep(1)
        for _ in range(amount):
            insert_index = random.randint(0, len(location) - 1)
            location.insert(insert_index, status_card)
        print(f"{player.name} gained {amount} {status_card['Name']}({status_card['Info']}) \nPlaced into {location}")
        if end is True:
            sleep(1.5)
            system("clear")
        else:
            sleep(1)

    def start_turn(self):
        ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
        if self.buffs["Barricade"] is False:
            self.block = 0
        else:
            if self.active_turns > 1 and self.block > 0:
                ansiprint(f"{self.name}'s Block was not removed because of <light-cyan>Barricade</light-cyan")
        if self.buffs["Vulnerable"] > 0:
            self.buffs["Vulnerable"] -= 1
            ansiprint("<light-cyan>-1 Vulnerable</light-cyan>")
            if self.buffs["Vulnerable"] == 0:
                print("Vulnerable wears off.")
        if self.buffs['Weak'] > 0:
            self.buffs['Weak'] -= 1
            ansiprint("<light-cyan>-1 Weak</light-cyan>")
            if self.buffs['Weak'] == 0:
                print("Weak wears off")
        print()


# Characters
player = Player(80, 0, 3, [])
cards = {
    # Ironclad cards
    'Strike': {'Name': 'Strike', 'Damage': 6, 'Energy': 1, 'Rarity': 'Basic', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {6 + player.buffs["Strength"]} damage', 'Function': player.use_strike},
    'Strike+': {'Name': '<green>Strike+</green>', 'Upgraded': True, 'Damage': 9, 'Energy': 1, 'Rarity': 'Basic', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {9 + player.buffs["Strength"]} damage', 'Function': player.use_strike},

    'Defend': {'Name': 'Defend', 'Block': 5, 'Energy': 1, 'Target': 'Yourself', 'Rarity': 'Basic', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.buffs["Dexterity"]} <yellow>Block</yellow>', 'Function': player.use_defend},
    'Defend+': {'Name': '<green>Defend+</green>', 'Upgraded': True, 'Block': 8, 'Energy': 1, 'Target': 'Yourself', 'Rarity': 'Basic', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {8 + player.buffs["Dexterity"]} <yellow>Block</yellow>', 'Function': player.use_defend},

    'Bash': {'Name': 'Bash', 'Damage': 8, 'Vulnerable': 2, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Basic', 'Class': 'Ironclad', 'Type': 'Attack', 'Info': f'Deal {8 + player.buffs["Strength"]} damage. Apply 2 <yellow>Vulnerable</yellow>', 'Function': player.use_bash},
    'Bash+': {'Name': '<green>Bash+</green>', 'Upgraded': True, 'Damage': 10, 'Vulnerable': 3, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Basic', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {10 + player.buffs["Strength"]} damage. Apply 3 <yellow>Vulnerable</yellow>', 'Function': player.use_bash},

    'Anger': {'Name': 'Anger', 'Damage': 6, 'Energy': 0, 'Location': player.discard_pile, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {6 + player.buffs["Strength"]} damage. Add a copy of this card to your discard pile.', 'Function': player.use_anger},
    'Anger+': {'Name': '<green>Anger+</green>', 'Upgraded': True, 'Damage': 8, 'Energy': 0, 'Location': player.discard_pile, 'Target': 'Single', 'Rarity': 'Common', 'Class': 'Ironclad', 'Type': 'Attack', 'Info': f'Deal {8 + player.buffs["Strength"]} damage. Add a copy of this card to your discard pile.', 'Function': player.use_anger},

    'Armaments': {'Name': 'Armaments', 'Block': 5, 'Upgrade Target': 'Single', 'Target': 'Yourself', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.buffs["Dexterity"]} <yellow>Block</yellow>. <yellow>Upgrade</yellow> a card in your hand for the rest of combat.'},
    'Armaments+': {'Name': '<green>Armaments+</green>', 'Upgraded': True, 'Block': 5, 'Upgrade Target': 'All', 'Target': 'Yourself', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.buffs["Dexterity"]} <yellow>Block</yellow>. <yellow>Upgrade</yellow> ALL cards in your hand for the rest of combat.'},

    'Body Slam': {'Name': 'Body Slam', 'Damage': player.block, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal damage equal to your <yellow>Block</yellow>({player.block + player.buffs["Strength"]})', 'Function': player.use_bodyslam},
    'Body Slam+': {'Name': '<green>Body Slam+</green>', 'Upgraded': True, 'Damage': player.block, 'Energy': 0, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal damage equal to your <yellow>Block</yellow>({player.block + player.buffs["Strength"]})', 'Function': player.use_bodyslam},

    'Clash': {'Name': 'Clash', 'Damage': 14, 'Energy': 0, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Can only be played is every card in your hand is an Attack. Deal {14 + player.buffs["Strength"]} damage.', 'Function': player.use_clash},
    'Clash+': {'Name': '<green>Clash+</green>', 'Upgraded': True, 'Damage': 18, 'Energy': 0, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Can only be played if every card in your hand is an Attack. Deal {18 + player.buffs["Strength"]} damage.', 'Function': player.use_clash},

    'Cleave': {'Name': 'Cleave', 'Damage': 8, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {8 + player.buffs["Strength"]} damage to ALL enemies', 'Function': player.use_cleave},
    'Cleave+': {'Name': '<green>Cleave+</green>', 'Upgraded': True, 'Damage': 11, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {11 + player.buffs["Strength"]} damage to ALL enemies', 'Function': player.use_cleave},

    'Clothesline': {'Name': 'Clothesline', 'Energy': 2, 'Damage': 12, 'Weak': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {12 + player.buffs["Strength"]} damage. Apply 2 <yellow>Weak</yellow>', 'Function': player.use_clothesline},
    'Clothesline+': {'Name': '<green>Clothesline+</green>', 'Upgraded': True, 'Energy': 2, 'Damage': 14, 'Weak': 3, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {14 + player.buffs["Strength"]} damage. Apply 3 <yellow>Weak</yellow>', 'Function': player.use_clothesline},

    'Flex': {'Name': 'Flex', 'Strength': 2, 'Strength Down': 2, 'Energy': 0, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Gain 2 <yellow>Strength</yellow>. At the end of your turn, lose 2 <yellow>Strength</yellow>'},
    'Flex+': {'Name': '<green>Flex+</green>', 'Upgraded': True, 'Strength': 4, 'Strength Down': 4, 'Energy': 0, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Gain 4 <yellow>Strength</yellow>. At the end of your turn lose 4 <yellow>Strength</yellow>', 'Function': player.use_flex},

    'Havoc': {'Name': 'Havoc', 'Energy': 1, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Play the top card of your draw pile and <yellow>Exhaust</yellow> it.', 'Function': player.use_havoc},
    'Havoc+': {'Name': '<green>Havoc+</green>', 'Upgraded': True, 'Energy': 0, 'Target': 'Yourself', 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': 'Play the top card of your draw pile and <yellow>Exhaust</yellow> it.', 'Function': player.use_havoc},

    'Headbutt': {'Name': 'Headbutt', 'Damage': 9, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {9 + player.buffs["Strength"]} damage. Place a card from your discard pile on top of your draw pile.', 'Function': player.use_headbutt},
    'Headbutt+': {'Name': '<green>Headbutt+</green>', 'Upgraded': True, 'Damage': 12, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {12 + player.buffs["Strength"]} damage. Place a card from your discard pile on top of your draw pile.', 'Function': player.use_headbutt},

    'Heavy Blade': {'Name': 'Heavy Blade', 'Damage': 14, 'Strength Multi': 3, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {14 + player.buffs["Strength"]} damage. <yellow>Strength</yellow> affects this card 3 times.', 'Function': player.use_heavyblade},
    'Heavy Blade+': {'Name': '<green>Heavy Blade+</green>', 'Upgraded': True, 'Damage': 14, 'Strength Multi': 5, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {14 + player.buffs["Strength"]} damage. <yellow>Strength</yellow> affects this card 5 times', 'Function': player.use_heavyblade},

    'Iron Wave': {'Name': 'Iron Wave', 'Damage': 5, 'Block': 5, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Gain {5 + player.buffs["Dexterity"]} <yellow>Block</yellow>. Deal {5 + player.buffs["Strength"]} damage.', 'Function': player.use_ironwave},
    'Iron Wave+': {'Name': '<green>Iron Wave+</green>', 'Upgraded': True, 'Damage': 7, 'Block': 7, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Gain {7 + player.buffs["Dexterity"]} <yellow>Block</yellow>. Deal {7 + player.buffs["Strength"]} damage.', 'Function': player.use_ironwave},

    'Perfected Strike': {'Name': 'Perfected Strike', 'Damage': 6, 'Damage Per "Strike"': 2, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 
                         'Info': f'Deal {6 + player.buffs["Strength"] + len([card for card in player.deck if "strike" in card.get("Name").lower()]) * 2} damage. Deals 2 additional damage for ALL your cards containing "Strike".', 'Function': player.use_perfectedstrike},
    'Perfected Strike+': {'Name': '<green>Perfected Strike+</green>', 'Upgraded': True, 'Damage': 6, 'Damage Per "Strike"': 3, 'Energy': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 
                          'Info': f'Deal {6 + player.buffs["Strength"] + len([card for card in player.deck if "strike" in card.get("Name").lower()]) * 3} damage. Deals 3 additional damage for ALL your cards containing "Strike".', 'Function': player.use_perfectedstrike},

    'Pommel Strike': {'Name': 'Pommel Strike', 'Damage': 9, 'Cards': 2, 'Energy': 1, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {9 + player.buffs["Strength"]} damage. Draw 1 card.', 'Function': player.use_pommelstrike},
    'Pommel Strike+': {'Name': '<green>Pommel Strike+</green>', 'Upgraded': True, 'Damage': 10, 'Cards': 2, 'Target': 'Single', 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {10 + player.buffs["Strength"]} damage. Draw 2 cards.', 'Function': player.use_pommelstrike},

    'Shrug it Off': {'Name': 'Shrug it Off', 'Block': 8, 'Cards': 1, 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {8 + player.buffs["Dexterity"]} <yellow>Block</yellow>. Draw 1 card.', 'Function': player.use_shrugitoff},
    'Shrug it Off+': {'Name': '<green>Shrug it Off+</green>', 'Upgraded': True, 'Block': 11, 'Cards': 1, 'Energy': 1, 'Rarity': 'Common', 'Type': 'Skill', 'Class': 'Ironclad', 'Info': f'Gain {11 + player.buffs["Dexterity"]} <yellow>Block</yellow>. Draw 1 card.', 'Function': player.use_shrugitoff},

    'Sword Boomerang': {'Name': 'Sword Boomerang', 'Damage': 3, 'Times': 3, 'Target': 'Random', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {3 + player.buffs["Strength"]} damage to a random enemy 3 times.', 'Function': player.use_swordboomerang},
    'Sword Boomerang+': {'Name': '<green>Sword Boomerang+</green>', 'Upgraded': True, 'Damage': 3, 'Times': 4, 'Target': 'Random', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {3 + player.buffs["Strength"]} damage to a random enemy 4 times.', 'Function': player.use_swordboomerang},

    'Thunderclap': {'Name': 'Thunderclap', 'Damage': 4, 'Vulnerable': 1, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {4 + player.buffs["Strength"]} damage and apply 1 <yellow>Vulnerable</yellow> to ALL enemies.', 'Function': player.use_thunderclap},
    'Thunderclap+': {'Name': '<green>Thunderclap+</green>', 'Upgraded': True, 'Damage': 7, 'Vulnerable': 1, 'Target': 'All', 'Energy': 1, 'Rarity': 'Common', 'Type': 'Attack', 'Class': 'Ironclad', 'Info': f'Deal {7 + player.buffs["Strength"]} damage and apply 1 <yellow>Vulnerable</yellow> to ALL enemies.', 'Function': player.use_thunderclap},

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
    'Regal Pillow': {'Name': 'Regal Pillow', 'Class': 'Any', 'Rarity': 'Common', 'Heal HP': 15, 'Info': 'Heal an additional 15 HP when you Rest.', 'Flavor': "Now you can get a proper night's rest."},
    'Smiling Mask': {'Name': 'Smiling Mask', 'Class': 'Any', 'Rarity': 'Common', 'Info': "The merchant's card removal service now always costs 50 Gold.", 'Flavor': 'Mask worn by the merchant. He must have spares...'},
    'Strawberry': {'Name': 'Strawberry', 'Class': 'Any', 'Rarity': 'Common', 'Max HP': 7, 'Flavor': "'Delicious! Haven't seen any of these since the blight.' - Ranwid"},
    'The Boot': {'Name': 'The Boot', 'Class': 'Any', 'Rarity': 'Common', 'Info': 'When you would deal 4 or less unblocked Attack damage, increase it to 5.', 'Flavor': 'When wound up, the boot grows larger in size.'},
    'Tiny Chest': {'Name': 'Tiny Chest', 'Class': 'Any', 'Rarity': 'Common', 'Info': 'Every 4th <bold>?</bold> room is a <bold>Treasure</bold> room.', 'Flavor': '"A fine prototype." - The Architect'},
    # Class specific common relics
    'Red Skull': {'Name': 'Red Skull', 'Class': 'Ironclad', 'Rarity': 'Common', 'Info': 'While your HP is at or below 50%, you have 3 additional <bold>Strength</bold>.', 'Flavor': 'A small skull covered in ornamental paint.'},
    'Snecko Skull': {'Name': 'Snecko Skull', 'Class': 'Silent', 'Rarity': 'Common', 'Info': 'Whenever you apply <bold>Poison</bold>, apply an additional 1 <bold>Poison</bold>', 'Flavor': 'A snecko skull in pristine condition. Mysteriously clean and smooth, dirt and grime fall off inexplicably.'},
    'Data Disk': {'Name': 'Data Disk', 'Class': 'Defect', 'Rarity': 'Common', 'Info': 'Start each combat with 1 <bold>Focus</bold>.', 'Flavor': 'This dish contains precious data on birds and snakes.'},
    'Damaru': {'Name': 'Damaru', 'Class': 'Watcher', 'Rarity': 'Common', 'Info': 'At the start of your turn, gain 1 <bold>Mantra</bold>.', 'Flavor': 'The sound of the small drum keeps your mind awake, revealing a path forward.'},
    # Uncommon relics
    'Blue Candle': {'Name': 'Blue Candle', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': '<bold>Curse</bold> cards can now be played. Playing a <bold>Curse</bold> will make you lose 1 HP and <bold>Exhaust</bold> the card.', 'Flavor': 'The flame ignites when shrouded in darkness.'},
    'Bottled Flame': {'Name': 'Bottled Flame', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Upon pickup, choose an <bold>Attack</bold> card. At the start of your turn, this card will be in your hand.', 'Flavor': 'Inside the bottle resides a flame which eternally burns.'},
    'Bottled Lightning': {'Name': 'Bottled Lightning', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Upon pickup, choose an <bold>Skill</bold> card. At the start of your turn, this card will be in your hand.', 'Flavor': 'Peering into the swirling maelstrom, you see a part of yourself staring back.'},
    'Bottled Tornado': {'Name': 'Bottled Tornado', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Upon pickup, choose an <bold>Power</bold> card. At the start of your turn, this card will be in your hand.', 'Flavor': 'The bottle gently hums and whirs.'},
    'Darkstone Periapt': {'Name': 'Darkstone Periapt', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Whenever you obtain a <bold>Curse</bold>, raise your Max HP by 6.', 'Flavor': 'The stone draws power from dark energy, converting it into vitality for the user.'},
    'Eternal Feather': {'Name': 'Eternal Feather', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'For every 5 cards in your deck, heal 3 HP when you enter a rest site.', 'Flavor': 'This feather appears to be completely indestructible. What bird does this possibly come from?'},
    'Molten Egg': {'Name': 'Molten Egg', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Whenever you add an <bold>Attack</bold> card to your deck, it is <bold>Upgraded</bold>. ', 'Flavor': 'The egg of a Pheonix. It glows red hot with a simmering lava.'},
    'Toxic Egg': {'Name': 'Toxic Egg', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Whenever you add a <bold>Skill</bold> card to your deck, it is <bold>Upgraded</bold>. ', 'Flavor': '"What a marvelous discovery! This appears to be the inert egg of some magical creature. Who or what created this?" - Ranwid'},
    'Frozen Egg': {'Name': 'Frozen Egg', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Whenever you add a <bold>Power</bold> card to your deck, it is <bold>Upgraded</bold>. ', 'Flavor': 'The egg lies inert and frozen, never to hatch'},
    'Gremlin Horn': {'Name': 'Gremlin Horn', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Whenever an enemy dies, gain 1 <bold>Energy</bold> and draw 1 card.'},
    'Horn Cleat': {'Name': 'Horn Cleat', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'At the start ofy our 2nd trun, gain 14 <bold>Block</bold>.', 'Flavor': 'Pleasant to hold in the hand. What was it for?'},
    'Ink Bottle': {'Name': 'Ink Bottle', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Whenever you play 10 cards, draw 1 card.', 'Flavor': 'Once exhausted, it appears to refil itself in a different color.'},
    'Kunai': {'Name': 'Kunai', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Every time you play 3 <bold>Attacks</bold> in a single turn, gain 1 <bold>Dexterity</bold>.', 'Flavor': 'A blade favored by assasins for its lethality at range.'},
    'Letter Opener': {'Name': 'Letter Opener', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Every time you play 3 <bold>Skill</bold> in a single turn, deal 5 damage to ALL enemies.', 'Flavor': 'Unnaturally sharp.'},
    'Matryoshka': {'Name': 'Matryoshka', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'The next 2 non-boss chests you open contain 2 relics.', 'Flavor': 'A stackable set of dolls. The paint depicts an unknown bird with white eyes and blue feathers.'},
    'Meat on the Bone': {'Name': 'Meat on the Bone', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'If your HP is at 50% or lower at the end of combat, heal 12 HP.'},
    'Mercury Hourglass': {'Name': 'Mercury Hourglass', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'At the start of your turn, deal 3 damage to ALL enemies.', 'Flavor': 'An enchanted hourglass that endlessly drips.'},
    'Mummified Hand': {'Name': 'Mummified Hand', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Whenever you play a <bold>Power</bold> card, a random card in your hand costs 0 that turn.', 'Flavor': 'Frequently twitches, especially when your pulse is high.'},
    'Ornamental Hand': {'Name': 'Ornamental Hand', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Every time you play 3 <bold>Attacks</bold> in a single turn, gain 4 <bold>Block</bold>.', 'Flavor': 'The fan seems to extend and harden as blood is spilled.'},
    'Pantograph': {'Name': 'Pantograph', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'At the start of boss combats, heal 25 HP.', 'Flavor': '"Solid foundations are not accidental. Tools for planning are a must." - The Architect'},
    'Pear': {'Name': 'Pear', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Raise your Max HP by 10', 'Flavor': 'A common fruit before the Spireblight.'},
    'Question Card': {'Name': 'Question Card', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Future card rewards have 1 additional card to choose from.', 'Flavor': '"Those with more choices minimize the downside to chaos." - Kublai the Great'},
    'Shuriken': {'Name': 'Shuriken', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Every time you play 3 <bold>Attacks</bold> in a single turn, gain 1 <bold>Strength</bold>.', 'Flavor': 'Lightweight throwing weapons. Recommend going for the eyes.'},
    'Singing Bowl': {'Name': 'Singing Bowl', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'When adding cards to your deck, you may gain +2 Max HP instead.', 'Flavor': 'This well-used artifact rings out a beautiful melody when struck.'},
    'Strike Dummy': {'Name': 'Strike Dummy', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': "Cards containing 'Strike' deal 3 additional damage.", 'Flavor': "It's beat up."},
    'Sundial': {'Name': 'Sundial', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Every 3 times you shuffle your draw pile, gain 2 <bold>Energy</bold>.', 'Flavor': "'Early man's foolish obsession with time caused them to look to the sky for guidance, hoping for something permanent.' - Zoroth"},
    'The Courier': {'Name': 'The Courier', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'The merchant never runs out of cards, relics, or potions and his prices are reduced by 20%.', 'Flavor': "The merchant's personal pet!"},
    'White Beast Statue': {'Name': 'White Beast Statue', 'Class': 'Any', 'Rarity': 'Uncommon', 'Info': 'Potions always drop after combat.', 'Flavor': 'A small white statue of a creature you have never seen before.'},
    # Class specific uncommon relics
    'Paper Phrog': {'Name': 'Paper Phrog', 'Class': 'Ironclad', 'Rarity': 'Uncommon', 'Info': 'Enemies with <bold>Vulnerable</bold> take 75% more damage rather than 50%.', 'Flavor': 'The paper continuously folds and unfolds into the shape of a small creature.'},
    'Self-Forming Clay': {'Name': 'Self-Forming Clay', 'Class': 'Ironclad', 'Rarity': 'Uncommon', 'Info': 'Whenever you lose HP in combat, gain 4 <bold>Block</bold> next turn.', 'Flavor': '“Most curious! It appears to form itself loosely on my thoughts! Tele-clay?” - Ranwid'},
    'Ninja Scroll': {'Name': 'Ninja Scroll', 'Class': 'Silent', 'Rarity': 'Uncommon', 'Info': 'Start each combat with 3 <bold>Shivs</bold> in hand.', 'Flavor': 'Contains the secrets of assasination.'},
    'Paper Krane': {'Name': 'Paper Krane', 'Class': 'Silent', 'Rarity': 'Uncommon', 'Info': 'Enemies with <bold>Weak</bold> deal 40% less damage rather than 25%.', 'Flavor': 'An origami of a creature of a past age.'},
    'Gold-Plated Cables': {'Name': 'Gold-Plated Cables', 'Class': 'Defect', 'Rarity': 'Uncommon', 'Info': 'Your rightmost <bold>Orb</bold> triggers its passive an additional time.', 'Flavor': '"Interesting! Even automatons are affected by placebo." - Ranwid'},
    'Symbiotic Virus': {'Name': 'Symbiotic Virus', 'Class': 'Defect', 'Rarity': 'Uncommon', 'Info': 'At the start of each combat, Channel 1 <bold>Dark</bold> orb.', 'Flavor': 'A little bit of bad can do a lot of good.'},
    'Duality': {'Name': 'Duality', 'Class': 'Watcher', 'Rarity': 'Uncommon', 'Info': 'Whenever you play an <bold>Attack</bold>, gain 1 <bold>Dexterity</bold>.', 'Flavor': '“And the sun was extinguished forever, as if curtains fell before it.” - Zoroth'},
    'Teardrop Locket': {'Name': 'Teardrop Locket', 'Class': 'Watcher', 'Rarity': 'Uncommon', 'Info': 'Start each combat in <bold>Calm</bold>.', 'Flavor': 'Its owner blind, its contents unseen.'},
    # Rare relics
    'Bird-Faced Urn': {'Name': 'Bird-Faced Urn', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Whenever you play a <bold>Power</bold> card, heal 2 HP.', 'Flavor': 'The urn shows the crow god Mazaleth looking mischievous.'},
    'Calipers': {'Name': 'Calipers', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'At the start of your turn, lose 15 <bold>Block</bold> rather than all of your <bold>Block</bold>.', 'Flavor': '"Mechanical precision leads to greatness." - The Architect'},
    "Captain's Wheel": {'Name': "Captain's Wheel", 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'At the start of your 3rd turn, gain 18 <bold>Block</bold>.', 'Flavor': 'A wooden trinked carved with delicate precision. A name is carved into it but the language is foreign.'},
    'Dead Branch': {'Name': 'Dead Branch', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Whenever you <bold>Exhaust</bold> a card, add a random card into your hand.', 'Flavor': 'The branch of a tree from a forgotten era.'},
    'Du-Vu Doll': {'Name': 'Du-Vu Doll', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'For each <bold>Curse</bold> in your deck, start each comabt with 1 additional <bold>Strength</bold>.', 'Flavor': 'A doll devised to gain strength from malicious energy.'},
    'Fossilized Helix': {'Name': 'Fossilized Helix', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Prevent the first time you would lose HP in combat.', 'Flavor': 'Seemingly indestrutible, you wonder what kind of creature this belonged to.'},
    'Gambling Chip': {'Name': 'Gambling Chip', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'At the start of each combat, discard any number of cards then draw that many.', 'Flavor': "You see a small inscription on one side. It reads: 'Bear's Lucky Chip!''"},
    'Ginger': {'Name': 'Ginger', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'You can no longer become <bold>Weakened</bold>.', 'Flavor': 'A potent tool in many tonics.'},
    'Girya': {'Name': 'Girya', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'You can now gain <bold>Strength</bold> at <bold>Rest Sites</bold>. (3 times max)', 'Flavor': 'This Girya is unfathomably heavy. You could train with this to get significantly stronger.'},
    'Ice Cream': {'Name': 'Ice Cream', 'Class': 'Any', 'Rarity': 'Rare', 'Info': '<bold>Energy</bold> is now conserved between turns.', 'Flavor': 'Delicious!'},
    'Incense Burner': {'Name': 'Incense Burner', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Every 6 turns, gain 1 <bold>Intangible</bold>', 'Flavor': 'The smoke imbues the owner with the spirit of the burned.'},
    'Lizard Tail': {'Name': 'Lizard Tail', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'When you would die, heal to 50% of your Max HP instead. (Works once)', 'Flavor': 'A fake tail to trick enemies during combat.'},
    'Mango': {'Name': 'Mango', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Raise your Max HP by 14.', 'Flavor': 'The most coveted forgotten fruit. Impeccably preserved with no signs of Spireblight.'},
    'Old Coin': {'Name': 'Old Coin', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Gain 300 <bold>Gold</bold>.', 'Flavor': 'Unique coins are highly valued for their historical value and rare mettalic composition.'},
    'Pocketwatch': {'Name': 'Pocketwatch', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Whenever you play 3 or less cards during your turn, draw 3 additional cards next turn.', 'Flavor': "The hands seem stuck on the 3 o'clock position."},
    'Prayer Wheel': {'Name': 'Prayer Wheel', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Normal enemies drop an additional card reward.', 'Flavor': 'The wheel continues to spin, never stopping.'},
    'Shovel': {'Name': 'Shovel', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'You can now Dig for loot at <bold>Rest Sites</bold>.', 'Flavor': 'The Spire houses all number of relics from past civilizations and powerful adventurers lost to time. Time to go dig them up!'},
    'Stone Calender': {'Name': 'Stone Calender', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'At the end of turn 7, deal 52 damage to ALL enemies.', 'Flavor': 'The passage of time is imperceptible in the Spire.'},
    'Thread and Needle': {'Name': 'Thread and Needle', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'At the start of each combat, gain 4 <bold>Plated Armor</bold>.', 'Flavor': 'Wrapping the magical thread around your body, you feel harder to the touch.'},
    'Torii': {'Name': 'Torii', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'Whenever you would recieve 5 or less unblocked attack damage, reduce it to 1.', 'Flavor': 'Holding the small Torii, you feel a sense of calm and safety drift through your mind.'},
    'Tungsten Rod': {'Name': 'Tungsten Rod', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'When you would lose HP, lose 1 less.', 'Flavor': "It's very very heavy."},
    'Turnip': {'Name': 'Turnip', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'You can no longer become <bold>Frail</bold>.', 'Flavor': 'Best with Ginger.'},
    'Unceasing Top': {'Name': 'Unceasing Top', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'When you have no cards in your hand during your turn, draw 1 card.', 'Flavor': 'The top continues to spin effortlessly as if your were in a dream.'},
    'Wing Boots': {'Name': 'Wing Boots', 'Class': 'Any', 'Rarity': 'Rare', 'Info': 'You may ignore paths when choosing the next room to travel to up to 3 times.', 'Flavor': 'Stylish.'},
    # Class specific rare relics
    'Champion Belt': {'Name': 'Champion Belt', 'Class': 'Ironclad', 'Rarity': 'Rare', 'Info': 'Whenever you apply <bold>Vulnerable</bold>, also apply 1 <bold>Weak</bold>.', 'Flavor': 'Only the greatest may wear this belt.'},
    "Charon's Ashes": {'Name': "Charon's Ashes", 'Class': 'Ironclad', 'Rarity': 'Rare', 'Info': 'Whenever you <bold>Exhaust</bold> a card, deal 3 damage to ALL enemies.', 'Flavor': 'Charon was said to be the god of rebirth, eternally dying and reviving in a burst of flame.'},
    'Magic Flower': {'Name': 'Magic Flower', 'Class': 'Ironclad', 'Rarity': 'Rare', 'Info': 'Healing is 50% more effective during combat.', 'Flavor': 'A flower long thought extinct, somehow preserved in perfect condition.'},
    'The Specimen': {'Name': 'The Specimen', 'Class': 'Silent', 'Rarity': 'Rare', 'Info': 'Whenever an enemy dies, transfer any <bold>Poison</bold> it had to random enemy.', 'Flavor': '"Fascinating! I found a mutated creature demonstrating astounding toxic properties. Storing a sample for later examination." - Ranwid'},
    'Tingsha': {'Name': 'Tingsha', 'Class': 'Silent', 'Rarity': 'Rare', 'Info': 'Whenever you discard a card during your turn, deal 3 damage to random enemy for each card discarded.', 'Flavor': 'The sound this instrument generates appears to be capable of reverberating to painful levels of volume.'},
    'Tough Bandages': {'Name': 'Tough Bandages', 'Class': 'Silent', 'Rarity': 'Rare', 'Info': 'Whenever you discard a card during your turn, gain 3 <bold>Block</bold>.', 'Flavor': 'Loss gives strength.'},
    'Emotion Chip': {'Name': 'Emotion Chip', 'Class': 'Defect', 'Rarity': 'Rare', 'Info': 'If you lost HP during your previous turn, trigger the passive ability of ALL <bold>Orbs</bold> at the start of your next turn.', 'Flavor': '...<3...?'},
    'Cloak Clasp': {'Name': 'Cloak Clasp', 'Class': 'Watcher', 'Rarity': 'Rare', 'Info': 'At the end of your turn, gain 1 <bold>Block</bold> for each card in your hand.', 'Flavor': 'A simple but sturdy design.'},
    'Golden Eye': {'Name': 'Golden Eye', 'Class': 'Watcher', 'Rarity': 'Rare', 'Info': 'Whenever you <bold>Scry</bold>, <bold>Scry</bold> 2 additional cards.', 'Flavor': 'See into the minds of those nearby, predicting their future moves.'},
    # Shop relics
    'Cauldron': {'Name': 'Cauldron', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'When obtained, brews 5 random potions.', 'Flavor': 'The merchant is actually a rather skilled ption brewer. Buy 4 get 1 free.'},
    'Chemical X': {'Name': 'Chemical X', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Whenever you play an X cost card, its effects are increased by 2.', 'Flavor': 'WARNING: Do not combine with sugar, spice, and everything nice.'},
    'Clockwork Souvenir': {'Name': 'Clockwork Souvenir', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'At the start of each combat, gain 1 <bold>Artifact</bold>.', 'Flavor': 'So many intricate gears.'},
    'Dolly Mirror': {'Name': 'Dolly Mirror', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Upon pick up, obtain an additional copy of a card in your deck.', 'Flavor': 'I look funny in this.'},
    'Frozen Eye': {'Name': 'Frozen Eye', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'When viewing your draw pile, the cards are now shown in order.', 'Flavor': 'Staring into the eye, you see a glimpse of your future.'},
    'Hand Drill': {'Name': 'Hand Drill', 'Class': 'Any', 'Rarity': 'Shop', 'Info': "Whenever you break an enemy's <bold>Block</bold>, apply 2 <bold>Vulnerable</bold>.", 'Flavor': 'Spirals are dangerous.'},
    "Lee's Waffle": {'Name': "Lee's Waffle", 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Raise your Max HP by 7 and heal all of your HP.', 'Flavor': '"Tastiest treat you will find in all the Spire! Baked today just for you."'},
    'Medical Kit': {'Name': 'Medical Kit', 'Class': 'Any', 'Rarity': 'Shop', 'Info': '<bold>Status</bold> cards can now be played. Playing a <bold>Status</bold> will <bold>Exhaust</bold> the card.', 'Flavor': '"Has everything you need! Anti-itch, anti-burn, anti-venom, and more!"'},
    'Membership Card': {'Name': 'Membership Card', 'Class': 'Any', 'Rarity': 'Shop', 'Info': '50% discout on all products!', 'Flavor': '"Bonus membership option for my most valuable customers!"'},
    'Orange Pellets': {'Name': 'Orange Pellets', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Whenever you play a <bold>Power, Attack,</bold> and <bold>Skill</bold> in the same turn, remove ALL of your debuffs.', 'Flavor': 'Made from various fungi found throughout the Spire, they will stave off any affliction.'},
    'Orrery': {'Name': 'Orrery', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Choose and add 5 to your deck.', 'Flavor': '"Once you understand the universe..." - Zoroth'},
    'Prismatic Shard': {'Name': 'Prismatic Shard', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Combat reward screens now contain colorless cards and cards from other colors.', 'Flavor': 'Looking through the shard, you are able to see entirely new perspectives.'},
    'Sling of Courage': {'Name': 'Sling of Courage', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Start each <bold>Elite</bold> combat with 2 <bold>Strength<bold>.', 'Flavor': 'A handy tool for dealing with particalarly tough opponents.'},
    'Strange Spoon': {'Name': 'Strange Spoon', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Cards that <bold>Exhaust</bold> will instead discard 50% of the time.', 'Flavor': 'Staring at the spoon, it appears to bend and twist around before your eyes.'},
    'The Abacus': {'Name': 'The Abacus', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'Gain 6 <bold>Block</bold> when you shuffle your draw pile.', 'Flavor': 'One...Two...Three...'},
    'Toolbox': {'Name': 'Toolbox', 'Class': 'Any', 'Rarity': 'Shop', 'Info': 'At the start of each combat, choose 1 of 3 Colorless cards to add to your hand.', 'Flavor': 'A tool for every job.'},
    # Class specific shop relics
    'Brimstone': {'Name': 'Brimstone', 'Class': 'Ironclad', 'Rarity': 'Shop', 'Info': 'At the start of your turn, gain 2 <bold>Strength</bold> and ALL enemies gain 1 <bold>Strength</bold>.', 'Flavor': 'Emanates an infernal heat.'},
    'Twisted Funnel': {'Name': 'Twisted Funnel', 'Class': 'Silent', 'Rarity': 'Shop', 'Info': 'At the start of each combat, apply 4 <bold>Poison</bold> to ALL enemies.', 'Flavor': "I wouldn't drink out of it."},
    'Runic Capacitor': {'Name': 'Runic Capacitor', 'Class': 'Defect', 'Rarity': 'Shop', 'Info': 'Start each combat with 3 additional <bold>Orb</bold> slots.', 'Flavor': 'More is better.'},
    'Melange': {'Name': 'Melange', 'Class': 'Watcher', 'Rarity': 'Shop', 'Info': 'Whenever you shuffle your draw pile, <bold>Scry</bold> 3.', 'Flavor': 'Mysterious sands from an unknown origin, smells of cinnamon.'},
    # Boss relics
    'Astrolabe': {'Name': 'Astrolabe', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Upon pickup, choose and <bold>Transform</bold> 3 cards, then <bold>Upgrade<bold> them.', 'Flavor': 'A tool to glean inavluable knowledge from the stars.'},
    'Black Star': {'Name': 'Black Star', 'Class': 'Any', 'Rarity': 'Boss', 'Info': '<bold>Elites</bold> now drop 2 relics when defeated.', 'Flavor': 'Originally discovered in the town of the serpent, aside a solitary candle.'},
    'Busted Crown': {'Name': 'Busted Crown', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. On card reward screens, you have 2 less cards to choose from.', 'Flavor': "The Champ's crown... or a pale imitation?"},
    'Calling Bell': {'Name': 'Calling Bell', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Obtain a special <bold>Curse</bold> and 3 relics.', 'Flavor': 'The dark iron bell rang 3 times when you found it, but now it remains silent.'},
    'Coffee Dripper': {'Name': 'Coffee Dripper', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. You can no longer Rest at <bold>Rest Sites</bold>.', 'Flavor': '"Yes, another cup please. Back to work. Back to work!" - The Architect'},
    'Cursed Key': {'Name': 'Cursed Key', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. Whenever you open a non-boss chest, obtain 1 <bold>Curse</bold>.', 'Flavor': 'You can feel the malicious energy emanating from the key. Power comes at a price.'},
    'Ectoplasm': {'Name': 'Ectoplasm', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. You can no longer obtain <bold>Gold</bold>.', 'Flavor': 'This blob of slime and energy seems to pulse with life.'},
    'Empty Cage': {'Name': 'Empty Cage', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Upon pickup, remove 2 cards from your deck.', 'Flavor': '"How unusual to cage that which you worship." - Ranwid'},
    'Fusion Hammer': {'Name': 'Fusion Hammer', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. You can no longer Smith at <bold>Rest Sites</bold>.', 'Flavor': 'Once wielded, the owner can never let go.'},
    "Pandora's Box": {'Name': "Pandora's Box", 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Transform all <bold>Strikes</bold> and <bold>Defends</bold>.', 'Flavor': 'You have a bad feeling about opening this.'},
    "Philosopher's Stone": {'Name': "Philosopher's Stone", 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. ALL enemies start with 1 <bold>Strength</bold>.', 'Flavor': 'Raw energy emanates from the stone, empowering all nearby.'},
    'Runic Dome': {'Name': 'Runic Dome', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. You can no longer see enemy intents.', 'Flavor': 'The runes are indecipherable.'},
    'Runic Pyramid': {'Name': 'Runic Pyramid', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'At the end of your turn, you no longer discard your hand.', 'Flavor': 'The runes are indecipherable.'},
    'Sacred Bark': {'Name': 'Sacred Bark', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Double the effectiveness of potions.', 'Flavor': 'A bark rumered to originate from the World Tree.'},
    "Slaver's Collar": {'Name': "Slaver's Collar", 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'During <bold>Boss</bold> and <bold>Elite</bold> encounters, gain 1 <bold>Energy</bold> at the start of each turn.', 'Flavor': 'Rusty miserable chains.'},
    'Snecko Eye': {'Name': 'Snecko Eye', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Draw 2 additonal cards each turn. You start each combat <bold>Confused</bold>.', 'Flavor': 'The eye of a fallen snecko. Much larger than you imagined.'},
    'Sozu': {'Name': 'Sozu', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. You can no longer obtain potions.', 'Flavor': 'You notice that magical liquids seem to lose their properties when near this relic.'},
    'Tiny House': {'Name': 'Tiny House', 'Class': 'Any', 'Rarity': 'Boss', 'Info': 'Obtain 1 potion. Gain 50 <bold>Gold</bold>. Raise your Max HP by 5. Obtain 1 card. <bold>Upgrade</bold> 1 card.', 'Flavor': '"A near-perfect implementation of miniaturization. My finest work to date, but still not adequate." - The Architect'},
    'Velvet Choker': {'Name': 'Velvet Choker', 'Class': 'Any', 'Rarity': 'Boss', 'Info': "Gain 1 <bold>Energy</bold> at the start of each turn. You can't play more than 6 cards per turn.", 'Flavor': '"Immense power, but too limited." - Kublai the Great'},
    # Class specific boss relics
    'Black Blood': {'Name': 'Black Blood', 'Class': 'Ironclad', 'Rarity': 'Boss', 'Info': 'Replaces <bold>Burning Blood</bold>. At the end of each combat, heal 12 HP.', 'Flavor': 'The rage grows darker.'},
    'Mark of Pain': {'Name': 'Mark of Pain', 'Class': 'Ironclad', 'Rarity': 'Boss', 'Info': 'Gain 1 <bold>Energy</bold> at the start of each turn. Start combat with 2 <bold>Wounds</bold> in your draw pile.', 'Flavor': 'This brand was used by the northern tribes to signify warriors who had mastered pain in battle.'},
    'Runic Cube': {'Name': 'Runic Cube', 'Class': 'Ironclad', 'Rarity': 'Boss', 'Info': 'Whenever you lose HP, draw 1 card.', 'Flavor': 'The runes are indecipherable.'},
    'Ring of the Serpent': {'Name': 'Ring of the Serpent', 'Class': 'Silent', 'Rarity': 'Boss', 'Info': 'Replaces <bold>Ring of the Snake</bold>. At the start of each turn, draw 1 additional card.', 'Flavor': 'Your ring has morphed and changed forms.'},
    'Wrist Blade': {'Name': 'Wrist Blade', 'Class': 'Silent', 'Rarity': 'Boss', 'Info': 'Attacks that cost 0 deal 4 additional damage.', 'Flavor': 'Handy for assasinations.'},
    'Hovering Kite': {'Name': 'Hovering Kite', 'Class': 'Silent', 'Rarity': 'Boss', 'Info': 'The first time you discard a card each turn, gain 1 <bold>Energy</bold>.', 'Flavor': 'The Kite floats around you in battle, propelled by a mysterious force.'},
    'Frozen Core': {'Name': 'Frozen Core', 'Class': 'Defect', 'Rarity': 'Boss', 'Info': 'Replaces <bold>Cracked Core</bold>. If you end your turn with empty orb slots, Channel 1 <bold>Frost</bold> orb.', 'Flavor': 'The crack in your core has been filled with a pulsating cold energy.'},
    'Inserter': {'Name': 'Inserter', 'Class': 'Defect', 'Rarity': 'Boss', 'Info': 'Every 2 turns, gain 1 <bold>Orb</bold> slot.', 'Flavor': 'Push. Pull. Stack. Repeat.'},
    'Nuclear Battery': {'Name': 'Nuclear Battery', 'Class': 'Defect', 'Rarity': 'Boss', 'Info': 'At the start of each combat, Channel 1 <bold>Plasma</bold> orb.', 'Flavor': 'Ooooh...'},
    'Holy Water': {'Name': 'Holy Water', 'Class': 'Watcher', 'Rarity': 'Boss', 'Info': 'Replaces <bold>Pure Water</bold>. At the start of combat, add 3 <bold>Miracle</bold> cards to your hand.', 'Flavor': 'Collected from a time before the Spire.'},
    'Violet Lotus': {'Name': 'Violet Lotus', 'Class': 'Watcher', 'Rarity': 'Boss', 'Info': 'Whenever you exit <bold>Calm</bold>, gain an additional <bold>Energy</bold>.', 'Flavor': 'The old texts describe that the surface of “mana pools” were littered with these flowers.'},
    # Event relics
    'Bloody Idol': {'Name': 'Bloody Idol', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Forgotten Altar', 'Info': 'Whenever you gain <bold>Gold</bold>, heal 5 HP.', 'Flavor': 'The idol now weeps a constant stream of blood.'},
    'Cultist Headpiece': {'Name': 'Cultist Headpiece', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Face Trader', 'Info': 'You feel more talkative. CAW! CAAAW', 'Flavor': 'Part of the Flock!'},
    'Enchiridion': {'Name': 'Enchiridion', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Cursed Tome', 'Info': 'At the start of each combat, add a random <bold>Power</bold> card to your hand. It costs 0 until the end of your turn.', 'Flavor': 'The legendary journal of an ancient lich.'},
    'Face of Cleric': {'Name': 'Face of Cleric', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Face Trader', 'Info': 'Raise your Max HP by 1 after each combat', 'Flavor': 'Everybody loves Cleric.'},
    'Golden Idol': {'Name': 'Golden Idol', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Golden Idol', 'Info': 'Enemies drop 25% more Gold.', 'Flavor': 'Made of solid gold, you feel richer just holding it.'},
    'Gremlin Visage': {'Name': 'Gremlin Visage', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Face Trader', 'Info': 'Start each combat with 1 <yellow>Weak</yellow>.', 'Flavor': 'Time to run.'},
    'Mark of the Bloom': {'Name': 'Mark of the Bloom', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Mind Bloom', 'Info': 'You can no longer heal.', 'Flavor': 'In the Beyond, thoughts and reality are one.'},
    'Mutagenic Strength': {'Name': 'Mutagenic Strength', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Augmenter', 'Info': 'Start each comabat with 3 <bold>Strength</bold> that is lost at the end of your turn.', 'Flavor': '"The results seem fleeting, triggering when the subject is in danger." - Unknown'},
    "N'loth's Gift": {'Name': "N'loth's Gift", 'Class': 'Any', 'Rarity': 'Event', 'Source': "N'loth", 'Info': 'The next non-boss chest you open is empty.', 'Flavor': "The strange gift from N'loth. Whenever you try and unwrap it, another wrapped box of the same size lies within."},
    "N'loth's Hungry Face": {'Name': "N'loth's Hungry Face", 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Face Trader', 'Info': 'The next non-boss <yellow>Chest</yellow> you open is empty.', 'Flavor': 'You feel hungry.'},
    'Necronomicon': {'Name': 'Necronomicon', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Necronomicon', 'Info': 'The first <bold>Attack</bold> played each turn that has a cost of 2 or more is played twice.', 'Flavor': 'Only a fool would try and harness this evil power. At night your dreams are haunted by images of the book devouring your mind.'},
    "Neow's Lament": {'Name': "Neow's Lament", 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Cursed Tome', 'Info': 'Enemies in your first 3 combats have 1 HP.', 'Flavor': 'The blessing of lamentation bestowed by Neow.'},
    "Nilry's Codex": {'Name': "Nilry's Codex", 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Cursed Tome', 'Info': 'At the end of each turn, you can choose 1 of 3 random cards to shuffle into your draw pile.', 'Flavor': "Created by the infamous game master himself. Said to expand one's mind."},
    'Odd Mushroom': {'Name': 'Odd Mushroom', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Hypnotizing Colored Mushrooms', 'Info': 'When <bold>Vulnerable</bold>, take 25% more damage rather than 50%.', 'Flavor': '"After consuming trichella parastius I felt larger and less... susceptible." - Ranwid'},
    'Red Mask': {'Name': 'Red Mask', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Masked Bandits or Tome of Lord Red Mask', 'Info': 'At the start of combat, apply 1 <bold>Weak</bold> to ALL enemies.', 'Flavor': 'This very stylish-looking mask belongs to the leader of the Red Mask Bandits. Technically that makes you the leader now?'},
    'Spirt Poop': {'Name': 'Spirit Poop', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Bonfire Spirits', 'Info': "It's unpleasant.", 'Flavor': 'The charred remains of your offering to the spirits.'},
    'Ssserpent Head': {'Name': 'Ssserpent Head', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Face Trader', 'Info': 'Whenever you enter a <bold>?</bold> room, gain 50 Gold.', 'Flavor': 'The most fulfilling of lives is that in which you can buy anything!'},
    'Warped Tongs': {'Name': 'Warped Tongs', 'Class': 'Any', 'Rarity': 'Event', 'Source': 'Ominous Forge', 'Info': 'At the start of your turn, upgrade a random card in your hand for the rest of combat.', 'Flavor' : 'The cursed tongs emit a strong desire to return to where they were stolen from.'},
    # Circlet can only be obtained once you have gotten all other relics.
    'Circlet': {'Name': 'Circlet', 'Class': 'Any', 'Rarity': 'Special', 'Info': 'Looks pretty.', 'Flavor': 'You ran out of relics to find. Impressive!'}
}
golden_multi = int(player.golden_bark) + 1
potions = {
    # Common | All Classes
    'Attack Potion': {'Name': 'Attack Potion', 'Cards': 1 * golden_multi, 'Card Type': 'Attack', 'Class': 'All', 'Rarity': 'Common', 'Info': f'Add {"1" if not player.golden_bark else "2 copies"} of 3 random Attack cards to your hand, {"it" if not player.golden_bark else "they"} costs 0 this turn'},
    'Power Potion': {'Name': 'Power Potion', 'Cards': 1 * golden_multi, 'Card Type': 'Power', 'Class': 'All', 'Rarity': 'Common', 'Info': f'Add {"1" if not player.golden_bark else "2 copies"} of 3 random Power cards to your hand, {"it" if not player.golden_bark else "they"} costs 0 this turn'},
    'Skill Potion': {'Name': 'Skill Potion', 'Cards': 1 * golden_multi, 'Card Type': 'Skill', 'Class': 'All', 'Rarity': 'Common', 'Info': f'Add {"1" if not player.golden_bark else "2 copies"} of 3 random Skill cards to your hand, {"it" if not player.golden_bark else "they"} costs 0 this turn'},
    'Colorless Potion': {'Name': 'Colorless Potion', 'Cards': 1 * golden_multi, 'Card Type': 'Colorless', 'Class': 'All', 'Rarity': 'Common', 'Info': f'Choose {"1" if not player.golden_bark else "2 copies"} of 3 random Colorless cards to add to your hand, {"it" if not player.golden_bark else "they"} costs 0 this turn'},
    'Block Potion': {'Name': 'Block Potion', 'Block': 12 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': f'Gain {12 * golden_multi} Block'},
    'Dexterity Potion': {'Name': 'Dexterity Potion', 'Dexterity': 2 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': f'Gain {2 * golden_multi} Dexterity'},
    'Energy Potion': {'Name': 'Energy Potion', 'Energy': 2 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': f'Gain {2 * golden_multi} Energy'},
    'Explosive Potion': {'Name': 'Explosive Potion', 'Damage': 10 * golden_multi, 'Target': 'All', 'Class': 'All', 'Rarity': 'Common', 'Info': f'Deal {10 * golden_multi} damage to ALL enemies'},
    'Fear Potion': {'Name': 'Fear Potion', 'Vulnerable': 3 * golden_multi, 'Target': 'Enemy', 'Class': 'All', 'Rarity': 'Common', 'Info': f'Apply {3 * golden_multi} Vulnerable'},
    'Fire Potion': {'Name': 'Fire Potion', 'Damage': 20 * golden_multi, 'Target': 'Enemy', 'Class': 'All', 'Rarity': 'Common', 'Info': f'Deal {20 * golden_multi} damage to target enemy'},
    'Flex Potion': {'Name': 'Flex Potion', 'Strength': 5 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': f'Gain {5 * golden_multi} Strength. At the end of your turn lose {5 * golden_multi} Strength'},
    'Speed Potion': {'Name': 'Speed Potion', 'Dexterity': 5 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': f'Gain {5 * golden_multi} Dexterity. At the end of your turn, lose {5 * golden_multi} Dexterity'},
    'Strength Potion': {'Name': 'Strength Potion', 'Strength': 2 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': f'Gain {2 * golden_multi} Strength'},
    'Swift Potion': {'Name': 'Swift Potion', 'Cards': 3 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': 'Draw 3 cards'},
    # Uncommon | All Classes
    'Ancient Potion': {'Name': 'Ancient Potion', 'Artifact': 1 * golden_multi, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': f'Gain {1 * golden_multi} Artifact'},
    'Distilled Chaos': {'Name': 'Distilled Chaos', 'Cards': 3 * golden_multi, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': f'Play the top {3 * golden_multi} cards of your draw pile'},
    'Duplication Potion': {'Name': 'Duplication Potion', 'Cards': 1 * golden_multi, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': f'This turn, the next {"card is" if not player.golden_bark else "2 cards are"} played twice.'},
    'Essence of Steel': {'Name': 'Essence of Steel', 'Plated Armor': 4 * golden_multi, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': f'Gain {4 * golden_multi} <light-cyan>Plated Armor</light-cyan>'},
    "Gambler's Brew": {'Name': "Gambler's Brew", 'Class': 'All', 'Rarity': 'Uncommon', 'Info': 'Discard any number of cards, then draw that many'},
    'Liquid Bronze': {'Name': 'Liquid Bronze', 'Thorns': 3 * golden_multi, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': f'Gain {3 * golden_multi} Thorns'},
    'Liquid Memories': {'Name': 'Liquid Memories', 'Cards': 1 * golden_multi, 'Class': 'All', 'Rarity': 'Uncommon', 'Info': f'Choose {"a card" if not player.golden_bark else "2 cards"} in your discard pile and return {"it" if player.golden_bark else "them"} to your hand. {"It" if not player.golden_bark else "They"} costs 0 this turn'},
    'Regen Potion': {'Name': 'Regen Potion', 'Regen': 5 * golden_multi, 'Class': 'All', 'Rarity': 'Common', 'Info': f'Gain {5 * golden_multi} Regeneration'},
    # Rare | All Classes
    'Cultist Potion': {'Name': 'Cultist Potion', 'Ritual': 1 * golden_multi, 'Class': 'All', 'Rarity': 'Rare', 'Info': f'Gain {1 * golden_multi} Ritual'},
    'Entropic Brew': {'Name': 'Entropic Brew', 'Potions': player.max_potions - len(player.potions) + 1, 'Class': 'All', 'Rarity': 'Rare', 'Info': 'Fill all your empty potion slots with random potions'},
    'Fairy in a Bottle': {'Name': 'Fairy in a Bottle', 'Playable': False, 'Revive Health': math.floor(player.max_health * (0.3 * golden_multi)), 'Class': 'All', 'Rarity': 'Rare', 'Info': f'When you would die, heal to {30 * golden_multi}% of your Max HP({math.floor(player.max_health * (0.3 * golden_multi))}) instead and discard this potion'},
    'Fruit Juice': {'Name': 'Fruit Juice', 'Playable Everywhere?': True, 'Max Health': 5 * golden_multi, 'Class': 'All', 'Rarity': 'Rare', 'Info': f'Gain {5 * golden_multi} Max HP'},
    'Smoke Bomb': {'Name': 'Smoke Bomb', 'Escape from boss': False, 'Target': 'Nothing', 'Class': 'All', 'Rarity': 'Rare', 'Info': 'Escape from a non-boss combat. You recieve no rewards.'},
    'Sneko Oil': {'Name': 'Snecko Oil', 'Cards': 5 * golden_multi, 'Range': (0, player.max_energy + 1), 'Class': 'All', 'Rarity': 'Rare', 'Info': f'Draw {5 * golden_multi} cards. Randomize the costs of all cards in your hand for the rest of combat.'},
    # Ironclad Potions
    'Blood Potion': {'Name': 'Blood Potion', 'Health': math.floor(player.max_health * (0.2 * golden_multi)), 'Class': 'Ironclad', 'Rarity': 'Uncommon', 'Info': f'Heal for {20 * golden_multi}% of your Max HP({math.floor(player.max_health * (0.2 * golden_multi))})'},
    'Elixir': {'Name': 'Elixir', 'Class': 'Ironclad', 'Rarity': 'Uncommon', 'Info': 'Exhaust any number of cards in your hand'},
    'Heart of Iron': {'Name': 'Heart of Iron', 'Metallicize': 8 * golden_multi, 'Class': 'Ironclad', 'Rarity': 'Rare', 'Info': f'Gain {8 * golden_multi} <light-cyan>Metallicize</light-cyan>'},
    # Silent potion
    'Poison Potion': {'Name': 'Poison Potion', 'Poison': 6 * golden_multi, 'Target': 'Enemy', 'Class': 'Silent', 'Rarity': 'Common', 'Info': f'Apply {6 * golden_multi} <light-cyan>Poison</light-cyan> to target enemy'},
    'Cunning Potion': {'Name': 'Cunning Potion', 'Shivs': 3 * golden_multi, 'Card': 'placehold', 'Class': 'Silent', 'Rarity': 'Uncommon', 'Info': f'Add {3 * golden_multi} <bold>Upgraded Shivs</bold> to your hand'}, # Shiv card doesn't not exist yet
    'Ghost in a Jar': {'Name': 'Ghost in a Jar', 'Intangible': 1 * golden_multi, 'Class': 'Silent', 'Rarity': 'Rare', 'Info': f'Gain {1 * golden_multi} Intangible'},
    # Defect Potions
    'Focus Potion': {'Name': 'Focus Potion', 'Focus': 2 * golden_multi, 'Class': 'Defect', 'Rarity': 'Common', 'Info': f'Gain {2 * golden_multi} Focus'},
    'Potion of Capacity': {'Name': 'Potion of Capacity', 'Orb Slots': 2 * golden_multi, 'Class': 'Defect', 'Rarity': 'Uncommon', 'Info': f'Gain {2 * golden_multi} Orb slots'},
    'Essence of Darkness': {'Name': 'Essence of Darkness', 'Dark': player.orb_slots * golden_multi, 'Class': 'Defect', 'Rarity': 'Rare', 'Info': f'Channel {1 * golden_multi} Dark for each orb slot'},
    # Watcher Potions
    'Bottled Miracle': {'Name': 'Bottled Miracle', 'Miracles': 2 * golden_multi, 'Card': 'placehold', 'Class': 'Watcher', 'Rarity': 'Common', 'Info': f'Add {2 * golden_multi} Miracles to your hand'},
    'Stance Potion': {'Name': 'Stance Potion', 'Stances': ['Calm', 'Wrath'], 'Class': 'Watcher', 'Rarity': 'Uncommon', 'Info': 'Enter Calm or Wrath'},
    'Ambrosia': {'Name': 'Ambrosia', 'Stance': 'Divinity', 'Class': 'Watcher', 'Rarity': 'Rare', 'Info': 'Enter Divinity Stance'}
}
player.deck = [cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Bash']]
# Enemies
enemy_encounters = [[Enemy([48, 54], 0, "Cultist", [['self.buff("Ritual", 3, True, True, "Incantation")'], ['self.attack(6, 1, True, True, "Dark Strike")']])],
              [Enemy([40, 44], 0, "Jaw Worm", [['self.attack(11, 1, True, False, "Chomp")'], ['self.attack(7, 1, True, False, "Thrash")', 'self.blocking(5, False, True)'], ['self.buff("Strength", 3, True, False, "Bellow")', 'self.blocking(6, False, True)']])]]
