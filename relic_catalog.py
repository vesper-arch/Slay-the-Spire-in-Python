from __future__ import annotations

import random
from copy import deepcopy
from typing import TYPE_CHECKING, Sequence

import effect_catalog
from ansi_tags import ansiprint
from definitions import CardType, PlayerClass, Rarity, State, TargetType
from message_bus_tools import Message, Potion, Relic
from card_catalog import create_all_cards

if TYPE_CHECKING:
    from enemy import Enemy
    from player import Player

import displayer as view
import effect_interface as ei


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


def create_all_relics() -> Sequence[Relic]:
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
