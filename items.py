from __future__ import annotations

import random
from copy import deepcopy
from typing import TYPE_CHECKING

import effects
from ansi_tags import ansiprint
from definitions import CardType, DeepCopyTuple, PlayerClass, Rarity, State, TargetType
from message_bus_tools import Card, Message, Potion, Relic

if TYPE_CHECKING:
    from enemy import Enemy
    from player import Player
    from items import Card

import displayer as view
import effect_interface as ei


class IroncladStrike(Card):
    def __init__(self):
        super().__init__("Strike", "Deal 6 damage.", Rarity.BASIC, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 6
        self.damage = self.base_damage
        self.damage_affected_by = [f"Strike({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>9</green> damage.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 9, 9
        self.info = 'Deal 9 damage.'

    def apply(self, origin, target):
        origin.attack(target, self)

class IroncladDefend(Card):
    def __init__(self):
        super().__init__("Defend", "Gain 5 <keyword>Block</keyword>.", Rarity.BASIC, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.base_block = 5
        self.block = self.base_block
        self.block_affected_by = [f"Defend({self.block} block)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain <green>8</green> <keyword>Block</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_block, self.block = 8, 8
        self.info = "Gain 8 <keyword>Block</keyword>."

    def apply(self, origin):
        origin.blocking(card=self)

class Bash(Card):
    def __init__(self):
        super().__init__("Bash", "Deal 8 damage. Apply 2 <debuff>Vulnerable</debuff>.", Rarity.BASIC, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=2)
        self.base_damage = 8
        self.damage = self.base_damage
        self.damage_affected_by = [f"Bash({self.damage} dmg)"]
        self.vulnerable = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>10</green> damage. Apply <green>3</green> <debuff>Vulnerable</debuff>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 10, 10
        self.vulnerable = 3
        self.info = "Deal 10 damage. Apply 3 <debuff>Vulnerable</debuff>."

    def apply(self, origin, target):
        origin.attack(target, self)
        ei.apply_effect(target, origin, effects.Vulnerable, self.vulnerable)

class Anger(Card):
    def __init__(self):
        super().__init__("Anger", "Deal 6 damage. Add a copy of this card to your discard pile.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=0)
        self.base_damage = 6
        self.damage = self.base_damage
        self.damage_affected_by = [f"Anger({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>8</green> damage. Add a copy of this card to your discard pile.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 8, 8
        self.info = "Deal 8 damage. Add a copy of this card to your discard pile."

    def apply(self, origin, target):
        origin.attack(target, self)
        origin.discard_pile.append(deepcopy(self))

class Armaments(Card):
    def __init__(self):
        super().__init__("Armaments", "Gain 5 <keyword>Block</keyword>. Upgrade a card in your hand for the rest of combat.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.base_block = 5
        self.block = self.base_block
        self.block_affected_by = [f"Armaments({self.block} block)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain 5 <keyword>Block</keyword>. Upgrade <green>ALL cards</green> in your hand for the rest of combat.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.info = "Gain 5 <keyword>Block</keyword>. Upgrade ALL cards in your hand for the rest of combat."

    def apply(self, origin):
        origin.blocking(card=self)
        if not self.upgraded and len(origin.hand) > 0:
            chosen_card = view.list_input("Choose a card to upgrade", origin.hand, view.view_piles, lambda card: card.is_upgradeable(), "That card is not upgradeable.")
            origin.hand[chosen_card].upgrade()
        else:
            for card in (card for card in origin.hand if card.is_upgradeable()):
                card.upgrade()

class BodySlam(Card):
    def __init__(self):
        super().__init__("Body Slam", "Deal damage equal to your current <keyword>Block</keyword>.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 0 # I am really not sure how to handle this
        self.damage = self.base_damage
        self.damage_affected_by = [f"Body Slam({self.damage} dmg)"]
        self.upgrade_preview += f"<light-red>{self.energy_cost} Energy</light-red> -> <light-red>0 Energy</light-red>"

    def upgrade(self):
        self.upgrade_markers()
        self.energy_cost = 0

    def apply(self, origin, target):
        self.damage = origin.block
        origin.attack(target, self)

class Clash(Card):
    def __init__(self):
        super().__init__("Clash", "Can only be played if every card in your hand is an <keyword>Attack</keyword>. Deal 14 damage.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=0)
        self.base_damage = 14
        self.damage = self.base_damage
        self.damage_affected_by = [f"Clash({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Can only be played if every card in your hand is an <keyword>Attack</keyword>. Deal <green>18</green> damage.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 18, 18
        self.info = "Can only be played if every card in your hand is an <keyword>Attack</keyword>. Deal 18 damage."

    def apply(self, origin, target):
        if not all((card for card in origin.hand if card.type == CardType.ATTACK)):
            print("You have non-Attack cards in your hand.")
            return
        origin.attack(target, self)

class Cleave(Card):
    def __init__(self):
        super().__init__("Cleave", "Deal 8 damage to ALL enemies.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.AREA, energy_cost=1)
        self.base_damage = 8
        self.damage = self.base_damage
        self.damage_affected_by = [f"Cleave({self.damage} dmg)"]
        self.upgrade_preview = f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>11</green> damage to ALL enemies.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 11, 11
        self.info = "Deal 11 damage to ALL enemies."

    def apply(self, origin, enemies):
        for enemy in enemies:
            origin.attack(enemy, self)

class Clothesline(Card):
    def __init__(self):
        super().__init__("Clothesline", "Deal 12 damage. Apply 2 <debuff>Weak</debuff>.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=2)
        self.base_damage = 12
        self.damage = self.base_damage
        self.damage_affected_by = [f"Clothesline({self.damage} dmg)"]
        self.weak = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>14</green> damage. Apply <green>3</green> <debuff>Weak</debuff>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 14, 14
        self.weak = 3
        self.info = "Deal 14 damage. Apply 3 <debuff>Weak</debuff>."

    def apply(self, origin, target):
        origin.attack(target, self)
        ei.apply_effect(target, origin, effects.Weak, self.weak)

class Flex(Card):
    def __init__(self):
        super().__init__("Flex", "Gain 2 <buff>Strength</buff>. At the end of your turn, lose 2 <buff>Strength</buff>.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=0)
        self.strength = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain <green>4</green> <buff>Strength</buff>. At the end of your turn, lose <green>4</green> <buff>Strength</buff>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.strength = 4
        self.info = "Gain 4 <buff>Strength</buff>. At the end of your turn, lose 4 <buff>Strength</buff>."

    def apply(self, origin):
        ei.apply_effect(origin, None, effects.Strength, self.strength)
        ei.apply_effect(origin, None, effects.StrengthDown, self.strength)

class Havoc(Card):
    def __init__(self):
        super().__init__("Havoc", "Play the top card of your draw pile and <keyword>Exhaust</keyword> it.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.ANY, energy_cost=1)
        self.upgrade_preview += f"<light-red>{self.energy_cost} Energy</light-red> -> <light-red><green>0</green> Energy</light-red>"

    def upgrade(self):
        self.upgrade_markers()
        self.energy_cost = 0

    def apply(self, origin, enemies):
        top_card = origin.draw_pile[-1]
        if top_card.target in (TargetType.SINGLE, TargetType.YOURSELF):
            origin.use_card(top_card, True, origin.draw_pile, random.choice(enemies))
        elif top_card.target in (TargetType.AREA, TargetType.ANY):
            origin.use_card(top_card, True, origin.draw_pile, enemies)
        else:
            origin.use_card(top_card, True, origin.draw_pile, random.choice(enemies))

class Headbutt(Card):
    def __init__(self):
        super().__init__("Headbutt", "Deal 9 damage. Put a card from your discard pile on top of your draw pile.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 9
        self.damage = self.base_damage
        self.damage_affected_by = [f"Headbutt({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>12</green> damage. Put a card from your discard pile on top of your draw pile.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 12, 12
        self.info = "Deal 12 damage. Put a card from your discard pile on top of your draw pile."

    def apply(self, origin, target):
        origin.attack(target, self)
        chosen_card = view.list_input("Choose a card to put on top of your draw pile", origin.discard_pile, view.view_piles)
        origin.draw_pile.append(origin.discard_pile.pop(chosen_card))

class HeavyBlade(Card):
    def __init__(self):
        super().__init__("Heavy Blade", "Deal 14 damage. <buff>Strength</buff> affects this card 3 times.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=2)
        self.base_damage = 14
        self.damage = self.base_damage
        self.damage_affected_by = [f"Heavy Blade({self.damage} dmg)"]
        self.strength_multi = 3
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal 14 damage. <buff>Strength</buff> affects this card <green>5</green> times.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.strength_multi = 5
        self.info = "Deal 14 damage. <buff>Strength</buff> affects this card 5 times."

    def apply(self, origin: Player, target):
        player_strength = effects.effect_amount(effects.Strength, origin.buffs)
        self.modify_damage(player_strength * self.strength_multi,
                           f"(+{player_strength * self.strength_multi} dmg from {player_strength} <buff>Strength</buff>)")
        origin.attack(target, self)

    def callback(self, message, data):
        pass # Unnecessary. We can just modify the damage directly in the apply method.

class IronWave(Card):
    def __init__(self):
        super().__init__("Iron Wave", "Deal 5 damage. Gain 5 <keyword>Block</keyword>.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 5
        self.damage = self.base_damage
        self.damage_affected_by = [f"Iron Wave({self.damage} dmg)"]
        self.base_block = 5
        self.block = self.base_block
        self.block_affected_by = [f"Iron Wave({self.block} block)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>7</green> damage. Gain <green>7</green> <keyword>Block</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 7, 7
        self.base_block, self.block = 7, 7
        self.info = "Deal 7 damage. Gain 7 <keyword>Block</keyword>."

    def apply(self, origin, target):
        origin.attack(target, self)
        origin.blocking(card=self)

class PerfectedStrike(Card):
    def __init__(self):
        super().__init__("Perfected Strike", "Deal 6 damage. Deals 2 additional damage for ALL your cards containing <italic>\"Strike\"</italic>.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=2)
        self.base_damage = 6
        self.damage = self.base_damage
        self.damage_affected_by = [f"Perfected Strike({self.damage} dmg)"]
        self.dmg_per_strike = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal 6 damage. Deals <green>3</green> additional damage for ALL your cards containing <italic>\"Strike\"</italic>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.dmg_per_strike = 3
        self.info = "Deal 6 damage. Deals 3 additional damage for ALL your cards containing <italic>\"Strike\"</italic>."

    def apply(self, origin: Player, target):
        player = origin
        strike_cards = sum([1 for card in player.hand if 'strike' in card.name.lower()])
        extra_damage = strike_cards * self.dmg_per_strike
        self.modify_damage(extra_damage, f"Perfected Strike(+{extra_damage} dmg)")
        origin.attack(target, self)

    def callback(self, message, data):
        pass # Unnecessary. We can just modify the damage directly in the apply method.

class PommelStrike(Card):
    def __init__(self):
        super().__init__("Pommel Strike", "Deal 9 damage. Draw 1 card.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 9
        self.damage = self.base_damage
        self.damage_affected_by = [f"Pommel Strike({self.damage} dmg)"]
        self.cards = 1
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>10</green> damage. Draw <green>2</green> cards.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 10, 10
        self.cards = 2
        self.info = "Deal 10 damage. Draw 2 cards."

    def apply(self, origin, target):
        origin.attack(target, self)
        origin.draw_cards(self.cards)

class ShrugItOff(Card):
    def __init__(self):
        super().__init__("Shrug It Off", "Gain 8 <keyword>Block</keyword>. ", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.base_block = 8
        self.block = self.base_block
        self.block_affected_by = [f"Shrug It Off({self.block} block)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain <green>11</green> <keyword>Block</keyword>. Draw 1 card.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_block, self.block = 11, 11
        self.info = "Gain 11 <keyword>Block</keyword>. Draw 1 card."

    def apply(self, origin):
        origin.blocking(card=self)
        origin.draw_cards(1)

class SwordBoomerang(Card):
    def __init__(self):
        super().__init__("Sword Boomerang", "Deal 3 damage to a random enemy 3 times.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.AREA, energy_cost=1)
        self.base_damage = 3
        self.damage = self.base_damage
        self.damage_affected_by = [f"Sword Boomerang({self.damage} dmg)"]
        self.times = 3
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal 3 damage to a random enemy <green>4</green> times.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.times = 4
        self.info = "Deal 3 damage to a random enemy 4 times."

    def apply(self, origin, enemies):
        for enemy in enemies:
            origin.attack(enemy, self)

class Thunderclap(Card):
    def __init__(self):
        super().__init__("Thunderclap", "Deal 4 damage and apply 1 <debuff>Vulnerable</debuff> to ALL enemies.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.AREA, energy_cost=1)
        self.base_damage = 4
        self.damage = self.base_damage
        self.damage_affected_by = [f"Thunderclap({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>7</green> damage and apply 1 <debuff>Vulnerable</debuff> to ALL enemies.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 7, 7
        self.info = "Deal 7 damage and apply 1 <debuff>Vulnerable</debuff> to ALL enemies."

    def apply(self, origin, enemies):
        for enemy in enemies:
            origin.attack(enemy, self)

class TrueGrit(Card):
    def __init__(self):
        super().__init__("True Grit", "Gain 7 <keyword>Block</keyword>. <keyword>Exhaust</keyword> a random card in your hand.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.base_block = 7
        self.block = self.base_block
        self.block_affected_by = [f"True Grit({self.block} block)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain <green>9</green> <keyword>Block</keyword>. <keyword>Exhaust</keyword> a card in your hand.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_block, self.block = 9, 9
        self.info = "Gain 9 <keyword>Block</keyword>. <keyword>Exhaust</keyword> a card in your hand."

    def apply(self, origin):
        origin.blocking(card=self)
        if self.upgraded is True:
            chosen_card = view.list_input("Choose a card to <keyword>Exhaust</keyword>", origin.hand, view.view_piles, lambda card: card.upgradeable is True and card.upgraded is False, "That card is either not upgradeable or is already upgraded.")
            origin.move_card(origin.hand[chosen_card], origin.exhaust_pile, origin.hand, False)
        else:
            random_card = random.choice([card for card in origin.hand if card.upgradeable is True and card.upgraded is False])
            origin.move_card(random_card, origin.exhaust_pile, origin.hand, False)

class TwinStrike(Card):
    def __init__(self):
        super().__init__("Twin Strike", "Deal 5 damage twice.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 5
        self.damage = self.base_damage
        self.damage_affected_by = [f"Twin Strike({self.damage}x2 dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>7</green> damage twice.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 7, 7
        self.info = "Deal 7 damage twice."

    def apply(self, origin, target):
        origin.attack(target, self)

class Warcry(Card):
    def __init__(self):
        super().__init__("Warcry", "Draw 1 card. Put a card from your hand on top of your draw pile. <keyword>Exhaust</keyword>.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=0)
        self.cards = 1
        self.exhaust = True
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Draw <green>2 cards</green>. Put a card from your hand on top of your draw pile. <keyword>Exhaust</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.cards = 2
        self.info = "Draw 2 cards. Put a card from your hand on top of your draw pile. <keyword>Exhaust</keyword>."

    def apply(self, origin):
        origin.draw_cards(self.cards)
        chosen_card = view.list_input("Choose a card to put on top of your draw pile", origin.hand, view.view_piles)
        origin.move_card(origin.hand[chosen_card], origin.draw_pile, origin.hand, False)

class WildStrike(Card):
    def __init__(self):
        super().__init__("Wild Strike", "Deal 12 damage. Shuffle a <status>Wound</status> into your draw pile.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 12
        self.damage = self.base_damage
        self.damage_affected_by = [f"Wild Strike({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>17</green> damage. Shuffle a <status>Wound</status> into your draw pile.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 17, 17
        self.info = "Deal 17 damage. Shuffle a <status>Wound</status> into your draw pile."

    def apply(self, origin, target):
        origin.attack(target, self)
        origin.draw_pile.insert(random.randint(0, len(origin.draw_pile) - 1), Wound())

class BattleTrance(Card):
    def __init__(self):
        super().__init__("Battle Trance", "Draw 3 cards. You can't draw additional cards this turn.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=0)
        self.cards = 3
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Draw <green>4</green> cards. You can't draw additional cards this turn.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.cards = 4
        self.info = "Draw 4 cards. You can't draw additional cards this turn."

    def apply(self, origin):
        origin.draw_cards(cards=self.cards)
        ei.apply_effect(origin, None, effects.NoDraw)

class BloodForBlood(Card):
    registers = [Message.ON_PLAYER_HEALTH_LOSS]
    def __init__(self):
        super().__init__("Blood for Blood", "Costs 1 less <keyword>Energy</keyword> for each time you lose HP in combat. Deal 18 damage.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=4)
        self.base_damage = 18
        self.damage = self.base_damage
        self.damage_affected_by = [f"Blood for Blood({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Costs 1 less <keyword>Energy</keyword> for each time you lose HP in combat. Deal <green>22</green> damage.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 22, 22
        self.info = "Costs 1 less <keyword>Energy</keyword> for each time you lose HP in combat. Deal 22 damage."

    def apply(self, origin, target):
        origin.attack(target, self)

    def callback(self, message, data):
        if message == Message.ON_PLAYER_HEALTH_LOSS:
            _ = data
            self.modify_energy_cost(-1, 'Adjust')

class Bloodletting(Card):
    def __init__(self):
        super().__init__("Bloodletting", "Lose 3 HP. Draw 2 cards.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=0)
        self.cards = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Lose 3 HP. Draw <green>3</green> cards.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.cards = 3
        self.info = "Lose 3 HP. Draw 3 cards."

    def apply(self, origin):
        origin.take_sourceless_dmg(3)
        origin.draw_cards(cards=self.cards)

class BurningPact(Card):
    def __init__(self):
        super().__init__("Burning Pact", "<keyword>Exhaust</keyword> 1 card. Draw 2 cards.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.cards = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow><keyword>Exhaust</keyword> 1 card. Draw <green>3</green> cards.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.cards = 3
        self.info = "<keyword>Exhaust</keyword> 1 card. Draw 3 cards."

    def apply(self, origin):
        chosen_card = view.list_input("Choose a card to <keyword>Exhaust</keyword>", origin.hand, view.view_piles)
        if chosen_card is not None:
            origin.move_card(origin.hand[chosen_card], origin.exhaust_pile, origin.hand, False)
            origin.draw_cards(cards=self.cards)

class Carnage(Card):
    def __init__(self):
        super().__init__("Carnage", "<keyword>Ethereal</keyword>. Deal 20 damage.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=2)
        self.base_damage = 20
        self.damage = self.base_damage
        self.damage_affected_by = [f"Carnage({self.damage} dmg)"]
        self.ethereal = True
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow><keyword>Ethereal</keyword>. Deal <green>28</green> damage.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 28, 28
        self.info = "<keyword>Ethereal</keyword>. Deal 28 damage."

    def apply(self, origin, target):
        origin.attack(target, self)

class Combust(Card):
    def __init__(self):
        super().__init__("Combust", "At the end of your turn, lose 1 HP and deal 5 damage to ALL enemies.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=1)
        self.combust = 5
        self.times_played = 1
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>At the end of your turn, lose 1 HP and deal <green>7</green> damage to ALL enemies.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.damage = 7
        self.info = "At the end of your turn, lose 1 HP and deal 7 damage to ALL enemies."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Combust", self.combust)
        origin.take_sourceless_dmg(self.times_played)

class DarkEmbrace(Card):
    def __init__(self):
        super().__init__(name="Dark Embrace", info="Whenever a card is <keyword>Exhausted</keyword>, draw 1 card.", rarity=Rarity.UNCOMMON, player_class=PlayerClass.IRONCLAD, card_type=CardType.POWER, target=TargetType.YOURSELF, energy_cost=2)
        self.upgrade_preview += f"<light-red>{self.energy_cost} Energy</light-red> -> <light-red><green>1</green> Energy</light-red>"

    def upgrade(self):
        self.upgrade_markers()
        self.energy_cost = 1

    def apply(self, origin):
        ei.apply_effect(origin, None, "DarkEmbrace")

class Disarm(Card):
    def __init__(self):
        super().__init__("Disarm", "Enemy loses 2 <buff>Strength</buff>. <keyword>Exhaust</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.SINGLE, energy_cost=1)
        self.strength_loss = 2
        self.exhaust = True
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Enemy loses <green>3</green> <buff>Strength</buff>. <keyword>Exhaust</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.strength_loss = 3
        self.info = "Enemy loses 3 <buff>Strength</buff>. <keyword>Exhaust</keyword>."

    def apply(self, origin, target):
        ei.apply_effect(target, origin, "Strength", -self.strength_loss)

class Dropkick(Card):
    def __init__(self):
        super().__init__("Dropkick", "Deal 5 damage. If the enemy has <debuff>Vulnerable</debuff>, gain 1 <keyword>Energy</keyword> and draw 1 card.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 5
        self.damage = self.base_damage
        self.damage_affected_by = [f"Dropkick({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>8</green> damage. If the enemy has <debuff>Vulnerable</debuff>, gain 1 <keyword>Energy</keyword> and draw 1 card.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 8, 8
        self.info = "Deal 8 damage. If the enemy has <debuff>Vulnerable</debuff>, gain 1 <keyword>Energy</keyword> and draw 1 card."

    def apply(self, origin: Player, target: Enemy):
        origin.attack(target, self)
        if effects.effect_amount(effects.Vulnerable, target.debuffs) >= 1:
            origin.energy += 1
            origin.draw_cards(cards=1)

    def callback(self, message, data):
        # Unnecessary. We can modify the energy and draw a card directly in the apply method
        # Generally, callbacks are used for effects that are not directly tied to a card's application
        pass


class DualWield(Card):
    def __init__(self):
        super().__init__("Dual Wield", "Create a copy of an <keyword>Attack</keyword> or <keyword>Power</keyword> card in your hand.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.copies = 1
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Create <green>2 copies</green> of an <keyword>Attack</keyword> or <keyword>Power</keyword> card in your hand.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.copies = 2
        self.info = "Create 2 copies of an <keyword>Attack</keyword> or <keyword>Power</keyword> card in your hand."

    def apply(self, origin):
        chosen_card = view.list_input(f"Choose a card to make {'a copy' if self.copies == 1 else '2 copies'} of",
                                      origin.hand,
                                      view.view_piles,
                                      validator=lambda card: card.type in (CardType.ATTACK, CardType.POWER),
                                      message_when_invalid="That card is neither an Attack or a Power.")
        for _ in range(self.copies):
            origin.hand.insert(chosen_card, origin.hand[chosen_card])

class Entrench(Card):
    def __init__(self):
        super().__init__("Entrench", "Double your <keyword>Block</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=2)
        self.upgrade_preview += f"<light-red>{self.energy_cost} Energy</light-red> -> <light-red><green>1</green> Energy</light-red>"

    def upgrade(self):
        self.upgrade_markers()
        self.energy_cost = 1

    def apply(self, origin: Player):
        origin.blocking(block=origin.block, context="Entrench")

class Evolve(Card):
    def __init__(self):
        super().__init__("Evolve", "Whenever you draw a <keyword>Status</keyword> card, draw 1 card.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=1)
        self.evolve = 1
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Whenever you draw a <keyword>Status</keyword> card, draw <green>2 cards</green>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.evolve = 2
        self.info = "Whenever you draw a <keyword>Status</keyword> card, draw 2 cards."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Evolve", self.evolve)

class FeelNoPain(Card):
    def __init__(self):
        super().__init__("Feel No Pain", "Whenever a card is <keyword>Exhausted</keyword>, gain 3 <keyword>Block</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=1)
        self.feel_no_pain = 3
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Whenever a card is <keyword>Exhausted</keyword>, gain <green>4</green> <keyword>Block</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.feel_no_pain = 4
        self.info = "Whenever a card is <keyword>Exhausted</keyword>, gain 4 <keyword>Block</keyword>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "FeelNoPain", self.feel_no_pain)

class FireBreathing(Card):
    def __init__(self):
        super().__init__("Fire Breathing", "Whenever you draw a <status>Status</status> or <curse>Curse</curse> card, deal 6 damage to ALL enemies.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=1)
        self.fire_breathing = 6
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Whenever you draw a <status>Status</status> or <curse>Curse</curse> card, deal <green>10</green> damage to ALL enemies.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.fire_breathing = 10
        self.info = "Whenever you draw a <status>Status</status> or <curse>Curse</curse> card, deal 10 damage to ALL enemies."

    def apply(self, origin):
        ei.apply_effect(origin, None, "FireBreathing", self.fire_breathing)

class FlameBarrier(Card):
    def __init__(self):
        super().__init__("Flame Barrier", "Gain 12 <keyword>Block</keyword>. Whenever you're attacked this turn, deal 4 damage back.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=2)
        self.base_block = 12
        self.block = self.base_block
        self.block_affected_by = [f"Flame Barrier({self.block} block)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain <green>14</green> <keyword>Block</keyword>. Whenever you're attacked this turn, deal 4 damage back.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_block, self.block = 14, 14
        self.info = "Gain 14 <keyword>Block</keyword>. Whenever you're attacked this turn, deal 4 damage back."

    def apply(self, origin: Player):
        origin.blocking(block=self.block, context="Flame Barrier")
        ei.apply_effect(origin, None, "FlameBarrier", 4)

class GhostlyArmor(Card):
    def __init__(self):
        super().__init__("Ghostly Armor", "<keyword>Ethereal</keyword>. Gain 10 <keyword>Block</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.base_block = 10
        self.block = self.base_block
        self.block_affected_by = [f"Ghostly Armor({self.block} block)"]
        self.ethereal = True
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow><keyword>Ethereal</keyword>. Gain <green>13</green> <keyword>Block</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_block, self.block = 13, 13
        self.info = "<keyword>Ethereal</keyword>. Gain 13 <keyword>Block</keyword>"

    def apply(self, origin):
        origin.blocking(card=self)

class Hemokinesis(Card):
    def __init__(self):
        super().__init__("Hemokinesis", "Lose 2 HP. Deal 15 damage.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.base_damage = 15
        self.damage = self.base_damage
        self.damage_affected_by = [f"Hemokinesis({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Lose 2 HP. Deal <green>20</green> damage.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 20, 20
        self.info = "Lose 2 HP. Deal 20 damage."

    def apply(self, origin, target):
        origin.take_sourceless_dmg(2)
        origin.attack(target, self)

class InfernalBlade(Card):
    def __init__(self):
        super().__init__("Infernal Blade", "Add a random <keyword>Attack</keyword> into your hand. It costs 0 this turn. <keyword>Exhaust</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.exhaust = True
        self.upgrade_preview += f"<light-red>{self.info} Energy</light-red> -> <light-red><green>0</green> Energy</light-red>"

    def upgrade(self):
        self.upgrade_markers()
        self.energy_cost = 0

    def apply(self, origin):
        cards = create_all_cards()
        attack_cards = [card for card in cards if card.type == CardType.ATTACK]
        origin.hand.append(random.choice(attack_cards).modify_energy_cost(0, "Set", True))

class Inflame(Card):
    def __init__(self):
        super().__init__("Inflame", "Gain 2 <buff>Strength</buff>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=1)
        self.strength = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain <green>3</green> <buff>Strength</buff>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.strength = 3
        self.info = "Gain 3 <buff>Strength</buff>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Strength", self.strength)

class Intimidate(Card):
    def __init__(self):
        super().__init__("Intimidate", "Apply 1 <debuff>Weak</debuff> to ALL enemies. <keyword>Exhaust</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.AREA, energy_cost=0)
        self.weak = 1
        self.exhaust = True
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Apply <green>2</green> <debuff>Weak</debuff> to ALL enemies. <keyword>Exhaust</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.weak = 2
        self.info = "Apply 2 <debuff>Weak</debuff> to ALL enemies. <keyword>Exhaust</keyword>."

    def apply(self, origin, enemies):
        for enemy in enemies:
            ei.apply_effect(enemy, origin, "Weak", self.weak)

class Metallicize(Card):
    def __init__(self):
        super().__init__("Metallicize", "At the end of your turn, gain 3 <keyword>Block</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=1)
        self.amount = 3
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>At the end of your turn, gain <green>4</green> <keyword>Block</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.amount = 4
        self.info = "At the end of your turn, gain 4 <keyword>Block</keyword>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Metallicize", self.amount)

class PowerThrough(Card):
    def __init__(self):
        super().__init__("Power Through", "Add 2 <status>Wounds</status> into your hand. Gain 15 <keyword>Block</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=1)
        self.base_block = 15
        self.block = self.base_block
        self.block_affected_by = [f"Power Through({self.block} block)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Add 2 <status>Wounds</status> into your hand. Gain <green>20</green> <keyword>Block</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_block, self.block = 20, 20
        self.info = "Add 2 <status>Wounds</status> into your hand. Gain 20 <keyword>Block</keyword>."

    def apply(self, origin):
        for _ in range(2):
            origin.hand.append(Wound())
        origin.blocking(card=self)

class Pummel(Card):
    def __init__(self):
        super().__init__("Pummel", "Deal 2 damage 4 times. <keyword>Exhaust</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=1)
        self.times = 4
        self.base_damage = 2
        self.damage = self.base_damage
        self.damage_affected_by = [f"Pummel({self.damage}x{self.times} dmg)"]
        self.exhaust = True
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal 2 damage <green>5</green> times. <keyword>Exhaust</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.times = 5
        self.info = "Deal 2 damage 5 times. <keyword>Exhaust</keyword>."

    def apply(self, origin, target):
        for _ in range(self.times):
            origin.attack(target, self)

class Rage(Card):
    def __init__(self):
        super().__init__("Rage", "Whenever you play an <keyword>Attack</keyword> this turn, gain 3 <keyword>Block</keyword>.", Rarity.UNCOMMON, PlayerClass.IRONCLAD, CardType.SKILL, TargetType.YOURSELF, energy_cost=0)
        self.rage = 3
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Whenever you play an <keyword>Attack</keyword> this turn, gain <green>5</green> <keyword>Block</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.rage = 5
        self.info = "Whenever you play an <keyword>Attack</keyword> this turn, gain 5 <keyword>Block</keyword>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Rage", self.rage)

class Barricade(Card):
    def __init__(self):
        super().__init__("Barricade", "<keyword>Block</keyword> is not removed at the start of your turn.", Rarity.RARE, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=3)
        self.upgrade_preview += f"<light-red>{self.energy_cost} Energy</light-red> -> <light-red><green>2</green> Energy</light-red>"

    def upgrade(self):
        self.upgrade_markers()
        self.energy_cost = 2

    def apply(self, origin):
        ei.apply_effect(origin, None, "Barricade")

class Berzerk(Card):
    def __init__(self):
        super().__init__("Berzerk", "Gain 2 <debuff>Vulnerable</debuff>. At the start of your turn, gain 1 <keyword>Energy</keyword>.", Rarity.RARE, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=0)
        self.self_vulnerable = 2
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Gain <green>1</green> <debuff>Vulnerable</debuff>. At the start of your turn, gain 1 <keyword>Energy</keyword>.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.self_vulnerable = 1
        self.info = "Gain 1 <debuff>Vulnerable</debuff>. At the start of your turn, gain 1 <keyword>Energy</keyword>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Vulnerable", self.self_vulnerable)
        ei.apply_effect(origin, None, "Berzerk", 1)

class Bludgeon(Card):
    def __init__(self):
        super().__init__("Bludgeon", "Deal 32 damage.", Rarity.RARE, PlayerClass.IRONCLAD, CardType.ATTACK, TargetType.SINGLE, energy_cost=3)
        self.base_damage = 32
        self.damage = self.base_damage
        self.damage_affected_by = [f"Bludgeon({self.damage} dmg)"]
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow>Deal <green>42</green> damage.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.base_damage, self.damage = 42, 42
        self.info = "Deal 42 damage."

    def apply(self, origin, target):
        origin.attack(target, self)

class Brutality(Card):
    def __init__(self):
        super().__init__("Brutality", "At the start of your turn, lose 1 HP and draw 1 card.", Rarity.RARE, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=0)
        self.innate = False
        self.upgrade_preview += f"<yellow>{self.info}</yellow> -> <yellow><green><keyword>Innate</keyword>.</green> At the start of your turn, lose 1 HP and draw 1 card.</yellow>"

    def upgrade(self):
        self.upgrade_markers()
        self.info = "<keyword>Innate</keyword>. At the start of your turn, lose 1 HP and draw 1 card."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Brutality", 1)

class Corruption(Card):
    def __init__(self):
        super().__init__("Corruption", "<keyword>Skills</keyword> cost 0. Whenever you play a <keyword>Skill</keyword>, <keyword>Exhaust</keyword> it.", Rarity.RARE, PlayerClass.IRONCLAD, CardType.POWER, TargetType.YOURSELF, energy_cost=3)
        self.upgrade_preview += f"<light-red>{self.energy_cost} Energy</light-red> -> <light-red><green>2</green> Energy</light-red>"

    def upgrade(self):
        self.upgrade_markers()
        self.energy_cost = 2

    def apply(self, origin):
        ei.apply_effect(origin, None, "Corruption")

class Slimed(Card):
    def __init__(self):
        super().__init__("Slimed", "<keyword>Exhaust</keyword>.", Rarity.COMMON, PlayerClass.IRONCLAD, CardType.STATUS, TargetType.YOURSELF, energy_cost=1)
        self.exhaust = True
        self.upgradeable = False

    def apply(self, *args, **kwargs):
        pass

class Wound(Card):
    def __init__(self):
        super().__init__("Wound", "<keyword>Unplayable</keyword>.", Rarity.COMMON, PlayerClass.ANY, CardType.STATUS, TargetType.NOTHING)
        self.playable = False

class Dazed(Card):
    def __init__(self):
        super().__init__("Dazed", "<keyword>Unplayable</keyword>.", Rarity.COMMON, PlayerClass.ANY, CardType.STATUS, TargetType.NOTHING)
        self.playable = False
#####---END OF CARDS SECTION---#####

class BurningBlood(Relic):
    registers = [Message.END_OF_COMBAT]
    def __init__(self):
        super().__init__("Burning Blood", "At the end of combat, heal 6 HP.", "Your body's own blood burns with an undying rage.", Rarity.STARTER, PlayerClass.IRONCLAD)

    def callback(self, message, data):
        if message == Message.END_OF_COMBAT:
            _, player = data
            player.health_actions(6, "Heal")

class Akabeko(Relic):
    registers = [Message.START_OF_COMBAT]
    def __init__(self):
        super().__init__("Akabeko", "Your first attack in each combat deal 8 additional damage.", "Muuu~", Rarity.COMMON)

    def callback(self, message, data):
        if message == Message.START_OF_COMBAT:
            _, player = data
            ei.apply_effect(player, None, "Vigor", 8)

class Anchor(Relic):
    registers = [Message.START_OF_COMBAT]
    def __init__(self):
        super().__init__("Anchor", "Start each combat with 10 <keyword>Block</keyword>.", "Holding this miniature trinket, you feel heavier and more stable.", Rarity.COMMON)

    def callback(self, message, data):
        if message == Message.START_OF_COMBAT:
            _, _, player = data
            player.blocking(block=10, context="Anchor(10 block)")

class AncientTeaSet(Relic):
    registers = [Message.WHEN_ENTERING_CAMPFIRE]
    def __init__(self):
        super().__init__("Ancient Tea Set", "Whenever you enter a <keyword>Rest Site</keyword>, start the next combat with 2 extra <keyword>Energy</keyword>.", "The key to a refreshing night's rest.", Rarity.COMMON)

    def callback(self, message, data):
        if message == Message.WHEN_ENTERING_CAMPFIRE:
            player = data
            player.ancient_tea_set = True

class ArtOfWar(Relic):
    registers = [Message.ON_CARD_PLAY, Message.START_OF_TURN]
    def __init__(self):
        super().__init__("Art of War", "If you do not play attacks during your turn, gain an extra <keyword>Energy</keyword> next turn.", "The ancient manuscript contains wisdom from a past age.", Rarity.COMMON)
        self.player_attacked_this_turn = False   # Relics can store data like this - no need to put it on the player

    def callback(self, message, data):
        if message == Message.ON_CARD_PLAY:
            player, card, target, enemies = data
            if player == self.host and card.type == CardType.ATTACK:
                self.player_attacked_this_turn = True
        elif message == Message.START_OF_TURN:
            _, player = data
            if not self.player_attacked_this_turn:
                player.energy += 1
                self.player_attacked_this_turn = False   # reset for next turn
                ansiprint(f"You gained 1 <keyword>Energy</keyword> from <keyword>{self.name}</keyword>.")

class BagOfMarbles(Relic):
    registers = [Message.START_OF_COMBAT]
    def __init__(self):
        super().__init__("Bag of Marbles", "At the start of each combat, apply 1 <debuff>Vulnerable</debuff> to ALL enemies.", "A once popular toy in the city. Useful for throwing enemies off balance.", Rarity.COMMON)

    def callback(self, message, data):
        if message == Message.START_OF_COMBAT:
            _, enemies, _ = data
            for enemy in enemies:
                ei.apply_effect(enemy, None, "Vulnerable", 1)

class BlueCandle(Relic):
    registers = [Message.ON_CARD_PLAY]
    def __init__(self):
        super().__init__("Blue Candle", "<curse>Curse</curse> cards can now be played. Playing a <curse>Curse</curse> will make you lose 1 HP and <keyword>Exhaust</keyword> the card.", "The flame ignites when shrouded in darkness.", Rarity.UNCOMMON)

    def callback(self, message, data):
        if message == Message.ON_CARD_PLAY:
            player, card, target, enemies = data
            if card.type == CardType.CURSE:
                player.take_sourceless_dmg(1)

class BottledFlame(Relic):
    registers = [Message.ON_RELIC_ADD]
    def __init__(self):
        super().__init__("Bottled Flame", "Upon pick up, choose an Attack card. At the start of each combat, this card will be in your hand.", "Inside the bottle resides a flame which eternally burns.", Rarity.UNCOMMON)

    def callback(self, message, data):
        if message == Message.ON_RELIC_ADD:
            player, _ = data
            if any(card.type == CardType.ATTACK for card in player.deck):
                chosen_card = view.list_input("Choose an <keyword>Attack</keyword> to bottle", player.deck, view.view_piles, lambda card: card.type == CardType.ATTACK, "That card is not an <keyword>Attack</keyword>.")
                player.deck[chosen_card].bottled = True

class BottledLighting(Relic):
    registers = [Message.ON_RELIC_ADD]
    def __init__(self):
        super().__init__("Bottled Lightning", "Upon pick up, choose a Skill card. At the start of each combat, this card will be in your hand.", "Peering into the swirling maelstrom, you see a part of yourself staring back.", Rarity.UNCOMMON)

    def callback(self, message, data):
        if message == Message.ON_RELIC_ADD:
            player, _ = data
            if any(card.type == CardType.SKILL for card in player.deck):
                chosen_card = view.list_input("Choose a <keyword>Skill</keyword> to bottle", player.deck, view.view_piles, lambda card: card.type == CardType.SKILL, "That card is not a <keyword>Skill</keyword>.")
                player.deck[chosen_card].bottled = True

class BottledTornado(Relic):
    registers = [Message.ON_RELIC_ADD]
    def __init__(self):
        super().__init__("Bottled Tornado", "Upon pick up, choose a Power card. At the start of each combat, this card will be in your hand.", "The bottle gently hums and whirs.", Rarity.UNCOMMON)

    def callback(self, message, data):
        if message == Message.ON_RELIC_ADD:
            player, _ = data
            if any(card.type == CardType.POWER for card in player.deck):
                chosen_card = view.list_input("Choose a <keyword>Power</keyword> to bottle", player.deck, view.view_piles, lambda card: card.type == CardType.POWER, "That card is not a <keyword>Power</keyword>.")
                player.deck[chosen_card].bottled = True

class DarkstonePeriapt(Relic):
    registers = [Message.ON_CARD_ADD]
    def __init__(self):
        super().__init__("Darkstone Periapt", "Whenever you obtain a <curse>Curse</curse>, raise your Max HP by 6.", "The stone draws power from dark energy, converting it into vitality for the wearer.", Rarity.UNCOMMON)

    def callback(self, message, data):
        if message == Message.ON_CARD_ADD:
            player, card = data
            if card.type == CardType.CURSE:
                player.health_actions(6, "Max Health")

class BirdFacedUrn(Relic):
    registers = [Message.ON_CARD_PLAY]
    def __init__(self):
        super().__init__("Bird-Faced Urn", "Whenever you play a <keyword>Power</keyword> card, heal 2 HP.", "The urn shows the crow god Mazaleth looking mischievous.", Rarity.RARE)

    def callback(self, message, data):
        if message == Message.ON_CARD_PLAY:
            player, card, _ = data
            if card.type == CardType.POWER:
                player.health_actions(2, "Heal")

class Calipers(Relic):
    def __init__(self):
        super().__init__("Calipers", "At the start of your turn, lose 15 <keyword>Block</keyword> instead of all your <keyword>Block</keyword>.", '"Mechanical precision leads to greatness." - The Architect', Rarity.RARE)

class CaptainsWheel(Relic):
    registers = [Message.START_OF_TURN]
    def __init__(self):
        super().__init__("Captain's Wheel", "At the start of your 3rd turn, gain 18 <keyword>Block</keyword>.", "Wooden trinket carved with delicate precision. A name is carved into it but the language is foreign.", Rarity.RARE)

    def callback(self, message, data):
        if message == Message.START_OF_TURN:
            turn, player = data
            if turn == 3:
                player.blocking(block=18, context="Captain's Wheel(18 block)")

class DeadBranch(Relic):
    registers = [Message.ON_EXHAUST]
    def __init__(self):
        super().__init__("Dead Branch", "Whenever you <keyword>Exhaust</keyword> a card, add a random card into your hand.", "The branch of a tree from a forgotten era.", Rarity.RARE)

    def callback(self, message, data):
        if message == Message.ON_EXHAUST:
            player, _ = data
            cards = create_all_cards()
            valid_cards = [card for card in cards if card.player_class == player.player_class and card.type not in (CardType.CURSE, CardType.STATUS) and card.rarity != Rarity.SPECIAL]
            player.hand.append(random.choice(valid_cards))

class DuVuDoll(Relic):
    registers = [Message.START_OF_COMBAT]
    def __init__(self):
        super().__init__("Du-Vu Doll", "For each <curse>Curse</curse> in your deck, start each combat with 1 additional <buff>Strength</buff>.", "A doll devised to gain strength from malicious energy.", Rarity.RARE)

    def callback(self, message, data):
        if message == Message.START_OF_COMBAT:
            _, _, player = data
            additional_strength = len([card for card in player.deck if card.type == CardType.CURSE])
            if additional_strength != 0:
                ei.apply_effect(player, None, "Strength", additional_strength)

class WarpedTongs(Relic):
    registers = [Message.START_OF_TURN]
    def __init__(self):
        super().__init__("Warped Tongs", "At the start of your turn, <keyword>Upgrade</keyword> a random card in your hand for the rest of combat.", "The cursed tongs emit a strong desire to return to where they were stolen from.", Rarity.EVENT)

    def callback(self, message, data):
        if message == Message.START_OF_TURN:
            _, player = data
            random_card = random.choice([card for card in player.hand if card.is_upgradeable()])
            random_card.upgrade()
#####---END OF RELICS SECTION---#####

class BloodPotion(Potion):
    def __init__(self):
        super().__init__("Blood Potion", "Heal for 20% of your Max HP.", Rarity.COMMON, TargetType.YOURSELF, PlayerClass.IRONCLAD)
        self.hp_gain = 0.20
        self.golden_stats = [self.hp_gain]
        self.golden_info = "Heal for 40% of your Max HP."

    def apply(self, origin):
        origin.health_actions(round(origin.max_health * self.hp_gain), "Heal")

class AttackPotion(Potion):
    def __init__(self):
        super().__init__("Attack Potion", "Add 1 of 3 random <keyword>Attack</keyword> cards to your hand. It costs 0 this turn.", Rarity.COMMON, TargetType.YOURSELF)
        self.copies = 1
        self.golden_stats = [self.copies]
        self.golden_info = "Add 2 copies of 1 of 3 random <keyword>Attack</keyword> cards to your hand. They cost 0 this turn."

    def apply(self, origin):
        cards = create_all_cards()
        valid_cards = random.choices([card for card in cards if card.type == CardType.ATTACK], k=3)
        chosen_card = view.list_input("Choose a card", valid_cards, view.view_piles)
        if chosen_card is not None:
            for _ in range(self.copies):
                origin.hand.append(deepcopy(valid_cards[chosen_card]))

class SkillPotion(Potion):
    def __init__(self):
        super().__init__("Skill Potion", "Add 1 of 3 random <keyword>Skill</keyword> cards to your hand. It costs 0 this turn.", Rarity.COMMON, TargetType.YOURSELF)
        self.copies = 1
        self.golden_stats = [self.copies]
        self.golden_info = "Add 2 copies of 1 of 3 random <keyword>Skill</keyword> cards to your hand. They cost 0 this turn."

    def apply(self, origin):
        cards = create_all_cards()
        valid_cards = random.choices([card for card in cards if card.type == CardType.SKILL], k=3)
        chosen_card = view.list_input("Choose a card", valid_cards, view.view_piles)
        if chosen_card is not None:
            for _ in range(self.copies):
                origin.hand.append(deepcopy(valid_cards[chosen_card]))

class PowerPotion(Potion):
    def __init__(self):
        super().__init__("Power Potion", "Add 1 of 3 random <keyword>Power</keyword> cards to your hand. It costs 0 this turn.", Rarity.COMMON, TargetType.YOURSELF)
        self.copies = 1
        self.golden_stats = [self.copies]
        self.golden_info = "Add 2 copies of 1 of 3 random <keyword>Power</keyword> cards to your hand. They cost 0 this turn."

    def apply(self, origin):
        cards = create_all_cards()
        valid_cards = random.choices([card for card in cards if card.type == CardType.POWER], k=3)
        chosen_card = view.list_input("Choose a card", valid_cards, view.view_piles)
        if chosen_card is not None:
            for _ in range(self.copies):
                origin.hand.append(deepcopy(valid_cards[chosen_card]))

class ColorlessPotion(Potion):
    def __init__(self):
        super().__init__("Colorless Potion", "Add 1 of 3 random <keyword>Colorless</keyword> cards to your hand. It costs 0 this turn.", Rarity.COMMON, TargetType.YOURSELF)
        self.copies = 1
        self.golden_stats = [self.copies]
        self.golden_info = "Add 2 copies of 1 of 3 random <keyword>Colorless</keyword> cards to your hand. They cost 0 this turn."

    def apply(self, origin):
        cards = create_all_cards()
        colorless_cards = [card for card in cards if card.player_class == PlayerClass.COLORLESS]
        valid_cards = random.choices(colorless_cards, k=min(len(colorless_cards), 3))
        chosen_card = view.list_input("Choose a card", valid_cards, view.view_piles)
        if chosen_card is not None:
            for _ in range(self.copies):
                origin.hand.append(deepcopy(valid_cards[chosen_card]))

class BlessingOfTheForge(Potion):
    def __init__(self):
        super().__init__("Blessing of the Forge", "<keyword>Upgrade</keyword> ALL cards in your hand for the rest of combat.", Rarity.COMMON, TargetType.YOURSELF)

    def apply(self, origin):
        for card in (card for card in origin.hand if card.is_upgradeable()):
            card.upgrade()

class Elixir(Potion):
    def __init__(self):
        super().__init__("Elixir", "<keyword>Exhaust</keyword> any number of cards in your hand.", Rarity.UNCOMMON, TargetType.YOURSELF, PlayerClass.IRONCLAD)

    def apply(self, origin: Player):
        chosen_cards = view.multi_input(input_string="Choose any number of cards to <keyword>Exhaust</keyword>",
                                        choices=origin.hand,
                                        displayer=view.view_piles,
                                        max_choices=len(origin.hand))
        if chosen_cards is not None:
            for i in chosen_cards:
                origin.move_card(origin.hand[i], origin.exhaust_pile, origin.hand)

class GamblersBrew(Potion):
    def __init__(self):
        super().__init__("Gambler's Brew", "Discard any number of cards, then draw that many.", Rarity.UNCOMMON, TargetType.YOURSELF)

    def apply(self, origin: Player):
        chosen_cards = view.multi_input(input_string="Choose any number of cards to discard",
                                        choices=origin.hand,
                                        displayer=view.view_piles,
                                        max_choices=len(origin.hand))
        if chosen_cards is not None:
            for i in chosen_cards:
                origin.move_card(origin.hand[i], origin.discard_pile, origin.hand)
            origin.draw_cards(cards=len(chosen_cards))

class LiquidMemories(Potion):
    def __init__(self):
        super().__init__("Liquid Memories", "Choose a card in your discard pile and return it to your hand. It costs 0 this turn.", Rarity.UNCOMMON, TargetType.YOURSELF)
        self.cards = 1
        self.golden_stats = [self.cards]
        self.golden_info = "Choose 2 cards in your discard pile and return them to your hand. They cost 0 this turn."

    def apply(self, origin: Player):
        chosen_cards = view.multi_input(input_string=f"Choose {'a' if self.cards == 1 else '2'} card{'' if self.cards == 1 else 's'} to return to your hand",
                                        choices=origin.discard_pile,
                                        displayer=view.view_piles,
                                        max_choices=self.cards)
        if chosen_cards is not None:
            for i in chosen_cards:
                origin.discard_pile[i].modify_energy_cost(0, "Set", one_turn=True)
                origin.move_card(chosen_cards[i], origin.hand, origin.discard_pile)

class DistilledChaos(Potion):
    def __init__(self):
        super().__init__("Distilled Chaos", "Play the top 3 cards of your draw pile.", Rarity.UNCOMMON, TargetType.ANY)
        self.cards = 3
        self.golden_stats = [self.cards]
        self.golden_info = "Play the top 6 cards of your draw pile."

    def apply(self, origin, enemies):
        # Literally Havoc but multiple cards
        for i in range(-1, -self.cards, -1):
            card = origin.draw_pile[i]
            if card.target in (TargetType.SINGLE, TargetType.YOURSELF):
                origin.use_card(card, True, origin.draw_pile, random.choice(enemies))
            elif card.target in (TargetType.AREA, TargetType.ANY):
                origin.use_card(card, True, origin.draw_pile, enemies)
            else:
                origin.use_card(card, True, origin.draw_pile, random.choice(enemies))

class DuplicationPotion(Potion):
    def __init__(self):
        super().__init__("Duplication Potion", "This turn, your next card is played twice.", Rarity.UNCOMMON, TargetType.YOURSELF)
        self.duplication = 1
        self.golden_stats = [self.duplication]
        self.golden_info = "This turn, your next 2 cards are played twice."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Duplication", self.duplication)

class AncientPotion(Potion):
    def __init__(self):
        super().__init__("Ancient Potion", "Gain 1 <buff>Artifact</buff>.", Rarity.UNCOMMON, TargetType.YOURSELF)
        self.artifact = 1
        self.golden_stats = [self.artifact]
        self.golden_info = "Gain 2 <buff>Artifact</buff>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Artifact", self.artifact)

class HeartOfIron(Potion):
    def __init__(self):
        super().__init__("Heart of Iron", "Gain 6 <buff>Metallicize</buff>.", Rarity.RARE, TargetType.YOURSELF)
        self.amount = 6
        self.golden_stats = [self.amount]
        self.golden_info = f"Gain {self.amount} <buff>Metallicize</buff>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Metallicize", self.amount)

class FruitJuice(Potion):
    def __init__(self):
        super().__init__("Fruit Juice", "Gain 5 Max HP.", Rarity.RARE, TargetType.YOURSELF)
        self.max_hp_gain = 5
        self.golden_stats = [self.max_hp_gain]
        self.golden_info = "Gain 10 Max HP."

    def apply(self, origin):
        origin.health_actions(self.max_hp_gain, "Max Health")

class FairyInABottle(Potion):
    def __init__(self):
        super().__init__("Fairy in a Bottle", "Unplayable. When you would die, heal 30% HP instead and discard this potion.", Rarity.RARE, TargetType.NOTHING)
        self.hp_percent = 0.3
        self.golden_stats = [self.hp_percent]
        self.golden_info = "Unplayable. When you would die, heal 60% HP instead and discard this potion."

class CultistPotion(Potion):
    def __init__(self):
        super().__init__("Cultist Potion", "Gain 1 <buff>Ritual</buff>.", Rarity.RARE, TargetType.YOURSELF)
        self.ritual = 1
        self.golden_stats = [self.ritual]
        self.golden_info = "Gain 2 <buff>Ritual</buff>."

    def apply(self, origin):
        ei.apply_effect(origin, None, "Ritual", self.ritual)

class EntropicBrew(Potion):
    def __init__(self):
        super().__init__("Entropic Brew", "Fill all your empty potion slots with random potions.", Rarity.RARE, TargetType.YOURSELF)

    def apply(self, origin):
        potions = create_all_potions()
        for _ in range(origin.max_potions - len(origin.potions)):
            origin.potions.append(random.choice(potion for potion in potions if potion.player_class == origin.player_class))

class SmokeBomb(Potion):
    def __init__(self):
        super().__init__("Smoke Bomb", "Escape from a non-boss combat. Recieve no rewards.", Rarity.RARE, TargetType.YOURSELF)

    def apply(self, origin):
        origin.state = State.ESCAPED

class SneckoOil(Potion):
    def __init__(self):
        super().__init__("Snecko Oil", "Draw 5 cards. Randomize the costs of all cards in your hand for the rest of combat.", Rarity.RARE, TargetType.YOURSELF)
        self.cards = 5
        self.golden_stats = [self.cards]
        self.golden_info = "Draw 10 cards. Randomize the costs of all cards in your hand for the rest of combat."

    def apply(self, origin):
        origin.draw_cards(cards=self.cards)
        for card in origin.hand:
            card.modify_energy_cost(random.randint(0, 3), "Set")

def create_all_relics() -> list[Relic]:
    relics = [relic() for relic in (
        # Starter Relics
        BurningBlood,
        # Common Relics
        Akabeko, Anchor, AncientTeaSet, ArtOfWar, BagOfMarbles,
        # Uncommon Relics
        BlueCandle, BottledFlame, BottledLighting, BottledTornado, DarkstonePeriapt,
        # Rare Relics
        BirdFacedUrn, Calipers, CaptainsWheel, DeadBranch, DuVuDoll,
        # Event Relics
        WarpedTongs,
    )]
    return relics

def create_all_cards() -> list[Card]:
    cards = [card() for card in (
        # ----------IRONCLAD CARDS------------
        # Starter(basic) cards
        IroncladStrike, IroncladDefend, Bash,
        # Common Cards
        Anger, Armaments, BodySlam, Clash, Cleave, Clothesline, Flex, Havoc,
        Headbutt, HeavyBlade, IronWave, PerfectedStrike, PommelStrike, ShrugItOff, SwordBoomerang, Thunderclap, TrueGrit, TwinStrike, Warcry, WildStrike,
        # Uncommon Cards
        BattleTrance, BloodForBlood, Bloodletting, BurningPact, Carnage, Combust, DarkEmbrace, Disarm, Dropkick, DualWield, Entrench, Evolve, FeelNoPain,
        FireBreathing, FlameBarrier, GhostlyArmor, Hemokinesis, InfernalBlade, Inflame, Intimidate, Metallicize, PowerThrough, Pummel, Rage,
        # Rare Cards
        Barricade, Berzerk, Bludgeon, Brutality, Corruption
    )]
    return cards

def create_all_potions() -> list[Potion]:
    potions = [potion() for potion in (
        # Common Potions
        BloodPotion, AttackPotion, SkillPotion, PowerPotion, ColorlessPotion, BlessingOfTheForge,
        # Uncommon Potions
        Elixir, GamblersBrew, LiquidMemories, DistilledChaos, DuplicationPotion, AncientPotion,
        # Rare Potions
        HeartOfIron, FruitJuice, FairyInABottle, CultistPotion, EntropicBrew, SmokeBomb, SneckoOil,
    )]
    return potions

sacred_multi: int = 1
def activate_sacred_bark():
    global sacred_multi
    sacred_multi = 2

