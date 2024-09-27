from __future__ import annotations

import random
from copy import deepcopy
from typing import TYPE_CHECKING, Sequence

import effects
from ansi_tags import ansiprint
from definitions import CardType, PlayerClass, Rarity, State, TargetType
from message_bus_tools import Message, Potion, Relic

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
        ei.apply_effect(target=origin, user=None, effect=effects.Ritual, amount=self.ritual)

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

def create_all_potions() -> Sequence[Potion]:
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

