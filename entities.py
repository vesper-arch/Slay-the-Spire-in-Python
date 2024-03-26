import math
import random
import sys
from ast import literal_eval
from copy import deepcopy
from time import sleep
from uuid import uuid4

import items
from ansi_tags import ansiprint
from definitions import CardType, CombatTier, EnemyState, PlayerClass, Rarity, TargetType
from helper import active_enemies, ei, gen, view
from message_bus_tools import Card, Message, Registerable, bus


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

    registers = [
        Message.END_OF_COMBAT,
        Message.START_OF_COMBAT,
        Message.START_OF_TURN,
        Message.END_OF_TURN,
    ]

    def __init__(
        self,
        health: int,
        block: int,
        max_energy: int,
        deck: list[Card],
        powers: dict = None,
    ):
        self.uid = uuid4()
        if not powers:
            powers = {}
        self.health: int = health
        self.block: int = block
        self.name: str = "Ironclad"
        self.player_class: str = "Ironclad"
        self.in_combat = False
        self.floors = 1
        self.fresh_effects: list[str] = []  # Shows what effects were applied after the player's turn
        self.max_health: int = health
        self.energy: int = 0
        self.max_energy: int = max_energy
        self.energy_gain: int = max_energy
        self.deck: list[Card] = deck
        self.potions: list[dict] = []
        self.relics: list[dict] = []
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
        self.debuffs: dict[str:int] = ei.init_effects("Player Debuffs") | powers
        self.buffs: dict[str:int] = ei.init_effects("Player Buffs") | powers
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
        self.draw_shuffles = 0  # Used for the Sundial relic
        self.incense_turns = 0  # Used for the Incense Burner relic
        self.girya_charges = 3  # Stores how many times the player can gain Energy from Girya
        self.plays_this_turn = 0  # Counts how many cards the played plays each turn
        self.stone_calender = 0
        self.choker_cards_played = 0  # Used for the Velvet Choker relic

    def __str__(self):
        return f"(<italic>Player</italic>)Ironclad(<red>{self.health} / {self.max_health}</red> | <yellow>{self.gold} Gold</yellow> | Deck: {len(self.deck)})"

    def __repr__(self):
        if self.in_combat is True:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy} Energy</light-red>)"
            for buff in self.buffs:
                if int(self.buffs[buff]) >= 1:
                    status += f" | <buff>{buff}</buff>{f' {self.buffs[buff]}' if isinstance(self.buffs[buff], int) else ''}"
            for debuff in self.debuffs:
                if int(self.debuffs[debuff]) >= 1:
                    status += f" | <debuff>{debuff}</debuff>{f' {self.debuffs[debuff]}' if isinstance(self.debuffs[debuff], int) else ''}"
        else:
            status = f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <yellow>{self.gold} Gold</yellow>)"
        return (
            status + ""
            if status == f"\n{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue> | <light-red>{self.energy} / {self.max_energy}</light-red>)"
            else status + "\n"
        )

    def show_effects(self):
        for buff in self.buffs:
            if int(self.buffs[buff]) > 0:
                ansiprint(f'<buff>{buff}</buff>: {ei.ALL_EFFECTS[buff].replace("X", str(self.buffs[buff]))}')
        for debuff in self.debuffs:
            ansiprint(f'<debuff>{debuff}</debuff>: {ei.ALL_EFFECTS[debuff].replace("X", str(self.debuffs[debuff]))}')

    def use_card(self, card, exhaust, pile, target: "Enemy"=None) -> None:
        """
        Uses a card
        Wow!
        """
        if card.type in (CardType.STATUS, CardType.CURSE) and card.name not in ("Slimed", "Pride"):
            return
        if card.target == TargetType.SINGLE:
            card.apply(origin=self, target=target)
        elif card.target == TargetType.AREA:
            card.apply(origin=self, enemies=active_enemies)
        elif card.target == TargetType.YOURSELF:
            card.apply(origin=self)
        bus.publish(Message.ON_CARD_PLAY, (self, card, target))
        if self.buffs["Corruption"]:
            exhaust = True

        if self.buffs["Double Tap"] > 0 and card.get("Type") == "Attack":
            self.buffs["Double Tap"] -= 1
            sleep(1.5)
            view.clear()
            self.use_card(card=card, target=target, exhaust=True, pile=None)
        if (card.type == CardType.STATUS and items.relics["Medical Kit"] in player.relics):
            exhaust = True
        elif (card.type == CardType.CURSE and items.relics["Blue Candle"] in player.relics):
            self.take_sourceless_dmg(1)
            exhaust = True
        if pile is not None:
            if exhaust is True or getattr(card, "exhaust", False) is True:
                ansiprint(f"{card['Name']} was <bold>Exhausted</bold>.")
                self.move_card(
                    card=card,
                    move_to=self.exhaust_pile,
                    from_location=pile,
                    cost_energy=True,
                )
            else:
                self.move_card(
                    card=card,
                    move_to=self.discard_pile,
                    from_location=pile,
                    cost_energy=True,
                )
        sleep(0.5)
        view.clear()

    def on_relic_pickup(self, relic):
        self.gold_on_card_add = relic["Name"] == "Ceramic Fish"
        self.max_potions += 2 if relic["Name"] == "Potion Belt" else 0
        self.starting_strength += int(relic["Name"] == "Vajra")
        if relic["Name"] in ("Bottled Flame", "Bottled Lightning", "Bottled Tornado"):
            relic_to_type = {
                "Bottled Flame": "Attack",
                "Bottled Lightning": "Skill",
                "Bottled Tornado": "Power",
            }
            self.bottle_card(relic_to_type[relic["Name"]])
        elif "Egg" in relic.get("Name"):
            relic_variables = {
                "Molten Egg": self.upgrade_attacks,
                "Frozen Egg": self.upgrade_skills,
                "Toxic Egg": self.upgrade_powers,
            }
            relic_variables[relic["Name"]] = True

        elif relic["Name"] in ("Whetstone", "War Paint"):
            valid_card_types = {"Whetstone": "Attack", "War Paint": "Skill"}
            valid_cards = [
                card
                for card in self.deck
                if card.get("Type") == valid_card_types[relic["Name"]]
            ]
            ansiprint(f"<bold>{relic['Name']}</bold>:")
            for _ in range(min(len(valid_cards), 2)):
                chosen_card = random.randint(0, len(self.deck) - 1)
                self.deck[chosen_card] = self.card_actions(
                    self.deck[chosen_card], "Upgrade", valid_cards
                )
        elif relic.get("Name") in ("Strawberry", "Pear", "Mango"):
            health_values = {"Strawberry": 7, "Pear": 10, "Mango": 14}
            self.health_actions(health_values[relic["Name"]], "Max Health")
        elif relic["Name"] in (
            "Mark of Pain",
            "Busted Crown",
            "Coffee Dripper",
            "Cursed Key",
            "Ectoplasm",
            "Fusion Hammer",
            "Philosopher's Stone",
            "Runic Dome",
            "Sozu",
            "Velvet Choker",
        ):
            self.max_energy += 1
        elif relic["Name"] == "Astrolabe":
            while True:
                try:
                    view.view_piles(
                        self.deck, validator=lambda card: card.removable is False
                    )
                    target_cards = literal_eval(
                        f"({input('Choose 3 cards to <keyword>Transform</keyword> and <keyword>Upgrade</keyword> separated by colons > ')})"
                    )
                    if len(target_cards) != 3:
                        raise TypeError("")
                    for card in target_cards:
                        self.deck[card] = self.card_actions(
                            self.deck[card], "Transform", items.cards
                        )
                        self.deck[card].upgrade()
                    break
                except (TypeError, ValueError):
                    ansiprint(
                        "<red>Incorrect syntax, wrong length, or invalid card number</red> Correct: '_, _, _'"
                    )
                    sleep(1.5)
                    view.clear()
                    continue
        elif relic["Name"] == "Calling Bell":
            gen.card_rewards(
                CombatTier.NORMAL, False, self, None, [items.cards["Call of the Bell"]]
            )
            for _ in range(3):
                gen.claim_relics(True, self, 3)
        elif relic["Name"] == "Empty Cage":
            view.view_piles(self.deck, self, False, "Removable")
            backup_counter = 2  # Used to account for wrong or invalid inputs
            for _ in range(backup_counter):
                option = view.list_input(
                    "Choose a card to remove > ",
                    self.deck,
                    view.view_piles,
                    lambda card: card.removable is False,
                    "That card is not removable.",
                )
                self.deck[option] = self.card_actions(
                    self.deck[option], "Remove", items.cards
                )
        elif relic["Name"] == "Pandora's Box":
            for card in self.deck:
                if card.name.replace("+", "") in ("Strike", "Defend"):
                    card = self.card_actions(card, "Upgrade", items.cards)
        elif relic["Name"] == "Sacred Bark":
            items.activate_sacred_bark()
        elif relic["Name"] == "Tiny House":
            gen.claim_potions(False, 1, self, items.potions)
            self.gain_gold(50)
            self.health_actions(5, "Max Health")
            gen.card_rewards("Normal", True, self, items.cards)
            upgrade_card = random.choice(
                (
                    index
                    for index in range(len(self.deck))
                    if not self.deck[index].upgraded
                    and (
                        self.deck[index].name == "Burn"
                        or self.deck[index].type
                        not in (CardType.STATUS, CardType.CURSE)
                    )
                )
            )
            self.deck[upgrade_card].upgrade()
        elif relic["Name"] == "Velvet Choker":
            self.max_energy += 1
        elif relic["Name"] == "Black Blood":
            burning_blood_index = self.relics.index(
                items.relics["Burning Blood"]
            )  # Will have to change once other characters are added
            self.deck[burning_blood_index] = relic
        elif relic["Name"] == "Mark of Pain":
            self.max_energy += 1
        _ = self.gain_gold(300) if relic["Name"] == "Old Coin" else None
        self.card_reward_choices += 1 if relic["Name"] == "Question Card" else 0

    def on_card_play(self, card: Card):
        if items.relics["Kunai"] in self.relics and card.type == CardType.ATTACK:
            self.kunai_attacks += 1
            if self.kunai_attacks == 3:
                ansiprint("<bold>Kunai</bold> activated: ", end="")
                ei.apply_effect(self, None, "Dexterity", 1)
                self.kunai_attacks = 0
        if (
            items.relics["Ornamental Fan"] in self.relics
            and card.type == CardType.ATTACK
        ):
            self.ornament_fan_attacks += 1
            if self.ornament_fan_attacks == 3:
                ansiprint("<bold>Ornamental Fan</bold> activated: ", end="")
                self.blocking(4, False)
        if items.relics["Letter Opener"] in self.relics and card.type == CardType.SKILL:
            self.letter_opener_skills += 1
            if self.letter_opener_skills == 3:
                ansiprint("<bold>Letter Opener</bold> activated")
                for enemy in active_enemies:
                    self.attack(5, enemy)
                self.letter_opener_skills = 0
        if (
            items.relics["Mummified Hand"] in self.relics
            and card.type == CardType.POWER
        ):
            ansiprint("<bold>Mummified Hand</bold> activated: ", end="")
            target_card = random.choice(self.hand)
            target_card.modify_energy_cost(0, "Set", True)
        if items.relics["Shuriken"] in self.relics and card.type == CardType.Attack:
            self.shuriken_attacks += 1
            if self.shuriken_attacks == 3:
                ansiprint("<bold>Shuriken</bold> activated: ", end="")
                ei.apply_effect(self, self, "Strength", 1)
        if items.relics["Ink Bottle"] in self.relics:
            self.inked_items.cards += 1
            if self.inked_items.cards == 10:
                ansiprint("<bold>Ink Bottle</bold> activated: ", end="")
                self.draw_cards(True, 1)
                self.inked_items.cards = 0
        if items.relics["Duality"] in self.relics and card.type == CardType.ATTACK:
            ansiprint("<bold>Duality</bold> activated: ", end="")
            ei.apply_effect(self, self, "Dexterity", 1)
        if (
            items.relics["Bird-Faced Urn"] in self.relics
            and card.type == CardType.POWER
        ):
            ansiprint("<bold>Bird-Faced Urn</bold> activated: ", end="")
            self.health_actions(2, "Heal")
        if items.relics["Velvet Choker"] in self.relics:
            self.choker_cards_played += 1

    def draw_cards(self, middle_of_turn: bool, draw_cards: int = 0):
        """Draws [draw_cards] cards."""
        if draw_cards == 0:
            draw_cards = self.draw_strength
        while True:
            if self.debuffs["No Draw"] is True:
                print("You can't draw any more cards")
                break
            if middle_of_turn is False:
                draw_cards += self.buffs["Draw Up"]
                if items.relics["Bag of Preparation"] in self.relics:
                    draw_cards += 2
                if items.relics["Ring of the Snake"] in self.relics:
                    draw_cards += 2
            if len(player.draw_pile) < draw_cards:
                player.draw_pile.extend(
                    random.sample(player.discard_pile, len(player.discard_pile))
                )
                player.discard_pile = []
                if items.relics["Sundial"] in self.relics:
                    self.draw_shuffles += 1
                    if self.draw_shuffles == 3:
                        ansiprint(
                            "<bold>Sundial</bold> gave you 2 <italic><red>Energy</red></italic>"
                        )
                        self.energy += 2
                        self.draw_shuffles = 0
                ansiprint("<bold>Discard pile shuffled into draw pile.</bold>")
            self.hand.extend(player.draw_pile[-draw_cards:])
            # Removes those cards
            player.draw_pile = player.draw_pile[:-draw_cards]
            print(f"Drew {draw_cards} cards.")
            # bus.publish(Message.ON_DRAW, (pl))
            break

    def blocking(self, card: Card = None, block=0):
        """Gains [block] Block. Cards are affected by Dexterity and Frail."""
        block = card.block if card else block
        bus.publish(Message.BEFORE_BLOCK, (self, card))
        self.block += block
        ansiprint(f"""{self.name} gained {block} <blue>Block</blue>{f" from {', '.join(card.block_affected_by).lstrip(', ') if card else ''}"}.""") # f-strings my beloved
        bus.publish(Message.AFTER_BLOCK, (self, card))

    def health_actions(self, heal: int, heal_type: str):
        """If [heal_type] is 'Heal', you heal for [heal] HP. If [heal_type] is 'Max Health', increase your max health by [heal]."""
        if heal_type == "Heal":
            heal = round(
                heal * 1.5
                if self.in_combat and items.relics["Magic Flower"] in self.relics
                else 1
            )
            self.health += heal
            self.health = min(self.health, self.max_health)
            ansiprint(
                f"You heal <green>{min(self.max_health - self.health, heal)}</green> <light-blue>HP</light-blue>"
            )
            if (
                self.health >= math.floor(self.health * 0.5)
                and items.relics["Red Skull"] in self.relics
            ):
                ansiprint("<red><bold>Red Skull</bold> deactivates</red>.")
                self.starting_strength -= 3
        elif heal_type == "Max Health":
            self.max_health += heal
            self.health += heal
            ansiprint(
                f"Your Max HP is {'increased' if heal > 0 else 'decreased'} by <{'light-blue' if heal > 0 else 'red'}>{heal}</{'light-blue' if heal > 0 else 'red'}>"
            )

    def card_actions(
        self, subject_card: dict, action: str, card_pool: list[dict] = None
    ):
        """[action] == 'Remove', remove [card] from your deck.
        [action] == 'Upgrade', Upgrade [card]
        [action] == 'Transform', transform a card into another random card.
        [action] == 'Store', (Only in the Note From Yourself event) stores a card to be collected from the event in another run.
        """
        if card_pool is None:
            card_pool = items.cards
        while True:
            if action == "Remove":
                del subject_card
            elif action == "Transform":
                # Curse cards can only be transformed into other Curses
                ansiprint(
                    f"{subject_card['Name']} was <bold>transformed</bold> into ", end=""
                )
                if subject_card.get("Type") == "Curse":
                    options = [
                        valid_card
                        for valid_card in items.cards.values()
                        if valid_card.get("Type") == "Curse"
                        and valid_card.get("Rarity") != "Special"
                    ]
                else:
                    options = [
                        valid_card
                        for valid_card in items.cards.values()
                        if valid_card.get("Class") == valid_card.get("Class")
                        and valid_card.get("Type") not in ("Status", "Curse", "Special")
                        and valid_card.get("Upgraded") is not True
                        and valid_card.get("Rarity") != "Basic"
                    ]
                while True:
                    new_card = random.choice(options)
                    if new_card == subject_card:
                        continue
                    ansiprint(
                        f"{new_card['Name']} | <yellow>{new_card['Info']}</yellow>"
                    )
                    return new_card

    def move_card(self, card, move_to, from_location, cost_energy, shuffle=False):
        if cost_energy is True:
            self.energy -= max(card.energy_cost, 0)
        from_location.remove(card)
        if shuffle is True:
            move_to.insert(random.randint(0, len(move_to) - 1), card)
        else:
            move_to.append(card)
        if move_to == self.exhaust_pile:
            bus.publish(Message.ON_EXHAUST, (card))

    def curse_status_effects(self):
        if items.cards["Burn"] in self.relics:
            self.take_sourceless_dmg(2)

    def attack(self, target: "Enemy", card: Card=None, dmg=-1, ignore_block=False):
        # Check if already dead and skip if so
        dmg = getattr(card, 'damage', default=None) if card else dmg  # noqa: B009
        if target.health <= 0:
            return
        if card is not None and card.type not in (CardType.STATUS, CardType.CURSE):
            bus.publish(Message.BEFORE_ATTACK, (self, target, card))
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
                bus.publish(Message.AFTER_ATTACK, (self, target, card))
                if target.health <= 0:
                    target.die()

    def gain_gold(self, gold, dialogue=True):
        if items.relics["Ectoplasm"] not in self.relics:
            self.gold += gold
        else:
            ansiprint(
                "You cannot gain <yellow>Gold</yellow> because of <bold>Ectoplasm</bold>."
            )
        if dialogue is True:
            ansiprint(
                f"You gained <green>{gold}</green> <yellow>Gold</yellow>(<yellow>{self.gold}</yellow> Total)"
            )
        sleep(1)

    def bottle_card(self, card_type):
        while True:
            option = view.list_input(
                "What card do you want to bottle? > ",
                self.deck,
                view.view_piles,
                lambda card: card.name == card_type,
                f"That card is not {'an' if card_type == 'Attack' else 'a'} {card_type}.",
            )
            self.deck[option].bottled = True
            ansiprint(f"<blue>{self.deck[option]['Name']}</blue> is now bottled.")
            sleep(0.8)
            break

    def end_of_turn_effects(self):
        if self.debuffs["Strength Down"] > 0:
            self.buffs["Strength"] -= self.debuffs["Strength Down"]
            ansiprint(
                f'<debuff>Strength Down</debuff> reduced <buff>Strength</buff> to {self.buffs["Strength"]}'
            )
            self.debuffs["Strength Down"] = 0
            ansiprint("<debuff>Strength Down</debuff>")
        if self.buffs["Regeneration"] > 0:
            self.health_actions(self.buffs["Regeneration"], False)
        if self.buffs["Metallicize"] > 0:
            print("Metallicize: ", end="")
            self.blocking(self.buffs["Metallicize"], False)
        if self.buffs["Plated Armor"] > 0:
            print("Plated Armor: ", end="")
            self.blocking(self.buffs["Plated Armor"], False)
        if self.buffs["Ritual"] > 0:
            print("Ritual: ", end="")
            ei.apply_effect(self, self, "Strength", self.buffs["Ritual"])
        if self.buffs["Combust"] > 0:
            self.take_sourceless_dmg(self.combusts_played)
            for enemy in active_enemies:
                self.attack(self.buffs["Combust"], enemy)
                sleep(0.1)
        if self.buffs["Omega"] > 0:
            for enemy in active_enemies:
                self.attack(self.buffs["Omega"], enemy)
                sleep(0.5)
        if self.buffs["The Bomb"] > 0:
            self.the_bomb_countdown -= 1
            if self.the_bomb_countdown == 0:
                for enemy in active_enemies:
                    self.attack(self.buffs["The Bomb"], enemy)
                self.buffs["The Bomb"] = 0
                ansiprint("<light-cyan>The Bomb</light-cyan> wears off")
                self.the_bomb_countdown = 3

    def end_of_turn_relics(self):
        if items.relics["Orichaicum"] in self.relics and self.block == 0:
            ansiprint("From <bold>Orichaicum</bold>: ", end="")
            self.blocking(6, False)

    def take_sourceless_dmg(self, dmg):
        if items.relics["Tungsten Rod"] in self.relics:
            dmg -= 1
        self.health -= dmg
        ansiprint(f"<light-red>You lost {dmg} health.</light-red>")
        if (
            items.relics["Red Skull"] in self.relics
            and self.health <= math.floor(self.max_health * 0.5)
            and not self.red_skull_active
        ):
            self.starting_strength += 3
            ansiprint(
                "<bold>Red Skull</bold> activated. You now start combat with 3 <light-cyan>Strength</light-cyan>."
            )
            self.red_skull_active = True
        if items.relics["Runic Cube"] and dmg > 0:
            self.draw_cards(False, 1)

    def start_of_combat_relics(self, turn, combat_type):
        if items.relics["Snecko Eye"] in self.relics:
            ei.apply_effect(self, self, "Confused")
        if items.relics["Slaver's Collar"] in self.relics and combat_type in (
            CombatTier.BOSS,
            CombatTier.ELITE,
        ):
            self.max_energy += 1
        if items.relics["Du-Vu Doll"] in self.relics:
            num_curses = len(
                [card for card in self.deck if card.get("Type") == "Curse"]
            )
            if num_curses > 0:
                ansiprint("From <bold>Du-Vu Doll</bold>: ", end="")
                ei.apply_effect(self, self, "Strength", num_curses)
        if items.relics["Pantograph"] in self.relics and combat_type == CombatTier.BOSS:
            ansiprint("From <bold>Pantograph</bold>: ", end="")
            self.health_actions(25, "Heal")
        if items.relics["Fossilized Helix"] in self.relics:
            ei.apply_effect(self, self, "Buffer", 1)
        if items.relics["Thread and Needle"] in self.relics:
            self.buff("Plated Armor", 4, False)
        if items.relics["Akabeko"] in self.relics:
            self.buff("Vigor", 8, False)
        if (
            self.ancient_tea_set is True
            and items.relics["Ancient Tea Set"] in self.relics
            and turn == 1
        ):
            self.energy += 2
            ansiprint("You gained 2 Energy from <bold>Ancient Tea Set</bold>")
        if items.relics["Bag of Marbles"] in self.relics:
            for enemy in active_enemies:
                ansiprint("From <bold>Bag of Marbles</bold>: ", end="")
                self.debuff("Vulnerable", 1, enemy, False)
        # Bag of Preparation and Ring of the Snake are coded in the .draw_cards() method above.
        if items.relics["Blood Vial"] in self.relics:
            ansiprint("From <bold>Blood Vial</bold>: ", end="")
            self.health_actions(2, "Heal")
        if items.relics["Bronze Scales"] in self.relics:
            ansiprint("From <bold>Bronze Scales</bold>: ", end="")
            self.buff("Thorns", 3, False)
        if items.relics["Oddly Smooth Stone"] in self.relics:
            ansiprint("From <bold>Oddly Smooth Stone</bold>: ", end="")
            self.buff("Dexterity", 1, False)
        if items.relics["Data Disk"] in self.relics:
            ansiprint("From <bold>Data Disk</bold>: ", end="")
            self.buff("Focus", 1, False)
        if items.relics["Philosopher's Stone"] in self.relics:
            for enemy in active_enemies:
                ei.apply_effect(enemy, self, "Strength", 1)
        if items.relics["Mark of Pain"] in self.relics:
            for _ in range(2):
                self.hand.append(deepcopy(items.cards["Wound"]))

    def die(self):
        view.clear()
        ansiprint("<red>You Died</red>")
        input("Press enter > ")
        sys.exit()

    def end_of_combat_effects(self, combat_type):
        if items.relics["Slaver's Collar"] in self.relics and combat_type in (
            CombatTier.BOSS,
            CombatTier.ELITE,
        ):
            self.max_energy -= 1
        if items.relics[
            "Meat on the Bone"
        ] in self.relics and self.health <= math.floor(self.max_health * 0.5):
            ansiprint("<bold>Meat on the Bone</bold> activated.")
            self.health_actions(12, "Heal")
        if items.relics["Burning Blood"] in self.relics:
            ansiprint("<bold>Burning Blood</bold> activated.")
            self.health_actions(6, "Heal")
        elif items.relics["Black Blood"] in player.relics:
            ansiprint("<bold>Black Blood</bold> activated.")
            self.health_actions(12, "Heal")
        if self.buffs["Repair"] > 0:
            ansiprint("<light-cyan>Self Repair</light-cyan>: ", end="")
            self.health_actions(self.buffs["Repair"], "Heal")

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
            turn = data
            ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
            self.energy = self.energy if items.relics["Ice Cream"] in self.relics else 0
            self.energy += (
                self.energy_gain + self.buffs["Energized"] + self.buffs["Berzerk"]
            )
            if self.buffs["Energized"] > 0:
                ansiprint(
                    f"You gained {self.buffs['Energized']} extra energy because of <light-cyan>Energized</light-cyan>"
                )
                self.buffs["Energized"] = 0
                ansiprint("<light-cyan>Energized wears off.")
            if self.buffs["Berzerk"] > 0:
                ansiprint(
                    f"You gained {self.buffs['Berzerk']} extra energy because of <light-cyan>Berzerk</light-cyan>"
                )
            if self.buffs["Barricade"]:
                if turn > 1:
                    ansiprint(
                        "You kept your block because of <light-cyan>Barriacade</light-cyan>"
                    )
            elif items.relics["Calipers"] in self.relics and self.block > 15:
                self.block -= 15
                ansiprint(
                    f"You kept {self.block} <light-blue>Block</light-blue> because of <bold>Calipers</bold>"
                )
            else:
                self.block = 0
            self.draw_cards(False)
            self.plays_this_turn = 0
            ei.tick_effects(self)
            self.fresh_effects.clear()
        elif message == Message.END_OF_TURN:
            self.discard_pile += self.hand
            if items.relics["Runic Pyramid"] not in self.relics:
                self.hand.clear()
            sleep(1)
            view.clear()


class Enemy(Registerable):
    registers = [Message.START_OF_TURN, Message.END_OF_TURN, Message.ON_DEATH_OR_ESCAPE]

    def __init__(self, health_range: list, block: int, name: str, powers: dict = None):
        self.uid = uuid4()
        if not powers:
            powers = {}
        actual_health = random.randint(health_range[0], health_range[1])
        self.health = actual_health
        self.max_health = actual_health
        self.block = block
        self.name = name
        self.third_person_ref = (
            f"{self.name}'s"  # Python f-strings suck so I have to use this
        )
        self.past_moves = ["place"] * 3
        self.intent: str = ""
        self.next_move: list[tuple[str, str, tuple] | tuple[str, tuple]] = ""
        self.state = EnemyState.ALIVE
        self.buffs = ei.init_effects("Enemy Buffs") | powers
        self.debuffs = ei.init_effects("Enemy Debuffs")
        self.stolen_gold = 0
        self.awake_turns = 0
        self.mode = ""
        self.flames = -1
        self.upgrade_burn = False
        self.active_turns = 1
        if "louse" in self.name:
            self.buffs["Curl Up"] = random.randint(3, 7)

    def __str__(self):
        return "Enemy"

    def __repr__(self):
        status = f"{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue>) | "
        for buff in self.buffs:
            if self.buffs[buff] is True or self.buffs[buff] > 0:
                status += f"<buff>{buff}</buff>{f' {self.buffs[buff]}' if isinstance(self.buffs[buff], int) else ''} | "
        for debuff in self.debuffs:
            if self.debuffs[debuff] is True or self.debuffs[debuff] > 0:
                status += f"<debuff>{debuff}</debuff>{f' {self.debuffs[debuff]}' if isinstance(self.debuffs[debuff], int) else ''} | "
        if self.flames > 0:
            status += f"<yellow>{self.flames} Flames</yellow> | "
        actual_intent, _ = view.display_actual_damage(self.intent, player, self)
        status += (
            "Intent: " + actual_intent
            if items.relics["Runic Dome"] not in player.relics
            else "<light-black>Hidden</light-black>"
        )
        return status

    def show_effects(self):
        for buff in self.buffs:
            ansiprint(
                f'<buff>{buff}</buff>: {ei.ALL_EFFECTS[buff].replace("X", str(self.buffs[buff]))})'
            )
        for debuff in self.debuffs:
            ansiprint(
                f'<debuff>{debuff}</debuff>: {ei.ALL_EFFECTS[debuff].replace("X", str(self.debuffs[debuff]))}'
            )

    def set_intent(self):
        pass

    def execute_move(self):
        moves = 1
        display_name = "DEFAULT: UNKNOWN"
        for action in self.next_move:
            if moves == 1 and len(action) > 2:
                display_name, action, parameters = action
            else:
                action, parameters = action
            if action in ("Cowardly", "Sleeping", "Stunned") or action not in (
                "Attack",
                "Buff",
                "Debuff",
                "Status",
                "Block",
            ):
                self.misc_move()
                sleep(1)
                view.clear()
                return
            ansiprint(f"<bold>{display_name}</bold>\n" if moves == 1 else "", end="")
            sleep(0.6)
            if action == "Attack":
                dmg = parameters[0]
                times = parameters[1] if len(parameters) > 1 else 1
                self.attack(dmg, times)
            elif action == "Buff":
                buff_name = parameters[0]
                amount = parameters[1] if len(parameters) > 1 else 1
                target = parameters[2] if len(parameters) > 2 else self
                ei.apply_effect(target, self, buff_name, amount)
            elif action == "Debuff":
                debuff_name = parameters[0]
                amount = parameters[1] if len(parameters) > 1 else 1
                ei.apply_effect(self, self, debuff_name, amount)
            elif action == "Remove Effect":
                effect_name = parameters[0]
                effect_type = parameters[1]
                self.remove_effect(effect_name, effect_type)
            elif action == "Status":
                assert (
                    len(parameters) >= 3
                ), f"Status action requires 3 parameters: given {parameters}"
                status = parameters[0]
                amount = parameters[1]
                location = parameters[2].lower()
                self.status(status, amount, location)
            elif action == "Block":
                block = parameters[0]
                target = parameters[1] if len(parameters) > 1 else None
                self.blocking(block, target)
            sleep(0.2)
            moves += 1
        if display_name == "Inferno" and self.flames > -1:
            self.upgrade_burn = True
            self.flames = 0
        sleep(0.5)
        self.past_moves.append(display_name)
        self.active_turns += 1
        if not self.debuffs.get("Asleep"):
            self.awake_turns += 1
        if self.flames > -1:
            self.flames += 1

    def misc_move(self):
        if len(self.next_move[0]) > 2:
            name, func_name, parameters = self.next_move[0]
        else:
            name, func_name = self.next_move[0]
        ansiprint(f"<bold>{name}</bold>")
        sleep(0.6)
        if func_name == "Cowardly":
            ansiprint("<italic>Hehe. Thanks for the money.<italic>")
            self.state = EnemyState.ESCAPED
            ansiprint(f"<italic><red>{self.name} has escaped</red></italic>")
        elif func_name == "Sleeping":
            sleeptalk = parameters[0]
            ansiprint(f"<italic>{sleeptalk}</italic>")
        elif func_name == "Stunned":
            ansiprint("<italic>Stunned!</italic>")
        elif func_name == "Summon":
            enemies = tuple(parameters[0])
            amount = int(parameters[1]) if len(parameters) > 1 else 1
            choice = bool(parameters[2]) if len(parameters) > 2 else False
            self.summon(enemies, amount, choice)
        elif func_name == "Explode":
            pass
        elif func_name == "Rebirth":
            for debuff in self.debuffs:
                if debuff not in ei.NON_STACKING_EFFECTS:
                    self.debuffs[debuff] = 0
                else:
                    self.debuffs[debuff] = False
            self.buffs["Curiosity"] = False
            self.buffs["Unawakened"] = False
        elif func_name == "Revive":
            self.health = math.floor(self.health * 0.5)
            ansiprint(f"<bold>{self.name}</bold> revived!")
        elif func_name == "Charging":
            message = parameters[0]
            ansiprint(f"{message}")
        elif func_name == "Split":
            split_into = {
                "Slime Boss": (
                    Enemy(self.health, 0, "Acid Slime(L)"),
                    Enemy(self.health, 0, "Spike Slime (L)"),
                ),
                "Acid Slime (L)": (
                    Enemy(self.health, 0, "Acid Slime(M)"),
                    Enemy(self.health, 0, "Acid Slime(M)"),
                ),
                "Spike Slime (L)": (
                    Enemy(self.health, 0, "Spike Slime (M)"),
                    Enemy(self.health, 0, "Spike Slime (M)"),
                ),
            }
            for _ in range(2):
                active_enemies.append(split_into[self.name])
            ansiprint(f"{self.name} split into 2 {split_into[self.name].name}s")
        self.active_turns += 1

    def die(self):
        """
        Dies.
        """
        print(f"{self.name} has died.")
        if items.relics["Gremlin Horn"] in player.relics:
            player.energy += 1
            player.draw_cards(True, 1)
        self.state = EnemyState.DEAD

    def debuff_and_buff_check(self):
        """
        Not finished
        """

    def move_spam_check(self, target_move, max_count):
        """Returns False if the move occurs [max_count] times in a row. Otherwise returns True"""
        use_count = 0

        for move in self.past_moves:
            if move == target_move:
                use_count += 1
                if use_count == max_count:
                    return False
            else:
                use_count = 0

        return True

    def attack(self, dmg: int, times: int):
        for _ in range(times):
            bus.publish(Message.BEFORE_ATTACK, (self, dmg, player.block))
            if dmg <= player.block:
                player.block -= dmg
                dmg = 0
                ansiprint("<light-blue>Blocked</light-blue>")
            elif dmg > player.block:
                dmg -= player.block
                dmg = max(0, dmg)
                ansiprint(f"{self.name} dealt {dmg}(<light-blue>{player.block} Blocked</light-blue>) damage to you.")
                player.block = 0
                player.health -= dmg
                bus.publish(Message.ON_PLAYER_HEALTH_LOSS, None)
            bus.publish(Message.AFTER_ATTACK, (self, dmg, player.block))
        sleep(1)

    def remove_effect(self, effect_name, effect_type):
        if effect_name not in ei.ALL_EFFECTS:
            raise ValueError(
                f"{effect_name} is not a member of any debuff or buff list."
            )
        effect_types = {"Buffs": self.buffs, "Debuffs": self.debuffs}
        if effect_name not in ei.NON_STACKING_EFFECTS:
            effect_types[effect_type][effect_name] = 0
        else:
            effect_types[effect_type][effect_name] = False

    def blocking(self, block: int, target: "Enemy" = None):
        if not target:
            target = self
        target.block += block
        ansiprint(f"{target.name} gained {block} <blue>Block</blue>")
        sleep(1)

    def status(self, status_card: Card, amount: int, location: str):
        locations = {
            "draw pile": player.draw_pile,
            "discard pile": player.discard_pile,
            "hand": player.hand,
        }
        pile = locations[location]
        status_card = status_card()
        for _ in range(amount):
            upper_bound = len(location) - 1 if len(location) > 0 else 1
            insert_index = random.randint(0, upper_bound)
            pile.insert(insert_index, deepcopy(status_card))
        ansiprint(
            f"{player.name} gained {amount} {status_card.name} \nPlaced into {location}"
        )
        sleep(1)

    def summon(self, enemy, amount: int, random_enemy: bool):
        if len(enemy) == 1:
            enemy = enemy[0]
        for _ in range(amount):
            chosen_enemy = random.choice(enemy) if random_enemy else enemy
            active_enemies.append(chosen_enemy)
            ansiprint(f"<bold>{chosen_enemy.name}</bold> summoned!")

    def end_of_turn_effects(self):
        if self.buffs["Ritual"] > 0:
            ansiprint("<light-cyan>Ritual</light-cyan>: ", end="")
            ei.apply_effect(self, self, "Strength", self.buffs["Ritual"])
        if self.buffs["Metallicize"] > 0:
            ansiprint("<light-cyan>Metallicize</light-cyan>: ", end="")
            self.blocking(self.buffs["Metallicize"])
        if self.buffs["Plated Armor"] > 0:
            ansiprint("<light-cyan>Plated Armor</light-cyan>: ", end="")
            self.blocking(self.buffs["Plated Armor"])
        if self.buffs["Regen"] > 0:
            ansiprint("<light-cyan>Regen</light-cyan>: ", end="")
            self.health = min(self.health + self.buffs["regen"], self.max_health)
        if self.buffs["Strength Up"] > 0:
            ansiprint("<light-cyan>Strength Up</light-cyan>: ", end="")
            ei.apply_effect(self, self, "Strength", self.buffs["Strength Up"])

    def callback(self, message, data):
        if message == Message.START_OF_TURN:
            ansiprint(f"{self.name}'s current state: {self.state}")
            if self.state == EnemyState.ALIVE:
                ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
                if "Block" not in self.intent:  # Checks the last move(its intent hasn't been updated yet) used to see if the enemy Blocked last turn
                    if self.buffs["Barricade"] is False:
                        self.block = 0
                    else:
                        if self.active_turns > 1 and self.block > 0:
                            ansiprint(f"{self.name}'s Block was not removed because of <light-cyan>Barricade</light-cyan")
                ei.tick_effects(self)
                print()
                self.set_intent()
        elif message == Message.END_OF_TURN:
            if self.state == EnemyState.ALIVE:
                self.execute_move()
            # Needs to be expanded at some point
        elif message == Message.ON_DEATH_OR_ESCAPE:
            event, bus = data
            bus.death_messages.append(event)


def create_player():
    return Player(
        80,
        0,
        3,
        [
            card()
            for card in [
                items.IroncladStrike,
                items.IroncladStrike,
                items.IroncladStrike,
                items.IroncladStrike,
                items.IroncladStrike,
                items.IroncladDefend,
                items.IroncladDefend,
                items.IroncladDefend,
                items.IroncladDefend,
                items.Bash,
            ]
        ],
    )


# Characters
player = create_player()
player.relics.append(items.relics["Burning Blood"])
