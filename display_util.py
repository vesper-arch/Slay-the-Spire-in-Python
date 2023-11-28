from time import sleep
from os import system
import math
import random
import re
from ansi_tags import ansiprint


active_enemies = []
combat_turn = 1
combat_potion_dropchance = 40

class CombatViewer():
    '''Displays important info to the player during combat'''
    def __init__(self):
        pass

    def view_piles(self, pile: list[dict], entity, end=False, condition='True'):
        """Prints a numbered list of all the cards in a certain pile."""
        current_relics = [relic.get('Name') for relic in entity.relics]
        if len(pile) == 0:
            ansiprint('<red>This pile is empty</red>.')
            sleep(1.5)
            clear()
            return
        if pile == entity.draw_pile and 'Frozen Eye' not in current_relics:
            ansiprint('<italic>Cards are not shown in order.</italic>')
            pile = random.sample(pile, len(pile))
        counter = 1
        for card in pile:
            upgrades = card.get('Upgrade Count', '')
            upgrade_check = card.get('Upgraded') or card.get('Upgrade Count', 0) > 0
            changed_energy = 'light-red' if not card.get('Changed Energy') else 'green'
            if eval(condition):
                ansiprint(f"{counter}: <{card['Type'].lower()}>{card['Name']}</{card['Type'].lower()}>{f'<green>+{upgrades}</green>' if upgrade_check else ''} | <{changed_energy}>{card.get('Energy', 'Unplayable')}{' Energy' if card.get('Energy') else ''}</{changed_energy}> | <yellow>{card['Info']}</yellow>".replace('Σ', '').replace('꫱', ''))
                counter += 1
                sleep(0.05)
            else:
                ansiprint(f"{counter}: <light-black>{card['Name']} | {card['Type']} | {card.get('Energy', 'Unplayable')}{' Energy' if card.get('Energy') else ''} | {card['Info']}</light-black>".replace('Σ', '').replace('꫱', ''))
                counter += 1
                sleep(0.05)
        if end:
            input("Press enter to continue > ")
        sleep(1.0)
        if end:
            sleep(0.5)
            clear()

    def view_relics(self, entity):
        counter = 1
        for relic in entity.relics:
            name_colors = {'Starter': 'light-black', 'Common': 'white', 'Uncommon': 'uncommon', 'Rare': 'rare'}
            ansiprint(f"{counter}: <{name_colors[relic['Rarity']]}>{relic['Name']}</{name_colors[relic['Rarity']]}> | {relic['Class']} | <yellow>{relic['Info']}</yellow> | <dark-blue><italic>{relic['Flavor']}</italic></dark-blue>")
            counter += 1
            sleep(0.05)
        input("Press enter to continue > ")
        sleep(1.5)
        clear()

    def view_potions(self, entity, numbered_list=True):
        class_colors = {'Ironclad': 'red', 'Silent': 'dark-green', 'Defect': 'true-blue', 'Watcher': 'watcher-purple'}
        rarity_colors = {'Common': 'white', 'Uncommon': 'uncommon', 'Rare': 'rare'}
        counter = 1
        for potion in entity.potions:
            chosen_class_color = class_colors[potion['Class']]
            chosen_rarity_color = rarity_colors[potion['Rarity']]
            ansiprint(f"{f'{counter}: ' if numbered_list else ''}<{chosen_rarity_color}>{potion['Name']}<{chosen_rarity_color}> | <{chosen_class_color}>{potion['Class']}<{chosen_class_color}> | <yellow>{potion['Info']}</yellow>")
            counter += 1
        for _ in range(entity.max_potions - len(entity.potions)):
            ansiprint(f"<light-black>{f'{counter}: ' if numbered_list else ''}(Empty)</light-black>")
            counter += 1

    def display_ui(self, entity, combat=True):
        # Repeats for every card in the entity's hand
        ansiprint("<bold>Hand: </bold>")
        self.view_piles(entity.hand, entity, False, "card.get('Energy', float('inf')) <= entity.energy")
        if combat is True:
            for enemy in active_enemies:
                ansiprint(repr(enemy))
            ansiprint(repr(entity))
        else:
            ansiprint(str(entity))
        print()
view = CombatViewer()


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

def display_actual_damage(string: str, target, entity, card=None) -> tuple[str, str]:
    if not card:
        card = {}
    match = re.search(r"Σ(\d+)", string)
    affected_by = ''
    if match:
        original_damage: str = match.group()
        damage_value = int(original_damage.replace('Σ', ''))
        if "Body Slam" in card.get('Name', ''):
            damage_value += entity.block
        if "Perfected Strike" in card.get('Name', ''):
            perfected_strike_dmg = len([card for card in entity.deck if 'strike' in card.get('Name')]) * card.get('Damage Per "Strike"')
            damage_value += perfected_strike_dmg
            affected_by += f"Perfected Strike(+{perfected_strike_dmg} dmg)"
        if entity.buffs['Strength'] != 0:
            damage_value += entity.buffs['Strength'] * card.get("Strength Multi", 1)
            affected_by += f"<{'<light-cyan>' if entity.buffs['Strength'] > 0 else '<red>'}Strength{'</light-cyan>' if entity.buffs['Strength'] > 0 else '</red>'}>({'+' if entity.buffs['Strength'] > 0 else '-'}{abs(entity.buffs['Strength']) * card.get('Strength Multi', 1)} dmg) | "
            if card.get("Strength Multi", 1) > 1:
                affected_by += f"Heavy Blade(x{card.get('Strength Multi')} Strength gain)"
        if entity.buffs.get('Vigor', 0) > 0:
            damage_value += entity.buffs.get('Vigor')
            affected_by += f"<light-cyan>Vigor</light-cyan>(+{entity.buffs.get('Vigor')} dmg) | "
        if target.debuffs['Vulnerable'] > 0:
            damage_value = math.floor(damage_value * 1.5)
            affected_by += f'{"Target" if hasattr(target, "player_class") else "Your"} <debuff>Vulnerable</debuff>(x1.50 dmg) | '
        if entity.debuffs['Weak'] > 0:
            damage_value = math.floor(damage_value * 0.75)
            affected_by += "<red>Weak</red>(x0.75 dmg)"
        string = string.replace(original_damage, str(damage_value))
    return string, affected_by

def display_actual_block(string: str, entity) -> tuple[str, str]:
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

def clear():
    system('clear')
