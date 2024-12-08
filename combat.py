import random
from time import sleep

import card_catalog
import displayer as view
import effect_interface as ei
import game_map
import generators as gen
import potion_catalog
from ansi_tags import ansiprint
from definitions import CombatTier, State, TargetType
from enemy import Enemy
from enemy_catalog import (
    create_act1_boss,
    create_act1_elites,
    create_act1_normal_encounters,
)
from message_bus_tools import Message, bus
from player import Player


class Combat:
    def __init__(self, tier: CombatTier, player: Player, game_map: game_map.GameMap, all_enemies: list[Enemy] | None = None):
        self.tier = tier
        self.player = player
        self.all_enemies = all_enemies if all_enemies else []
        self.previous_enemy_states = ()
        self.death_messages = []
        self.turn = 1
        self.game_map = game_map

    @property
    def active_enemies(self):
        return [enemy for enemy in self.all_enemies if enemy.state == State.ALIVE]

    def end_conditions(self) -> bool:
        '''Returns True if the combat should end, False otherwise.'''
        return len(self.active_enemies) <= 0 or \
               self.player.state == State.DEAD

    def take_turn(self):
        killed, escaped, robbed = False, False, False
        while True:
            self.on_player_move()
            killed = all((enemy.state == State.DEAD for enemy in self.all_enemies))
            escaped = self.player.state == State.ESCAPED
            if any([killed, escaped, robbed]):
                return killed, escaped, robbed
            print(f"Turn {self.turn}: ")
            # Shows the player's potions, cards(in hand), amount of cards in discard and draw pile, and shows the status for you and the enemies.
            view.display_ui(self.player, self.active_enemies)
            print("1-0: Play card, P: Play Potion, M: View Map, D: View Deck, A: View Draw Pile, S: View Discard Pile, X: View Exhaust Pile, E: End Turn, F: View Debuffs and Buffs")
            action = input("> ").lower()
            other_options = {
                "d": lambda: view.view_piles(self.player.deck, end=True),
                "a": lambda: view.view_piles(
                    self.player.draw_pile, shuffle=True, end=True
                ),
                "s": lambda: view.view_piles(self.player.discard_pile, end=True),
                "x": lambda: view.view_piles(self.player.exhaust_pile, end=True),
                "p": self.play_potion,
                "f": lambda: ei.full_view(self.player, self.active_enemies),
                "m": lambda: view.view_map(self.game_map),
            }
            if action.isdigit():
                option = int(action) - 1
                if option + 1 in range(len(self.player.hand) + 1):
                    self.play_new_card(self.player.hand[option])
                else:
                    view.clear()
                    continue
            elif action in other_options:
                other_options[action]()
            elif action == "e":
                view.clear()
                break
            else:
                view.clear()
                continue
            sleep(1)
            view.clear()
        return killed, escaped, robbed

    def combat(self) -> None:
        """There's too much to say here."""
        self.start_combat()
        while not self.end_conditions():
            assert self.player.health > 0, "Player is dead."
            bus.publish(Message.START_OF_TURN, (self.turn, self.player))
            killed, escaped, robbed = self.take_turn()
            bus.publish(Message.END_OF_TURN, data=(self.player, self.all_enemies))
            self.turn += 1
        self.end_combat(killed_enemies=killed, escaped=escaped, robbed=robbed)

    def end_combat(self, killed_enemies=False, escaped=False, robbed=False):
        if killed_enemies is True:
            potion_roll = random.random()
            ansiprint("<green>Combat finished!</green>")
            self.player.gain_gold(random.randint(10, 20))
            if (potion_roll < self.player.potion_dropchance):
                gen.claim_potions(True, 1, self.player, potion_catalog.create_all_potions())
                self.player.potion_dropchance -= 10
            else:
                self.player.potion_dropchance += 10
            gen.card_rewards(self.tier, True, self.player, card_catalog.create_all_cards())
            view.clear()
        elif escaped is True:
            print("Escaped...")
            sleep(0.8)
            print("You recieve nothing.")
            sleep(1.5)
            view.clear()
        elif robbed:
            print("Robbed...")
            sleep(0.8)
            print("You recieve nothing.")
            sleep(1.2)
            view.clear()
        bus.publish(Message.END_OF_COMBAT, (self.tier, self.player))
        self.player.unsubscribe()
        for enemy in self.all_enemies:
            enemy.unsubscribe()

    def on_player_move(self):
        self.update_death_messages()
        self.previous_enemy_states = tuple(enemy.state for enemy in self.all_enemies)

        def clean_effects(effects):
            for effect in effects:
                if effect.amount <= 0:
                    effect.unsubscribe()
                    ansiprint(f"{effect.get_name()} wears off.")
            return [effect for effect in effects if effect.amount >= 1]

        for enemy in self.active_enemies:
            enemy.buffs = clean_effects(enemy.buffs)
            enemy.debuffs = clean_effects(enemy.debuffs)
        self.player.buffs, self.player.debuffs = [
            clean_effects(effects) for effects in (self.player.buffs, self.player.debuffs)
        ]

    def create_enemies_from_tier(self) -> list[Enemy]:
        act1_normal_encounters = create_act1_normal_encounters(self.all_enemies)
        act1_elites = create_act1_elites()
        act1_boss = create_act1_boss()
        encounter_types = {
            CombatTier.NORMAL: act1_normal_encounters,
            CombatTier.ELITE: act1_elites,
            CombatTier.BOSS: act1_boss,
        }
        return encounter_types[self.tier][0]

    def start_combat(self) -> list[Enemy]:
        self.player.register(bus=bus)
        if not self.all_enemies:
            self.all_enemies = self.create_enemies_from_tier()

        for enemy in self.all_enemies:
            enemy.register(bus=bus)

        bus.publish(Message.START_OF_COMBAT, (self.tier, self.active_enemies, self.player))
        self.previous_enemy_states = tuple(enemy.state for enemy in self.all_enemies)

    def select_target(self):
        if len(self.active_enemies) == 1:
            return 0
        else:
            while True:
                try:
                    target = int(input("Choose an enemy to target > ")) - 1
                    _ = self.active_enemies[target]
                except (IndexError, ValueError):
                    ansiprint(f"\u001b[1A\u001b[100D<red>You have to enter a number between 1 and {len(self.active_enemies)}</red>", end="")
                    sleep(1)
                    print("\u001b[2K\u001b[100D", end="")
                    continue
                return target

    def play_new_card(self, card):
        # Prevents the player from using a card that they don't have enough energy for.
        if card.energy_cost > self.player.energy:
            ansiprint("<red>You don't have enough energy to use this card.</red>")
            sleep(1)
            view.clear()
            return
        # Todo: Move to Velvet Choker relic
        if self.player.choker_cards_played == 6:
            ansiprint("You have already played 6 cards this turn!")
            sleep(1)
            view.clear()
            return

        if card.target == TargetType.SINGLE:
            target = self.select_target()
            self.player.use_card(card, target=self.active_enemies[target], exhaust=False, pile=self.player.hand, enemies=self.all_enemies)
        else:
            self.player.use_card(card, target=self.active_enemies, exhaust=False, pile=self.player.hand, enemies=self.all_enemies)

    def update_death_messages(self):
        current_states = tuple(enemy.state for enemy in self.all_enemies)
        for i in range(0, max(1, len(self.all_enemies) - 1)):
            if self.previous_enemy_states[i] != current_states[i]:
                self.death_messages.append(current_states[i])

    def play_potion(self):
        if len(self.player.potions) == 0:
            ansiprint("<red>You have no potions.</red>")
            return
        chosen_potion = view.list_input("Choose a potion to play", self.player.potions, view.view_potions, lambda potion: potion.playable, "That potion is not playable.")
        if chosen_potion is None:
            return
        potion = self.player.potions.pop(chosen_potion)
        if potion.target == TargetType.YOURSELF:
            potion.apply(self.player)
        elif potion.target == TargetType.SINGLE:
            target = self.select_target()
            potion.apply(self.player, self.active_enemies[target])
        elif potion.target in (TargetType.AREA, TargetType.ANY):
            potion.apply(self.player, self.active_enemies)

