import math
import sys
import random
from time import sleep
from copy import deepcopy
from ansi_tags import ansiprint
from items import relics, cards
from utility import active_enemies, combat_turn, DURATION_EFFECTS, PLAYER_BUFFS, PLAYER_DEBUFFS, ENEMY_BUFFS, ENEMY_DEBUFFS, NON_STACKING_EFFECTS, all_effects, list_input, clear, modify_energy_cost, calculate_actual_damage

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
        self.in_combat = False
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
        for debuff in PLAYER_DEBUFFS:
            if debuff not in NON_STACKING_EFFECTS:
                self.debuffs[debuff] = 0
            else:
                self.debuffs[debuff] = False
        self.buffs: dict[str: int] = {}
        for buff in PLAYER_BUFFS:
            if buff not in NON_STACKING_EFFECTS:
                self.buffs[buff] = 0
            else:
                self.buffs[buff] = False
        # Alternate debuff/buff effects
        self.combusts_played = 0
        self.the_bomb_countdown = 3
        self.deva_energy = 1
        # Relic buffs
        self.pen_nib_attacks: int = 0
        self.ancient_tea_set: bool = False
        self.attacks_played_this_turn: bool = False  # Used for the Art of War relic
        self.taken_damage: bool = False  # Used for the Centennial Puzzle relic
        self.gold_on_card_add: bool = False  # Used for the Ceramic Fish relic
        self.happy_flower: int = 0
        self.block_curses: int = 0  # Used for the Omamori relic
        self.nunckaku_attacks: int = 0
        self.starting_strength: int = 0  # Used for the Red Skull and Vajra relic
        self.golden_bark: bool = False  # Used for the Golden Bark relic
        # Used for the Molten, Toxic, and Frozen Egg relics
        self.upgrade_attacks = False
        self.upgrade_skills = False
        self.upgrade_powers = False
        self.red_skull_active = False
        self.inked_cards = 0  # Used for the Ink Bottle relic
        self.kunai_attacks = 0  # Used for the Kunai relic
        self.letter_opener_skills = 0  # Used for the Letter Opener relic
        self.ornament_fan_attacks = 0  # Used for the Ornamental Fan relic
        self.meat_on_the_bone = False
        self.darkstone_health = False
        self.shuriken_attacks = 0
        self.draw_shuffles = 0 # Used for the Sundial relic
        self.incense_turns = 0 # Used for the Incense Burner relic
        self.girya_charges = 3 # Stores how many times the player can gain Energy from Girya
        self.plays_this_turn = 0 # Counts how many cards the played plays each turn
        self.stone_calender = 0

    def use_card(self, card: dict, target: object, exhaust, pile) -> None:
        """
        Uses a card
        Wow!
        """
        if card.get('Target') == 'Single':
            card['Function'](target, card, self)
        elif card.get('Target') in ('Area', 'Random'):
            card['Function'](active_enemies, card, self)
        elif card.get('Target') == 'Yourself':
            card['Function'](card, self)
        else:
            ansiprint("<red>Card does not have a 'Target' key</red>")
            sys.exit(1)
        if card.get('Type') == 'Attack' and relics['Pen Nib'] in self.relics:
            self.pen_nib_attacks += 1
        if card.get('Type') == 'Attack' and relics['Nunchaku'] in self.relics:
            self.nunckaku_attacks += 1
            if self.nunckaku_attacks == 10:
                self.energy += 1
                ansiprint('You gained 1 Energy from <bold>Nunckaku</bold>.')
                self.nunckaku_attacks = 0
        self.on_card_play(card)
        if self.buffs['Corruption']:
            exhaust = True
        if exhaust is True or card.get('Exhaust') is True:
            ansiprint(f"{card['Name']} was <bold>Exhausted</bold>.")
            self.move_card(card, self.exhaust_pile, pile, True)
        else:
            self.move_card(card, self.discard_pile, pile, True)

        if self.buffs['Double Tap'] > 0 and card.get('Type') == 'Attack':
            self.buffs['Double Tap'] -= 1
            sleep(1.5)
            clear()
            self.use_card(card, target, True, pile)
        # Medical Kit allows Status cards to played
        if card.get('Type') == 'Status' and relics['Medical Kit'] in player.relics:
            exhaust = True
        elif card.get('Type') == 'Curse' and relics['Blue Candle'] in player.relics:
            self.take_sourceless_dmg(1)
            exhaust = True

    def on_relic_pickup(self, relic):
        self.gold_on_card_add = relic['Name'] == "Ceramic Fish"
        self.max_potions += 2 if relic['Name'] == 'Potion Belt' else 0
        self.starting_strength += int(relic['Name'] == 'Vajra')
        if relic['Name'] in ('Bottled Flame', 'Bottled Lightning', 'Bottled Tornado'):
            relic_to_type = {'Bottled Flame': 'Attack', 'Bottled Lightning': 'Skill', 'Bottled Tornado': 'Power'}
            self.bottle_card(relic_to_type[relic['Name']])
        if 'Egg' in relic.get('Name'):
            relic_variables = {'Molten Egg': self.upgrade_attacks,
                              'Frozen Egg': self.upgrade_skills,
                              'Toxic Egg': self.upgrade_powers}
            relic_variables[relic['Name']] = True

        if relic['Name'] in ('Whetstone', 'War Paint'):
            valid_card_types = {'Whetstone': 'Attack', 'War Paint': 'Skill'}
            valid_cards = [card for card in self.deck if card.get('Type') == valid_card_types[relic['Name']]]
            ansiprint(f"<bold>{relic['Name']}</bold>:")
            for _ in range(min(len(valid_cards), 2)):
                chosen_card = random.randint(0, len(self.deck) - 1)
                self.card_actions(self.deck[chosen_card], chosen_card, 'Upgrade', self.deck, valid_cards)
        if relic.get('Name') in ('Strawberry', 'Pear', 'Mango'):
            health_values = {'Strawberry': 7, 'Pear': 10, 'Mango': 14}
            self.health_actions(health_values[relic['Name']], 'Max Health')
        _ = self.gain_gold(300) if relic['Name'] == 'Old Coin' else None
        self.card_reward_choices += 1 if relic['Name'] == 'Question Card' else 0

    def on_card_play(self, card):
        if relics['Kunai'] in self.relics and card.get('Type') == 'Attack':
            self.kunai_attacks += 1
            if self.kunai_attacks == 3:
                ansiprint("<bold>Kunai</bold> activated: ", end='')
                self.buff("Dexterity", 1, False)
                self.kunai_attacks = 0
        if relics['Ornamental Fan'] in self.relics and card.get('Type') == 'Attack':
            self.ornament_fan_attacks += 1
            if self.ornament_fan_attacks == 3:
                ansiprint("<bold>Ornamental Fan</bold> activated: ", end='')
                self.blocking(4, False)
        if relics['Letter Opener'] in self.relics and card.get('Type') == 'Skill':
            self.letter_opener_skills += 1
            if self.letter_opener_skills == 3:
                ansiprint("<bold>Letter Opener</bold> activated")
                for enemy in active_enemies:
                    self.attack(5, enemy)
                self.letter_opener_skills = 0
        if relics['Mummified Hand'] in self.relics and card.get('Type') == 'Power':
            ansiprint('<bold>Mummified Hand</bold> activated: ', end='')
            target_card = random.choice(self.hand)
            target_card = modify_energy_cost(0, 'Set', target_card)
        if relics['Shuriken'] in self.relics and card.get('Type') == 'Attack':
            self.shuriken_attacks += 1
            if self.shuriken_attacks == 3:
                ansiprint('<bold>Shuriken</bold> activated: ', end='')
                self.buff('Strength', 1, False)
        if relics['Ink Bottle'] in self.relics:
            self.inked_cards += 1
            if self.inked_cards == 10:
                ansiprint("<bold>Ink Bottle</bold> activated: ", end='')
                self.draw_cards(True, 1)
                self.inked_cards = 0
        if relics['Duality'] in self.relics and card.get('Type') == 'Attack':
            ansiprint('<bold>Duality</bold> activated: ', end='')
            self.buff('Dexterity', 1, False)
        if relics['Bird-Faced Urn'] in self.relics and card.get('Type') == 'Power':
            ansiprint('<bold>Bird-Faced Urn<bold> activated: ', end='')
            self.health_actions(2, 'Heal')

    def draw_cards(self, middle_of_turn: bool, draw_cards: int = 0):
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
                if relics['Sundial'] in self.relics:
                    self.draw_shuffles += 1
                    if self.draw_shuffles == 3:
                        ansiprint('<bold>Sundial</bold> gave you 2 <italic><red>Energy</red></italic>')
                        self.energy += 2
                        self.draw_shuffles = 0
                ansiprint("<bold>Discard pile shuffled into draw pile.</bold>")
            self.hand.extend(player.draw_pile[-draw_cards:])
            # Removes those cards
            player.draw_pile = player.draw_pile[:-draw_cards]
            print(f"{self.name} drew {draw_cards} cards.")
            for card in player.hand[-draw_cards:]:
                if card['Type'] in ('Status', 'Curse') and self.buffs['Fire Breathing'] > 0:
                    for enemy in active_enemies:
                        self.attack(self.buffs['Fire Breathing'], enemy)
                if card['Type'] == 'Status' and self.buffs['Evolve'] > 0:
                    clear()
                    self.draw_cards(True, self.buffs['Evolve'])
            break

    def blocking(self, block: int, card: bool = True):
        '''Gains [block] Block. Cards are affected by Dexterity and Frail.'''
        block_affected_by = ''
        if card:
            block += self.buffs["Dexterity"]
            if self.buffs["Dexterity"] > 0:
                block_affected_by += f'{self.buffs["Dexterity"]} <{"light-cyan" if self.buffs["Dexterity"] > 0 else "red"}>Dexterity</{"light-cyan" if self.buffs["Dexterity"] > 0 else "red"}>({"+" if self.buffs["Dexterity"] > 0 else "-"}{self.buffs["Dexterity"]} Block) | '
            if self.debuffs["Frail"] > 0 and card:
                block = math.floor(block * 0.75)
                block_affected_by += '<light-cyan>Frail</light-cyan> (x0.75 block) | '
        self.block += block
        ansiprint(f'{self.name} gained {block} <blue>Block</blue>')
        if self.buffs['Juggernaut'] > 0:
            self.attack(self.buffs['Juggernaut'], random.choice(active_enemies))
        print('Affected by:')
        ansiprint(block_affected_by if block_affected_by else 'Nothing')

    def health_actions(self, heal: int, heal_type: str):
        '''If [heal_type] is 'Heal', you heal for [heal] HP. If [heal_type] is 'Max Health', increase your max health by [heal].'''
        if heal_type == "Heal":
            heal = round(heal * 1.5 if self.in_combat else 1)
            self.health += heal
            self.health = min(self.health, self.max_health)
            ansiprint(f"You heal <green>{min(self.max_health - self.health, heal)}</green> <light-blue>HP</light-blue>")
            if self.health >= math.floor(self.health * 0.5) and relics['Red Skull'] in self.relics:
                ansiprint('<bold>Red Skull</bold> <red>deactivates</red>.')
                self.starting_strength -= 3
        elif heal_type == "Max Health":
            self.max_health += heal
            self.health += heal
            ansiprint(f"Your Max HP is {'increased' if heal > 0 else 'decreased'} by <{'light-blue' if heal > 0 else 'red'}>{heal}</{'light-blue' if heal > 0 else 'red'}>")

    def card_actions(self, subject_card: dict, index: int, action: str, pile: list[dict], card_pool: list[dict] = None):
        '''[action] == 'Remove', remove [card] from your deck.
        [action] == 'Upgrade', Upgrade [card]
        [action] == 'Transform', transform a card into another random card.
        [action] == 'Store', (Only in the Note From Yourself event) stores a card to be collected from the event in another run.
        '''
        if card_pool is None:
            card_pool = cards
        while True:
            if action == "Remove":
                del pile[index]
                break
            elif action == 'Transform':
                # Curse cards can only be transformed into other Curses
                if subject_card.get('Type') == 'Curse':
                    options = [valid_card for valid_card in cards.values() if valid_card.get('Type') == 'Curse' and valid_card.get('Rarity') != 'Special']
                else:
                    options = [valid_card for valid_card in cards.values() if valid_card.get('Class') == valid_card.get('Class') and valid_card.get('Type') not in ('Status', 'Curse', 'Special') and valid_card.get('Upgraded') is not True and valid_card.get('Rarity') != 'Basic']
                while True:
                    new_card = random.choice(options)
                    if new_card == subject_card:
                        continue
                    del pile[index]
                    player.deck.insert(index, new_card)
                    break
                break
            elif action == 'Upgrade':
                if "Searing Blow" not in subject_card['Name']:
                    effects_plus: dict = subject_card.pop('Effects+')
                    subject_card['Name'] += '+'
                    for stat, new_value in effects_plus.items():
                        subject_card[stat] = new_value
                    subject_card['Upgraded'] = True
                else:
                    n = subject_card['Upgrade Count']
                    n += 1
                    subject_card['Name'] += f"+{n}"
                    subject_card['Damage'] = n * (n + 7) / 2 + 12
                    subject_card['Info'] = f"Deal Σ{subject_card['Damage']}. Can be <bold>upgraded</bold> any number of times."

                ansiprint(f"{subject_card['Name'].replace('+', '')} was upgraded to <green>{subject_card['Name']}</green>")
                break

    def show_status(self, full_view=False, combat=True):
        if combat is True:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)"
            for buff in self.buffs:
                if buff not in NON_STACKING_EFFECTS and self.buffs[buff] > 0:
                    status += f" | <buff>{buff}</buff>: {self.buffs[buff]}"
                elif buff in NON_STACKING_EFFECTS and self.buffs[buff] is True:
                    status += f" | <buff>{buff}</buff>"
            for debuff in self.debuffs:
                if debuff not in NON_STACKING_EFFECTS and self.debuffs[debuff] > 0:
                    status += f" | <red>{debuff}</red>: {self.debuffs[debuff]}"
                elif debuff in NON_STACKING_EFFECTS and self.debuffs[debuff] is True:
                    status += f" | <red>{debuff}</red>"
        else:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <yellow>{self.gold} Gold</yellow>)"
        ansiprint(status, '' if status == f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)" else '\n'
)
        if full_view is True:
            # int() function used to account for boolean variables.
            for buff in self.buffs:
                # .replace() method is used to replace any variable values with their current values
                if int(self.buffs[buff]) > 0:
                    ansiprint(f"<light-cyan>{buff}</light-cyan>: {all_effects[buff]}".replace("X", self.buffs[buff]))
            for debuff in self.debuffs:
                if int(self.debuffs[debuff]) > 0:
                    ansiprint(f"<red>{debuff}</red>: {all_effects[debuff]}".replace("X", self.debuffs[debuff]))
        print()

    def end_player_turn(self):
        self.discard_pile.extend(self.hand)
        self.hand = []
        self.end_of_turn_relics()
        sleep(1.5)
        clear()

    def move_card(self, card, move_to, from_location, cost_energy, shuffle=False):
        if cost_energy is True:
            energy_cost = eval(str(card['Energy']))
            self.energy -= energy_cost
        from_location.remove(card)
        if shuffle is True:
            move_to.insert(random.randint(0, len(move_to) - 1), card)
        else:
            move_to.append(card)
        if self.buffs["Dark Embrace"] > 0 and move_to == self.exhaust_pile:
            self.draw_cards(True, 1)
        if relics['Dead Branch'] in self.relics and move_to == self.exhaust_pile:
            self.hand.append(deepcopy(random.choice([card for card in cards if card.get('Upgraded') is not True and card.get('Class') == self.player_class])))
        if relics["Charon's Ashes"] in self.relics and move_to == self.exhaust_pile:
            for enemy in active_enemies:
                self.attack(3, enemy)

    def curse_status_effects(self):
        if cards['Burn'] in self.relics:
            self.take_sourceless_dmg(2)

    def attack(self, dmg,  target: 'Enemy', card=None, ignore_block=False):
        dmg_affected_by: str = ''
        if card is not None and card.get('Type') not in ('Status', 'Curse'):
            dmg = dmg + self.buffs['Strength'] * card.get("Strength Multi", 1) + self.buffs['Vigor']
            if relics['Strike Dummy'] in self.relics and 'strike' in card.get('Name').lower():
                dmg += 3
                dmg_affected_by += "<bold>Strike Dummy</bold>(+3 dmg) | "
            if self.debuffs["Weak"] > 0 and card:
                dmg = math.floor(dmg * 0.75)
                dmg_affected_by += "<debuff>Weak</debuff>(x0.75 dmg) | "
            if target.debuffs["Vulnerable"] > 0:
                dmg = math.floor(dmg * (1.50 + 0 if relics['Paper Phrog'] not in self.relics else 0.25))
                dmg_affected_by += f"<debuff>Vulnerable</debuff>(x{'1.5' if relics['Paper Phrog'] not in self.relics else '1.75'} dmg) | "
            if self.buffs["Vigor"] > 0:
                dmg_affected_by += f"{self.buffs['Vigor']} <buff>Vigor</buff>(+{self.buffs['Vigor']} dmg) | "
            if self.buffs["Strength"] != 0:
                dmg_affected_by += f"{'<buff>' if self.buffs['Strength'] < 0 else '<debuff>'}{self.buffs['Strength']}{'</buff>' if self.buffs['Strength'] < 0 else '</debuff>'} <buff>Strength</buff> | "
                if "Heavy Blade" in card.get('Name'):
                    dmg_affected_by += f"Heavy Blade(x{card.get('Strength Multi')} Strength gain) | "
            if self.buffs["Pen Nib"] > 0:
                dmg *= 2
                dmg_affected_by += "<light-cyan>Pen Nib</light-cyan>(x2 dmg) | "
            if self.buffs['Double Damage'] > 0:
                dmg *= 2
                dmg_affected_by += "<bold>Phantasmal Killer</bold>(x2 dmg) | "
            if target.buffs['Intangible'] > 0:
                dmg = 1
                dmg_affected_by = "<buff>Intangible</buff>(ALL damage reduced to 1)"
        if not ignore_block:
            if dmg <= target.block:
                target.block -= dmg
                dmg = 0
                ansiprint("<blue>Blocked</blue>")
            elif dmg > target.block:
                dmg -= target.block
                dmg = max(0, dmg)
                if self.buffs['Envenom'] > 0:
                    target.debuffs['Poison'] += 1
                    ansiprint(f"<light-cyan>Envenom</light-cyan> applied {self.buffs['Envenom']} <red>Poison</red>.")
                if dmg <= 4 and relics['The Boot'] in self.relics and card.get('Type') == 'Attack':
                    dmg = 5
                    dmg_affected_by += "<bold>The Boot</bold>(dmg increased to 5) | "
                target.health -= dmg
                ansiprint(f"You dealt {dmg} damage(<light-blue>{target.block} Blocked</light-blue>) to {target.name}")
                if target.health <= 0:
                    target.die()
                if 'Reaper' in card['Name']:
                    self.health_actions(dmg, 'Heal')
                target.block = 0

    def debuff(self, debuff_name: str, amount: int, target: object, end=False):
        if debuff_name not in all_effects:
            ansiprint(f"<red>{debuff_name} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if target.buffs['Artifact'] == 0:
            if debuff_name in NON_STACKING_EFFECTS and self != target:
                target.debuffs[debuff_name] = True
                ansiprint(f"{self.name} applied <debuff>{debuff_name}</debuff> to {target.name}.")
            elif debuff_name not in NON_STACKING_EFFECTS and self != target:
                target.debuffs[debuff_name] += amount
                ansiprint(f"{self.name} applied {amount} <debuff>{debuff_name}</debuff> to {target.name}.")
                if debuff_name == 'Vulnerable' and relics['Champion Belt'] in self.relics:
                    self.debuff('Weak', 1, target, False)
            if self == target and debuff_name not in NON_STACKING_EFFECTS:
                ansiprint(f"+{amount} {debuff_name}")
            elif self == target and debuff_name in NON_STACKING_EFFECTS:
                ansiprint(f"<debuff>{debuff_name}</debuff>")
        else:
            ansiprint(f"{debuff_name} was blocked by {'' if self != target else 'your'} <buff>Artifact</buff>")
            target.artifact -= 1
        if end is False:
            sleep(1)
        else:
            sleep(1.5)
            clear()

    def buff(self, buff_name, amount, end=False):
        if buff_name not in all_effects:
            ansiprint(f"<red>{buff_name} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if buff_name not in NON_STACKING_EFFECTS:
            self.buffs[buff_name] += amount
            ansiprint(f"+{amount} <light-cyan>{buff_name}</light-cyan>")
        else:
            self.buffs[buff_name] = True
            ansiprint(f"<light-cyan>{buff_name}</light-cyan>")
        if buff_name == "Strength(Temp)":
            self.debuff("Strength Down", amount, self, True)
        if end is True:
            sleep(1.5)
            clear()
        else:
            sleep(1)

    def gain_gold(self, gold, dialogue=True):
        if relics['Ectoplasm'] not in self.relics:
            self.gold += gold
        if dialogue is True:
            ansiprint(f"You gained <green>{gold}</green> <yellow>Gold</yellow>(<yellow>{self.gold}</yellow> Total)")
        sleep(1)

    def bottle_card(self, card_type):
        while True:
            valid_cards = [card for card in self.deck if card.get("Type") == card_type]
            for possible_card in self.deck:
                if possible_card in valid_cards:
                    ansiprint(f"{counter}: <blue>{possible_card['Name']}</blue> | <light-black>{possible_card['Type']}</light-black> | <light-red>{possible_card['Energy']} Energy</light-red> | <yellow>{possible_card['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
                else:
                    ansiprint(f"{counter}: <light-black>{possible_card['Name']} | {possible_card['Type']} | {possible_card['Energy']} Energy | {possible_card['Info']}</light-black>")
                    counter += 1
                    sleep(0.05)
            option = list_input('What card do you want to bottle? > ', self.deck)
            if self.deck[option] not in valid_cards:
                ansiprint(f"<red>{self.deck[option]['Name']} is not {'an' if card_type == 'Attack' else 'a'} {card_type}</red>")
                sleep(1)
                clear()
                continue
            bottled_card = self.deck[option].copy()
            bottled_card['Bottled'] = True
            self.deck.insert(option, bottled_card)
            del self.deck[option + 1]
            ansiprint(f"<blue>{self.deck[option]['Name']}</blue> is now bottled.")
            sleep(0.8)
            break

    def start_turn(self):
        ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
        # Start of turn effects
        self.draw_cards(False, (self.draw_strength + 3) if self.plays_this_turn <= 3 and relics['Pocketwatch'] in self.relics and combat_turn > 1 else 0)
        self.plays_this_turn = 0
        self.debuff_buff_tick()
        self.start_of_turn_relics()
        if combat_turn > 0:
            if relics['Incense Burner'] in self.relics:
                self.incense_turns += 1
                if self.incense_turns == 6:
                    ansiprint('<bold>Incense Burner</bold> caused: ', end='')
                    self.buff('Intangible', 1, False)
                    self.incense_turns = 0
            if relics['Stone Calender'] in self.relics:
                self.stone_calender += 1
                if self.stone_calender == 7:
                    for enemy in active_enemies:
                        self.attack(52, enemy)
        self.energy = self.energy if relics['Ice Cream'] in self.relics else 0
        self.energy += self.energy_gain + self.buffs["Energized"] + self.buffs["Berzerk"]
        if self.buffs["Energized"] > 0:
            ansiprint(f"You gained {self.buffs['Energized']} extra energy because of <light-cyan>Energized</light-cyan>")
            self.buffs["Energized"] = 0
            ansiprint("<light-cyan>Energized wears off.")
        if self.buffs["Berzerk"] > 0:
            ansiprint(f"You gained {self.buffs['Berzerk']} extra energy because of <light-cyan>Berzerk</light-cyan>")
        if self.buffs['Barricade']:
            if combat_turn > 1:
                ansiprint('You kept your block because of <light-cyan>Barriacade</light-cyan>')
        elif relics['Calipers'] in self.relics and self.block > 15:
            self.block -= 15
            ansiprint(f'You kept {self.block} <light-blue>Block</light-blue> because of <bold>Calipers</bold>')
        else:
            self.block = 0

    def debuff_buff_tick(self):
        # ///////Buffs\\\\\\\\
        for buff in self.buffs:
            if buff == 'Rage' and self.buffs[buff] > 0:
                self.buffs['Rage'] = 0
                ansiprint('<buff>Rage</buff> wears off.')
            if buff == 'Flame Barrier' and self.buffs[buff] > 0:
                self.buffs['Flame Barrier'] = 0
                ansiprint('<buff>Flame Barrier</buff> wears off')
            if buff in DURATION_EFFECTS and self.buffs[buff] > 0:
                self.buffs[buff] -= 1
                ansiprint(f"-1 <buff>{buff}</buff>")
                if self.buffs[buff] == 0:
                    ansiprint(f"<buff>{buff}</buff> wears off")
        # //////Debuffs\\\\\\
        for debuff in self.debuffs:
            if debuff in DURATION_EFFECTS and self.debuffs[debuff] > 0:
                self.debuffs[debuff] -= 1
                ansiprint(f"-1 <debuff>{debuff}</debuff>")
                if self.debuffs[debuff] == 0:
                    ansiprint(f"<debuff>{debuff}</debuff> wears off.")
        # Strength Down: Lose X Strength at the end of your turn
        if self.debuffs['Strength Down'] > 0:
            self.buffs['Strength'] -= self.debuffs['Strength Down']
            ansiprint(f"<red>Strength</red> was reduced by {self.debuffs['Strength Down']} because of <debuff>Strength Down</debuff>")
            sleep(0.7)
            self.debuffs['Strength Down'] = 0
            print("<debuff>Strength Down</debuff> wears off.")
            sleep(0.8)

    def end_of_turn_effects(self):
        if self.buffs["Regeneration"] > 0:
            self.health_actions(self.buffs["Regeneration"], False)
            # Regeneration gets reduced by 1 in the above function
        # Metallicize: At the end of your turn, gain X Block
        if self.buffs["Metallicize"] > 0:
            print("Metallicize: ", end='')
            self.blocking(self.buffs["Metallicize"], False)
            sleep(0.8)
        # Plated Armor: At the end of your turn, gain X Block. Decreases by 1 when recieving unblocked attack damage
        if self.buffs["Plated Armor"] > 0:
            print("Plated Armor: ", end='')
            self.blocking(self.buffs["Plated Armor"], False)
            sleep(0.8)
        if self.buffs["Ritual"] > 0:
            print("Ritual: ", end='')
            self.buff("Strength", self.buffs["Ritual"], True)
        if self.buffs["Combust"] > 0:
            self.take_sourceless_dmg(self.combusts_played)
            for enemy in active_enemies:
                self.attack(self.buffs['Combust'], enemy)
                sleep(0.1)
        if self.buffs["Omega"] > 0:
            for enemy in active_enemies:
                self.attack(self.buffs['Omega'], enemy)
                sleep(0.1)
        if self.buffs["The Bomb"] > 0:
            self.the_bomb_countdown -= 1
            if self.the_bomb_countdown == 0:
                for enemy in active_enemies:
                    self.attack(self.buffs['The Bomb'], enemy)
                    self.buffs["The Bomb"] = 0
                    ansiprint("<light-cyan>The Bomb</light-cyan> wears off")
                    self.the_bomb_countdown = 3

    def start_of_turn_effects(self):
        if self.buffs['Brutality'] > 0:
            ansiprint("From <buff>Brutality</buff>: ")
            self.take_sourceless_dmg(self.buffs['Brutality'])
            self.draw_cards(True, self.buffs['Brutality'])
        if self.buffs["Next Turn Block"] > 0:
            self.blocking(self.buffs["Next Turn Block"], False)
            self.buffs["Next Turn Block"] = 0
            ansiprint('<light-cyan>Next Turn Block</light-cyan> wears off')
        if self.debuffs['Bias'] > 0:
            self.buffs['Focus'] -= self.debuffs['Bias']
            ansiprint(f"<red>Bias</red> reduced <light-cyan>Focus</light-cyan> by {self.debuffs['Bias']}. You now have {self.buffs['Focus']} <light-cyan>Focus</light-cyan>.")
        if relics['Brimstone'] in self.relics:
            ansiprint("From <bold>Brimstone</bold>:")
            for enemy in active_enemies:
                enemy.buffs['Strength'] += 1
                ansiprint(f"{enemy.name} gained 1 <light-cyan>Strength</light-cyan>")
            self.buff('Strength', 2, False)
        if self.buffs['Demon Form'] > 0:
            ansiprint("From <buff>Demon Form</buff>: ", end='')
            self.buff("Strength", self.buffs['Demon Form'])
        if relics['Warped Tongs'] in self.relics:
            ansiprint("From <bold>Warped Tongs</bold>:")
            chosen_card = random.randint(0, len(self.hand) - 1)
            self.card_actions(self.hand[chosen_card], chosen_card, 'Upgrade', self.hand)
        if relics['Horn Cleat'] in self.relics:
            self.blocking(14, False)

    def start_of_turn_relics(self):
        if relics['Anchor'] in self.relics and combat_turn == 1:
            ansiprint('From <bold>Anchor</bold>: ', end='')
            self.blocking(10, False)
        if relics['Horn Cleat'] in self.relics and combat_turn == 2:
            ansiprint("From <bold>Horn Cleat</bold>: ", end='')
            self.blocking(14, False)
        if relics["Captain's Wheel"] in self.relics and combat_turn == 3:
            ansiprint("From <bold>Captain's Wheel</bold>: ", end='')
            self.blocking(18, False)
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
        if relics['Mercury Hourglass'] in self.relics:
            for enemy in active_enemies:
                ansiprint("<bold>Mercury Hourglass</bold> activated.")
                self.attack(3, enemy)

    def end_of_turn_relics(self):
        if relics['Orichaicum'] in self.relics and self.block == 0:
            ansiprint('From <bold>Orichaicum</bold>: ', end='')
            self.blocking(6, False)

    def take_sourceless_dmg(self, dmg):
        if relics['Tungsten Rod'] in self.relics:
            dmg -= 1
        self.health -= dmg
        ansiprint(f"<light-red>You lost {dmg} health.</light-red>")
        if relics['Red Skull'] in self.relics and self.health <= math.floor(self.max_health * 0.5) and not self.red_skull_active:
            self.starting_strength += 3
            ansiprint("<bold>Red Skull</bold> activated. You now start combat with 3 <light-cyan>Strength</light-cyan>.")
            self.red_skull_active = True

    def start_of_combat_relics(self):
        if relics['Thread and Needle'] in self.relics:
            self.buff("Plated Armor", 4, False)
        if relics['Akabeko'] in self.relics:
            self.buff('Vigor', 8, False)
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

    def die(self):
        clear()
        ansiprint("<red>You Died></red>")
        input('Press enter > ')
        sys.exit()

    def end_of_combat_effects(self):
        if relics['Meat on the Bone'] in self.relics and self.health <= math.floor(self.max_health * 0.5):
            ansiprint("<bold>Meat on the Bone</bold> activated.")
            self.health_actions(12, "Heal")
        if relics['Burning Blood'] in self.relics:
            ansiprint("<bold>Burning Blood</bold> activated.")
            self.health_actions(6, 'Heal')
        elif relics['Black Blood'] in player.relics:
            ansiprint("<bold>Black Blood</bold> activated.")
            self.health_actions(12, 'Heal')
        if self.buffs['Self Repair'] > 0:
            ansiprint("<light-cyan>Self Repair</light-cyan>: ", end='')
            self.health_actions(self.buffs['Self Repair'], 'Heal')


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

    def __init__(self, health: list, block: int, name: str):
        self.health = health
        self.max_health = health
        self.block = block
        self.name = name
        if 'louse' in self.name:
            self.damage = [5, 7]
        self.past_moves = ['place'] * 3
        self.intent: str = ''
        self.next_move: str = ''
        self.buffs = {}
        for buff in ENEMY_BUFFS:
            if buff not in NON_STACKING_EFFECTS:
                self.buffs[buff] = 0
            else:
                self.buffs[buff] = False
        self.debuffs = {}
        for debuff in ENEMY_DEBUFFS:
            if debuff not in NON_STACKING_EFFECTS:
                self.debuffs[debuff] = 0
            else:
                self.debuffs[debuff] = False
        self.active_turns = 0
        if 'louse' in self.name:
            self.buffs["Curl Up"] = random.randint(3, 7)

    def execute_move(self) -> tuple[str]:
        commands = self.next_move.split(' / ')
        moves = 1
        for move in commands:
            if moves == 1 and len(move.split('_')) > 2:
                name, func_name, parameters = move.split('_')
            else:
                func_name, parameters = move.split('_')
            if func_name in ('Cowardly', 'Sleeping', 'Stunned') or func_name not in ('Attack', 'Buff', 'Debuff', 'Status', 'Block'):
                self.misc_move()
                sleep(1.5)
                clear()
                return
            if ',' not in parameters:
                chars = list(parameters)
                chars.insert(chars.index(')'), ',')
                parameters = ''.join(chars)
            parameters = eval(parameters)
            ansiprint(f"<bold>{name}</bold>\n" if moves == 1 else '', end='')
            sleep(0.6)
            if func_name == 'Attack':
                dmg = int(parameters[0])
                times = int(parameters[1] if len(parameters) > 1 else 1)
                self.attack(dmg, times)
            elif func_name == 'Buff':
                buff_name = parameters[0]
                amount = int(parameters[1] if len(parameters) > 1 else 1)
                target = eval(parameters[2] if len(parameters) > 2 else 'self')
                self.buff(buff_name, amount, target)
            elif func_name == 'Debuff':
                debuff_name = parameters[0]
                amount = int(parameters[1]) if len(parameters) > 1 else 1
                self.debuff(debuff_name, amount)
            elif func_name == 'Status':
                locations = {'draw pile': player.draw_pile, 'discard pile': player.discard_pile}
                status_name = parameters[0]
                amount = int(parameters[1])
                location = locations[parameters[2].lower()]
                self.status(status_name, amount, location)
            elif func_name == 'Block':
                block = int(parameters[0])
                self.blocking(block)
            sleep(1)
        sleep(0.5)
        clear()
        self.past_moves.append(name)
        moves += 1

    def misc_move(self):
        if len(self.next_move.split('_') > 2):
            name, func_name, parameters = self.next_move.split('_')
        else:
            name, func_name = self.next_move.split('_')
        if len(self.next_move.split('_')) > 2 and ',' not in parameters:
            chars = list(parameters)
            chars.insert(chars.index(')'), ',')
            parameters = ''.join(chars)
        parameters = eval(parameters)
        ansiprint(f"<bold>{name}</bold>")
        sleep(0.6)
        if func_name == 'Cowardly':
            ansiprint("<italic>Hehe. Thanks for the money.<italic>")
        elif func_name == 'Sleeping':
            sleeptalk = parameters[0]
            ansiprint(f'<italic>{sleeptalk}</italic>')
        elif func_name == 'Stunned':
            pass
        elif func_name == 'Summon':
            enemies = tuple(parameters[0])
            amount = int(parameters[1]) if len(parameters) > 1 else 1
            choice = bool(parameters[2]) if len(parameters) > 2 else False
            self.summon(enemies, amount, choice)
        elif func_name == 'Explode':
            pass
        elif func_name == 'Rebirth':
            for debuff in self.debuffs:
                if debuff not in NON_STACKING_EFFECTS:
                    self.debuffs[debuff] = 0
                else:
                    self.debuffs[debuff] = False
            self.buffs['Curiosity'] = False
            self.buffs['Unawakened'] = False
        elif func_name == 'Revive':
            self.health = math.floor(self.health * 0.5)
            ansiprint(f"<bold>{self.name}</bold> revived!")
        elif func_name == 'Charging':
            ansiprint('Charging...')
        elif func_name == 'Split':
            split_into = {"Slime Boss": Enemy(self.health, 0, 'Acid Slime(L)'), "Acid Slime(L)": Enemy(self.health, 0, 'Acid Slime(M)')}
            for _ in range(2):
                active_enemies.append(split_into[self.name])
            ansiprint(f'{self.name} split into 2 {split_into[self.name].name}s')

    def die(self):
        """
        Dies.
        """
        print(f"{self.name} has died.")
        if relics['Gremlin Horn'] in player.relics:
            player.energy += 1
            player.draw_cards(True, 1)
        active_enemies.remove(self)

    def debuff_and_buff_check(self):
        """
        Not finished
        """

    def move_spam_check(self, target_move, max_count):
        '''Returns False if the move occurs [max_count] times in a row. Otherwise returns True'''
        use_count = 0

        for move in self.past_moves:
            if move == target_move:
                use_count += 1
                if use_count == max_count:
                    return False
            else:
                use_count = 0

        return True

    def set_intent(self):
        self.active_turns += 1
        while True:
            if self.name == "Cultist":
                if self.active_turns == 1:
                    self.next_move, self.intent = "Incantation_Buff_('Ritual', 3)", "<buff>Buff</buff>"
                else:
                    self.next_move, self.intent = "Dark Strike_Attack_(6)", "<attack>Attack</attack> Σ6"
            elif self.name in ('Acid Slime (L)', 'Acid Slime (M)'):
                random_num = random.randint(0, 100)
                if self.health < math.floor(self.max_health * 0.5) and self.name == "Acid Slime (L)":
                    self.next_move, self.intent = "Unknown_Split", "<yellow>Unknown</yellow>"
                elif random_num < 30 and self.move_spam_check("Corrosive", 3):
                    self.next_move, self.intent = "Corrosive Spit_Attack_(11) / Status_('Slimed', 2, 'draw pile')", "<attack>Attack</attack> Σ11 / <debuff>Debuff</debuff>"
                elif random_num > 70 and self.move_spam_check("Lick", 3):
                    self.next_move, self.intent = "Lick_Debuff_('Weak', 2)", "<debuff>Debuff</debuff>"
                elif self.move_spam_check("Tackle", 2):
                    self.next_move, self.intent = "Tackle_Attack_(16)", "<attack>Attack</attack> Σ16"
                else:
                    continue
            elif self.name == "Acid Slime (S)":
                random_num = random.randint(0, 100)
                if self.active_turns == 1:
                    self.next_move, self.intent = ("Lick_Debuff_('Weak', 1)", "<debuff>Debuff</debuff>") if random_num > 50 else ("Tackle_Attack_(3)", "<attack>Attack</attack> Σ3")
                elif self.past_moves[-1] == 'Lick':
                    self.next_move, self.intent = "Tackle_Attack_(3)", "<attack>Attack</attack> Σ3"
                elif self.move_spam_check("Lick", 3):
                    self.next_move, self.intent = "Lick_Debuff_('Weak', 1)", "<debuff>Debuff</debuff>"
                else:
                    continue
            elif self.name == "Jaw Worm":
                random_num = random.randint(0, 100)
                if self.active_turns == 1 or (random_num > 75 and self.past_moves[-1] != "Chomp"):
                    self.next_move, self.intent = "Chomp_Attack_(11)", "<attack>Attack</attack> Σ11"
                elif random_num < 45 and self.past_moves[-1] != "Bellow":
                    self.next_move, self.intent = "Bellow_Buff_('Strength', 3) / Block_(6)", "<buff>Buff</buff> / <light-blue>Block</light-blue>"
                elif self.past_moves[-2] != "Thrash":
                    self.next_move, self.intent = "Thrash_Attack_(7) / Block_(5)", f"<attack>Attack</attack> Σ7 / <light-blue>Block</light-blue>"
                else:
                    continue
            elif 'louse' in self.name.lower():
                random_num = random.randint(0, 100)
                if random_num < 75 and self.move_spam_check('Bite', 2):
                    self.next_move, self.intent = "Bite_Attack_(self.damage)", f"<attack>Attack</attack> Σ{self.damage}"
                elif self.move_spam_check('Grow', 2) and self.name == "Red Louse":
                    self.next_move, self.intent = "Grow_Buff_('Strength', 3)", "<buff>Buff</buff>"
                elif self.move_spam_check('Spit Web', 2) and self.name == "Green Louse":
                    self.next_move, self.intent = "Spit Web_Debuff_('Weak', 2)", '<debuff>Debuff</debuff>'
                else:
                    continue
            break

    def show_status(self, full_view=False):
        status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue>)"
        for buff in self.buffs:
            if buff not in NON_STACKING_EFFECTS and self.buffs[buff] > 0:
                status += f" | <buff>{buff}</buff>: {self.buffs[buff]}"
            elif buff in NON_STACKING_EFFECTS and self.buffs[buff] is True:
                status += f" | <buff>{buff}</buff>"
        for debuff in self.debuffs:
            if debuff not in NON_STACKING_EFFECTS and self.debuffs[debuff] > 0:
                status += f" | <red>{debuff}</red>: {self.debuffs[debuff]}"
            elif debuff in NON_STACKING_EFFECTS and self.debuffs[debuff] is True:
                status += f" | <red>{debuff}</red>"
        actual_intent, _ = calculate_actual_damage(self.intent, player, self)
        status += ' | Intent: ' + actual_intent
        ansiprint(status, '' if status == f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue>)" else '\n')
        if full_view is True:
            # int() function used to account for True|False variables.
            for buff in self.buffs:
                # .replace() method is used to replace any variable values with their current values
                if int(self.buffs[buff]) > 0:
                    ansiprint(f"<light-cyan>{buff}</light-cyan>: {all_effects[buff]}".replace("X", self.buffs[buff]))
            for debuff in self.debuffs:
                if int(self.debuffs[debuff]) > 0:
                    ansiprint(f"<red>{debuff}<red>: {all_effects[debuff]}".replace("X", self.debuffs[debuff]))
        print()

    def attack(self, dmg: int, times: int):
        dmg_affected_by = ''
        for _ in range(times):
            if self.buffs['Strength'] != 0:
                dmg += self.buffs['Strength']
                dmg_affected_by += f"<{'red' if self.buffs['Strength'] < 0 else 'light-cyan'}>Strength</{'red' if self.buffs['Strength'] < 0 else 'light-cyan'}>({'-' if self.buffs['Strength'] < 0 else '+'}{self.buffs['Strength']} dmg) | "
            if player.debuffs['Vulnerable']:
                dmg = math.floor(dmg * 1.5)
                dmg_affected_by += "<red>Vulnerable</red>(x1.5 dmg) | "
            if self.debuffs['Weak'] > 0:
                dmg = math.floor(dmg * 0.75 - 0.15 if relics['Paper Krane'] in player.relics else 0)
                dmg_affected_by += "<red>Weak</red>(x0.75 dmg) | "
            if player.buffs['Intangible']  > 0:
                dmg = 1
                dmg_affected_by = "<light-cyan>Intangible</light-cyan>(Reduce ALL damage to 1)"
            if dmg <= player.block:
                player.block -= dmg
                dmg = 0
                ansiprint("<light-blue>Blocked</light-blue>")
            elif dmg > player.block:
                dmg -= player.block
                dmg = max(0, dmg)
                if relics['Torii'] in player.relics and dmg in range(2, 6):
                    dmg = min(dmg, 1)
                    dmg_affected_by += "<bold>Torii</bold>(dmg reduced to 1) | "
                if relics['Tungsten Rod'] in player.relics:
                    dmg -= 1
                    dmg_affected_by += "<bold>Tungsten Rod</bold>(dmg reduced by 1) | "
                if relics['Red Skull'] in player.relics and player.health <= math.floor(player.health * 0.5) and not player.red_skull_active:
                    player.starting_strength += 3
                    player.buffs['Strength'] += 3
                    ansiprint("<bold>Red Skull</bold> gives you 3 <light-cyan>Strength</light-cyan>.")
                if dmg > 0 and relics['Self-Forming Clay'] in player.relics:
                    ansiprint('<bold>Self-Forming Clay</bold> activated.')
                    player.buffs['Next Turn Block'] += 3
                ansiprint(f"{self.name} dealt {dmg}(<light-blue>{player.block} Blocked</light-blue>) damage to you.")
                player.block = 0
                player.health -= dmg
            if player.buffs['Flame Barrier'] > 0:
                if self.block >= dmg:
                    self.block -= dmg
                else:
                    dmg -= self.block
                    self.health -= dmg
                    self.block = 0
                    ansiprint(f"{self.name} took {dmg}(<light-blue>{self.block} Blocked</light-blue>) damage from <buff>Fire Breathing</buff>.")
        if player.health <= math.floor(player.max_health * 0.5) and not player.meat_on_the_bone:
            player.meat_on_the_bone = True
            ansiprint("<bold>Meat on the Bone</bold>> activated.")
        sleep(1)

    def buff(self, buff: str, amount=0, target: 'Enemy'=None):
        if not target:
            target = self
        if buff not in all_effects:
            ansiprint(f"<red>{buff} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if buff not in NON_STACKING_EFFECTS:
            target.buffs[buff] += amount
            ansiprint(f"{self.name} gained {amount} <buff>{buff}</buff>" if target == self else f"{self.name} applied {amount} <buff>{buff}</buff> to {target.name}")
        else:
            target.buffs[buff] = True
            ansiprint(f"{self.name} gained <buff>{buff}</buff>" if target == self else f"{self.name} applied {amount} <buff>{buff}</buff> to {target.name}")
        sleep(1)

    def debuff(self, debuff: str, amount: int):
        if debuff not in all_effects:
            ansiprint(f"<red>{debuff} is not a valid debuff or buff. This is my mistake!</red>")
            sys.exit(1)
        if debuff == 'Weak' and relics['Ginger'] in player.relics:
            ansiprint('<red>Weak</red> was blocked by your <bold>Ginger</bold>')
            sleep(1)
            return
        if debuff == 'Frail' and relics['Turnip'] in player.relics:
            ansiprint('<red>Frail</red> was blocked by your <bold>Turnip</bold>')
            sleep(1)
            return
        if debuff not in NON_STACKING_EFFECTS:
            player.debuffs[debuff] += amount
            ansiprint(f"{self.name} applied {amount} <light-cyan>{debuff}</light-cyan> to you")
        else:
            player.debuffs[debuff] = True
            ansiprint(f"{self.name} applied <light-cyan>{debuff}</light-cyan> to you")
        sleep(1)

    def blocking(self, block: int):
        self.block += block
        ansiprint(f"{self.name} gained {block} <blue>Block</blue>")
        sleep(1)

    def status(self, status_card: str, amount: int, location: list):
        for _ in range(amount):
            status_card = deepcopy(cards[status_card])
            insert_index = random.randint(0, len(location) - 1)
            location.insert(insert_index, status_card)
        print(f"{player.name} gained {amount} {status_card['Name']}({status_card['Info']}) \nPlaced into {location}")
        sleep(1)

    def summon(self, enemy, amount: int, random_enemy: bool):
        if len(enemy) == 1:
            enemy = enemy[0]
        for _ in range(amount):
            chosen_enemy = random.choice(enemy) if random_enemy else enemy
            active_enemies.append(chosen_enemy)
            ansiprint(f"<bold>{chosen_enemy.name}</bold> summoned!")

    def start_turn(self):
        ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
        if self.buffs["Barricade"] is False:
            self.block = 0
        else:
            if self.active_turns > 1 and self.block > 0:
                ansiprint(f"{self.name}'s Block was not removed because of <light-cyan>Barricade</light-cyan")
        if self.buffs['Ritual'] > 0:
            ansiprint("From <buff>Ritual</buff>: ", end='')
            self.buff("Strength", self.buffs['Ritual'], False)
        if self.debuffs["Vulnerable"] > 0:
            self.debuffs["Vulnerable"] -= 1
            ansiprint("<light-cyan>-1 Vulnerable</light-cyan>")
            if self.debuffs["Vulnerable"] == 0:
                print("Vulnerable wears off.")
        if self.debuffs['Weak'] > 0:
            self.debuffs['Weak'] -= 1
            ansiprint("<light-cyan>-1 Weak</light-cyan>")
            if self.debuffs['Weak'] == 0:
                print("Weak wears off")
        print()
        self.set_intent()

    def end_of_turn_effects(self):
        if self.buffs['Ritual'] > 0:
            ansiprint('<light-cyan>Ritual</light-cyan>: ', end='')
            self.buff('Strength', self.buffs['Ritual'])
        if self.buffs['Metallicize'] > 0:
            ansiprint('<light-cyan>Metallicize</light-cyan>: ', end='')
            self.blocking(self.buffs['Metallicize'])
        if self.buffs['Plated Armor'] > 0:
            ansiprint('<light-cyan>Plated Armor</light-cyan>: ', end='')
            self.blocking(self.buffs['Plated Armor'])
        if self.buffs['Regen'] > 0:
            ansiprint('<light-cyan>Regen</light-cyan>: ', end='')
            self.health = min(self.health + self.buffs['regen'], self.max_health)
        if self.buffs['Strength Up'] > 0:
            ansiprint('<light-cyan>Strength Up</light-cyan>: ', end='')
            self.buff('Strength', self.buffs['Strength Up'])


# Characters
player = Player(80, 0, 3, [])
player.deck = [deepcopy(card) for card in [cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Bash']]]
player.relics.append(relics['Burning Blood'])
# Enemies
enemy_encounters = [[Enemy([48, 54], 0, "Cultist")], [Enemy([40, 44], 0, "Jaw Worm")]]
