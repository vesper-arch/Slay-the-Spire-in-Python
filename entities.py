import math
import sys
import random
from time import sleep
from os import system
from ansimarkup import ansiprint
from items import relics, cards, golden_multi
from utility import damage, active_enemies, combat_turn, remove_color_tags, duration_effects, player_buffs, player_debuffs, enemy_buffs, enemy_debuffs, non_stacking_effects, all_effects

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
        self.attacks_played_this_turn: bool = False  # Used for the Art of War relic
        self.taken_damage: bool = False  # Used for the Centennial Puzzle relic
        self.gold_on_card_add: bool = False  # Used for the Ceramic Fish relic
        self.happy_flower: int = 0
        self.block_curses: int = 0  # Used for the Omamori relic
        self.nunckaku_attacks: int = 0
        self.starting_strength: int = 0  # Used for the Red Skull and Vajra relic
        self.golden_bark: bool = False  # Used for the Golden Bark relic

    def use_card(self, card: dict, target: object, exhaust, pile) -> None:
        """
        Uses a card
        Wow!
        """
        if card.get('Name') == 'Slimed':
            self.move_card(card, self.exhaust_pile, pile, True)
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

        # Medical Kit allows Status cards to played
        if card.get('Type') == 'Status' and relics['Medical Kit'] in player.relics:
            exhaust = True
        elif card.get('Type') == 'Curse' and relics['Blue Candle'] in player.relics:
            damage(1, self, self)
        if exhaust is True or card.get('Exhaust') is True:
            ansiprint(f"{card['Name']} was <bold>Exhausted</bold>.")
            self.move_card(card, self.exhaust_pile, pile, True)
        else:
            self.move_card(card, self.discard_pile, pile, True)

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

    def blocking(self, block: int, card: bool = True):
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

    def card_actions(self, card: object, action: str, card_pool: list[dict] = None):
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
            # Barricade: Block is not remove at the start of your turn
            if self.buffs["Barricade"] is False:
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
        # Strength Down: Lose X Strength at the end of your turn
        if self.debuffs['Strength Down'] > 0:
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
                    active_enemies.append(Enemy([self.health, self.health], 0, "Acid Slime (M)", [['self.attack(7, 1, True, False)', "self.status(cards['Slimed'], 1, player.discard_pile, False, True)"], [
                                          'self.debuff("Weak", 1, True, True, "Lick")'], ['self.attack(10, 1, True, True, "Tackle")']]))
                    print("Acid Slime (M) spawned!")
                    active_enemies.append(Enemy([self.health, self.health], 0, "Acid Slime (M)", [['self.attack(7, 1, True, False)', "self.status(cards['Slimed'], 1, player.discard_pile, False, True)"], [
                                          'self.debuff("Weak", 1, True, True, "Lick")'], ['self.attack(10, 1, True, True, "Tackle")']]))
                    print("Acid Slime (M) spawned!")
                    sleep(1.5)
                    system("clear")
                    break
                if random_num < 30 and self.move_spam_check("Corrosive", 3):
                    self.attack(11, 1, True, False, "Corrosive Spit")
                    self.status(cards["Slimed"], 2,player.discard_pile, False, True)
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
if relics['Golden Bark'] in player.relics:
    golden_multi += 1
player.deck = [cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'], cards['Strike'],
               cards['Defend'], cards['Defend'], cards['Defend'], cards['Defend'], cards['Bash']]
# Enemies
enemy_encounters = [[Enemy([48, 54], 0, "Cultist", [['self.buff("Ritual", 3, True, True, "Incantation")'], ['self.attack(6, 1, True, True, "Dark Strike")']])],
                    [Enemy([40, 44], 0, "Jaw Worm", [['self.attack(11, 1, True, False, "Chomp")'], ['self.attack(7, 1, True, False, "Thrash")', 'self.blocking(5, False, True)'], ['self.buff("Strength", 3, True, False, "Bellow")', 'self.blocking(6, False, True)']])]]
