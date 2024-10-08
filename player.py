import math
import random
import sys
from copy import deepcopy
from time import sleep
from uuid import uuid4

import effect_catalog
import items
from ansi_tags import ansiprint
from definitions import CardType, State, TargetType
from message_bus_tools import Message, Potion, Registerable, Relic, bus
from card_catalog import Card
from effect_catalog import Effect
from entities import Action
import card_catalog
import potion_catalog
import relic_catalog

import displayer as view
import effect_interface as ei


class Player(Registerable):
    """
    Attributes:::
    health: The player's current health
    block: The amount of damage the player can take before losing health. Removed at the start of their turn
    name: The player's name
    player_class: Ironclad, Silent, Defect, and Watcher
    max_health: The max amount health the player can have
    energy: Resource used to play cards. Replenished at the start of their turn
    energy_gain: The base amount of energy the player gains at the start of their turn
    deck: All the cards the player has. Is shuffled into the player's draw pile at the start of combat.
    potions: Holds the potions the player gets.
    max_potions: The max amount of potions the player can have
    """

    registers = [Message.END_OF_COMBAT, Message.START_OF_COMBAT, Message.START_OF_TURN, Message.END_OF_TURN, Message.ON_RELIC_ADD]

    def __init__(self, health: int, block: int, max_energy: int, deck: list[Card], powers: list = None):
        self.uid = uuid4()
        if not powers:
            powers = []
        self.health: int = health
        self.block: int = block
        self.name: str = "Ironclad"
        self.player_class: str = "Ironclad"
        self.in_combat = False
        self.state = State.ALIVE
        self.floors = 1
        self.fresh_effects: list[str] = []  # Shows what effects were applied after the player's turn
        self.max_health: int = health
        self.energy: int = 0
        self.max_energy: int = max_energy
        self.energy_gain: int = max_energy
        self.deck: list[Card] = deck
        self.potions: list[Potion] = []
        self.relics: list[Relic] = []
        self.max_potions: int = 3
        self.hand: list[Card] = []
        self.draw_pile: list[Card] = []
        self.discard_pile: list[Card] = []
        self.card_reward_choices: int = 3
        self.draw_strength: int = 5
        self.exhaust_pile: list[dict] = []
        self.potion_dropchance = 0.4
        self.orbs = []
        self.orb_slots: int = 3
        self.gold: int = 100
        self.debuffs: list[Effect] = []
        self.buffs: list[Effect] = powers
        # Alternate debuff/buff effects
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
        self.draw_shuffles = 0  # Used for the Sundial relic
        self.incense_turns = 0  # Used for the Incense Burner relic
        self.girya_charges = 3  # Stores how many times the player can gain Energy from Girya
        self.plays_this_turn = 0  # Counts how many cards the played plays each turn
        self.stone_calender = 0
        self.choker_cards_played = 0  # Used for the Velvet Choker relic

    @classmethod
    def create_player(cls):
        player = cls(health=80, block=0, max_energy=3, deck=[
            card_catalog.IroncladStrike(), card_catalog.IroncladStrike(), card_catalog.IroncladStrike(), card_catalog.IroncladStrike(), card_catalog.IroncladStrike(),
            card_catalog.IroncladDefend(), card_catalog.IroncladDefend(), card_catalog.IroncladDefend(), card_catalog.IroncladDefend(),
            card_catalog.Bash()
        ])
        player.relics.append(relic_catalog.BurningBlood())
        return player

    def __str__(self):
        return f"(<italic>Player</italic>)Ironclad(<red>{self.health} / {self.max_health}</red> | <yellow>{self.gold} Gold</yellow> | Deck: {len(self.deck)})"

    def __repr__(self):
        if self.in_combat is True:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy} Energy</light-red>)"
            for effect in self.buffs + self.debuffs:
                status += " | " + effect.get_name()
        else:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <yellow>{self.gold} Gold</yellow>)"
        return (
            status + ""
            if status == f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)"
            else status + "\n"
        )

    def register(self, bus):
        # Register all relics, effects, and cards
        for relic in self.relics:
            relic.register(bus)
        for effect in self.buffs + self.debuffs:
            effect.register(bus)
        for card in self.hand:
            card.register(bus)
        return super().register(bus)

    def use_card(self, card, exhaust, pile, enemies, target: "Enemy"=None) -> None:
        """
        Uses a card
        Wow!
        """
        # determine exhaust
        if card.type in (CardType.STATUS, CardType.CURSE) and card.name not in ("Slimed", "Pride"):
            if card.type == CardType.CURSE and relic_catalog.BlueCandle in self.relics:
                exhaust = True
            else:
                return

        # If the card is in a pile, remove it from the pile (prevents recursion)
        if pile is not None and card in pile:
            pile.remove(card)

        # apply the card
        if card.target == TargetType.SINGLE:
            card.apply(origin=self, target=target)
        elif card.target in (TargetType.AREA, TargetType.ANY):
            card.apply(origin=self, enemies=enemies)
        elif card.target == TargetType.YOURSELF:
            card.apply(origin=self)
        else:
            raise ValueError(f"Invalid target type: {card.target}")

        bus.publish(Message.ON_CARD_PLAY, (self, card, target, enemies))

        # Move the card to the appropriate pile
        if pile is not None:
            if exhaust is True or getattr(card, "exhaust", False) is True:
                ansiprint(f"{card.name} was <bold>Exhausted</bold>.")
                self.move_card(card=card, move_to=self.exhaust_pile, from_location=None, cost_energy=True)
            else:
                self.move_card(card=card, move_to=self.discard_pile, from_location=None, cost_energy=True)
        sleep(0.5)
        view.clear()

    def draw_cards(self, cards: int = None):
        """Draws [cards] cards."""
        if cards is None:
            cards = self.draw_strength
        action = Action(self, self._draw_cards, cards)
        bus.publish(Message.BEFORE_DRAW, (self, action))
        action.execute()
        bus.publish(Message.AFTER_DRAW, (self, action))

    def _draw_cards(self, num_cards: int):
        # Internal function to draw cards
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        if len(self.draw_pile) < num_cards:
            self.draw_pile.extend(random.sample(self.discard_pile, len(self.discard_pile)))
            self.discard_pile = []
            ansiprint("<bold>Discard pile shuffled into draw pile.</bold>")
        self.hand.extend(self.draw_pile[-num_cards:])
        # Removes those cards
        self.draw_pile = self.draw_pile[:-num_cards]
        for card in self.hand:
            card.register(bus=bus)
        print(f"Drew {num_cards} card{'s'[:num_cards^1]}.")  # Cool pluralize hack

    def blocking(self, card: Card = None, block=0, context: str=None):
        """Gains [block] Block. Cards are affected by Dexterity and Frail."""
        block = getattr(card, 'block', None) if card else block
        block_affected_by = ', '.join(getattr(card, 'block_affected_by', []) if card else [context])
        bus.publish(Message.BEFORE_BLOCK, (self, card))
        self.block += block
        ansiprint(f"""{self.name} gained {block} <blue>Block</blue> from {block_affected_by}.""") # f-strings my beloved
        bus.publish(Message.AFTER_BLOCK, (self, card))

    def health_actions(self, heal: int, heal_type: str):
        """If [heal_type] is 'Heal', you heal for [heal] HP. If [heal_type] is 'Max Health', increase your max health by [heal]."""
        heal_type = heal_type.lower()
        if heal_type == "heal":
            self.health += heal
            self.health = min(self.health, self.max_health)
            ansiprint(f"You heal <green>{min(self.max_health - self.health, heal)}</green> <light-blue>HP</light-blue>")
            if (self.health >= math.floor(self.health * 0.5) and any(["Red Skull" in relic.name for relic in self.relics])):
                ansiprint("<red><bold>Red Skull</bold> deactivates</red>.")
                self.starting_strength -= 3
        elif heal_type == "max health":
            self.max_health += heal
            self.health += heal
            ansiprint(f"Your Max HP is {'increased' if heal > 0 else 'decreased'} by <{'light-blue' if heal > 0 else 'red'}>{heal}</{'light-blue' if heal > 0 else 'red'}>")

    def card_actions(self, subject_card: dict, action: str, card_pool: list[dict] = None):
        """[action] == 'Remove', remove [card] from your deck.
        [action] == 'Transform', transform a card into another random card.
        """
        if card_pool is None:
            card_pool = card_catalog.create_all_cards()
        while True:
            if action == "Remove":
                del subject_card
            elif action == "Transform":
                # Curse cards can only be transformed into other Curses
                ansiprint(f"{subject_card.name} was <bold>transformed</bold> into ", end="")
                if subject_card.get("Type") == "Curse":
                    options = [valid_card for valid_card in card_catalog.create_all_cards() if valid_card.get("Type") == "Curse" and valid_card.get("Rarity") != "Special"]
                else:
                    options = [
                        valid_card
                        for valid_card in card_catalog.create_all_cards()
                        if valid_card.get("Class") == valid_card.get("Class")
                        and valid_card.get("Type") not in ("Status", "Curse", "Special")
                        and valid_card.get("Upgraded") is not True
                        and valid_card.get("Rarity") != "Basic"
                    ]
                while True:
                    new_card = random.choice(options)
                    if new_card == subject_card:
                        continue
                    ansiprint(f"{new_card.name} | <yellow>{new_card.info}</yellow>")
                    return new_card

    def move_card(self, card, move_to, from_location, cost_energy=False, shuffle=False):
        if cost_energy is True:
            self.energy -= max(card.energy_cost, 0)
        if from_location is None:
            pass    # Ignore when card is "floating" between piles
        elif card in from_location:
            from_location.remove(card)
        else:
            ansiprint(f"WARNING: {card.name} was not found in `from_location` in `move_card()` function.")
        if shuffle is True:
            move_to.insert(random.randint(0, len(move_to) - 1), card)
        else:
            move_to.append(card)
        if move_to == self.exhaust_pile:
            bus.publish(Message.ON_EXHAUST, (card))

    def attack(self, target: "Enemy", card: Card=None, dmg=-1):
        # Check if already dead and skip if so
        dmg = getattr(card, 'damage', dmg)
        if target.health <= 0:
            return
        if card is not None and card.type not in (CardType.STATUS, CardType.CURSE):
            bus.publish(Message.BEFORE_ATTACK, (self, target, card))
            dmg = getattr(card, 'damage', dmg)
            if dmg <= target.block:
                target.block -= dmg
                dmg = 0
                ansiprint("<blue>Blocked</blue>")
            elif dmg > target.block:
                dmg -= target.block
                dmg = max(0, dmg)
                target.health -= dmg
                ansiprint(f"You dealt {dmg} damage(<light-blue>{target.block} Blocked</light-blue>) to {target.name} with {' | '.join(card.damage_affected_by)}")
                target.block = 0
                bus.publish(Message.AFTER_ATTACK, (self, target, dmg))
                if target.health <= 0:
                    target.die()
                bus.publish(Message.ON_ATTACKED, (target))

    def gain_gold(self, gold, dialogue=True):
        self.gold += gold
        if dialogue is True:
            ansiprint(f"You gained <green>{gold}</green> <yellow>Gold</yellow>(<yellow>{self.gold}</yellow> Total)")
        sleep(1)

    def take_sourceless_dmg(self, dmg):
        self.health -= dmg
        ansiprint(f"<light-red>You lost {dmg} health.</light-red>")

    def die(self):
        view.clear()
        self.health = max(self.health, 0)
        if potion_catalog.FairyInABottle() in self.potions:
            try:
                potion_index = self.potions.index(potion_catalog.FairyInABottle())
            except ValueError:
                potion_index = -1
            self.player.health_actions(math.floor(self.player.max_health * self.potions[potion_index].hp_percent), "Heal")
            return
        bus.publish(Message.ON_DEATH_OR_ESCAPE, self)
        ansiprint("<red>You Died</red>")
        self.state = State.DEAD
        input("Press enter > ")

    def callback(self, message, data: tuple):
        if message == Message.START_OF_COMBAT:
            self.in_combat = True
            self.draw_pile = random.sample(self.deck, len(self.deck))
        elif message == Message.END_OF_COMBAT:
            self.in_combat = False
            self.draw_pile.clear()
            self.discard_pile.clear()
            self.hand.clear()
            self.exhaust_pile.clear()
        elif message == Message.START_OF_TURN:
            # turn = data
            for effect in self.buffs + self.debuffs:
                if effect.subscribed is False:
                    effect.register(bus)
            ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
            self.energy = min(self.energy + self.energy_gain, self.max_energy)
            # INFO: Both Barricade and Calipers are not accounted for here and will be added later.
            self.block = 0
            self.draw_cards()
            self.plays_this_turn = 0
            ei.tick_effects(self)
            self.fresh_effects.clear()
        elif message == Message.END_OF_TURN:
            self.discard_pile += self.hand
            for card in self.hand:
                card.unsubscribe()
            sleep(1)
            view.clear()
        elif message == Message.ON_RELIC_ADD:
            relic, _ = data
            relic.register(bus)

