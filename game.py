import math
import random
from time import sleep

import game_map
from ansi_tags import ansiprint
from definitions import CombatTier, EncounterType, EnemyState
from enemy_catalog import (
    create_act1_boss,
    create_act1_elites,
    create_act1_normal_encounters,
)
from entities import Enemy, Player, player
from events import choose_event
from helper import ei, gen, view
from items import activate_sacred_bark, cards, potions, relics
from message_bus_tools import Message, bus
from shop import Shop


class Game:
    def __init__(self, seed=None):
        self.bus = bus
        self.seed = seed
        self.game_map: list = None

    def start(self):
        if self.seed is not None:
            random.seed(self.seed)
        self.game_map = game_map.create_first_map()
        self.game_map.pretty_print()
        for encounter in self.game_map:
            self.play(encounter, self.game_map)
            player.floors += 1
            self.game_map.pretty_print()

    def play(self, encounter: EncounterType, game_map: game_map.GameMap):
        if encounter.type == EncounterType.START:
            pass
        elif encounter.type == EncounterType.REST_SITE:
            return rest_site()
        elif encounter.type == EncounterType.UNKNOWN:
            return unknown(self.game_map)
        elif encounter.type == EncounterType.BOSS:
            return Combat(tier=CombatTier.BOSS, player=player, game_map=self.game_map).combat(game_map)
        elif encounter.type == EncounterType.ELITE:
            return Combat(tier=CombatTier.ELITE, player=player, game_map=self.game_map).combat(game_map)
        elif encounter.type == EncounterType.NORMAL:
            return Combat(tier=CombatTier.NORMAL, player=player, game_map=self.game_map).combat(game_map)
        elif encounter.type == EncounterType.SHOP:
            return Shop(player).loop()
        else:
            raise game_map.MapError(f"Encounter type {encounter} is not valid.")

class Combat:
    def __init__(self, tier: CombatTier, player: Player, game_map, all_enemies: list[Enemy] = None):
        self.tier = tier
        self.player = player
        self.all_enemies = all_enemies if all_enemies else []
        self.active_enemies = [enemy for enemy in self.all_enemies if enemy.state == EnemyState.ALIVE]
        self.previous_enemy_states = ()
        self.death_messages = []
        self.turn = 1
        self.game_map = game_map

    def combat(self, current_map) -> None:
        """There's too much to say here."""
        self.start_combat()
        # Combat automatically ends when all enemies are dead.
        while len(self.active_enemies) > 0:
            bus.publish(Message.START_OF_TURN, (self.turn,))
            while True:
                self.update_death_messages()
                self.previous_enemy_states = tuple(enemy.state for enemy in self.all_enemies)
                self.active_enemies = [enemy for enemy in self.all_enemies if enemy.state == EnemyState.ALIVE]  # Updates the list
                if all((enemy.state == EnemyState.DEAD for enemy in self.all_enemies)):
                    self.end_combat(killed_enemies=True)
                    break
                # if all((enemy.state  for enemy in self.active_enemies)):
                #     self.end_combat(robbed=True)
                #     break
                # Todo: Move this to the Unceasing Top Relic
                _ = (
                    player.draw_cards(True, 1)
                    if len(player.hand) == 0
                    and relics["Unceasing Top"] in player.relics
                    else None
                )  # Assigned to _ so my linter shuts up

                print(f"Turn {self.turn}: ")
                # Shows the player's potions, cards(in hand), amount of cards in discard and draw pile, and shows the status for you and the enemies.
                view.display_ui(player, self.active_enemies)
                print(
                    "1-0: Play card, P: Play Potion, M: View Map, D: View Deck, A: View Draw Pile, S: View Discard Pile, X: View Exhaust Pile, E: End Turn, F: View Debuffs and Buffs"
                )
                action = input("> ").lower()
                other_options = {
                    "d": lambda: view.view_piles(player.deck, end=True),
                    "a": lambda: view.view_piles(
                        player.draw_pile, shuffle=True, end=True
                    ),
                    "s": lambda: view.view_piles(player.discard_pile, end=True),
                    "x": lambda: view.view_piles(player.exhaust_pile, end=True),
                    "p": play_potion,
                    "f": lambda: ei.full_view(player, self.active_enemies),
                    "m": lambda: view.view_map(current_map),
                }
                if action.isdigit():
                    option = int(action) - 1
                    if option + 1 in range(len(player.hand) + 1):
                        self.play_new_card(player.hand[option])
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
            bus.publish(
                Message.END_OF_TURN, data=None
            )  # So far I don't need to have anything passed for data
            self.turn += 1

    def end_combat(self, killed_enemies=False, escaped=False, robbed=False):
        if killed_enemies is True:
            potion_roll = random.random()
            ansiprint("<green>Combat finished!</green>")
            player.gain_gold(
                random.randint(10, 20) * 1
                if relics["Golden Idol"] not in self.player.relics
                else 1.25
            )
            if (
                potion_roll < self.player.potion_dropchance
                or relics["White Beast Statue"] in self.player.relics
            ):
                gen.claim_potions(True, 1, player, potions)
                player.potion_dropchance -= 10
            else:
                player.potion_dropchance += 10
            for _ in range(int(relics["Prayer Wheel"] in self.player.relics) + 1):
                gen.card_rewards(self.tier, True, self.player, cards)
            sleep(1.5)
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
        player.unsubscribe()
        for enemy in self.active_enemies:
            enemy.unsubscribe()

    def create_enemies_from_tier(self) -> list[Enemy]:
        act1_normal_encounters = create_act1_normal_encounters()
        act1_elites = create_act1_elites()
        act1_boss = create_act1_boss()
        encounter_types = {
            CombatTier.NORMAL: act1_normal_encounters,
            CombatTier.ELITE: act1_elites,
            CombatTier.BOSS: act1_boss,
        }
        return encounter_types[self.tier][0]

    def start_combat(self) -> list[Enemy]:
        player.register(bus=bus)
        if not self.all_enemies:
            self.all_enemies = self.create_enemies_from_tier()

        for enemy in self.all_enemies:
            enemy.register(bus=bus)

        bus.publish(Message.START_OF_COMBAT, (self.tier, player))
        self.active_enemies = [enemy for enemy in self.all_enemies if enemy.state == EnemyState.ALIVE]
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
                    ansiprint(
                        f"\u001b[1A\u001b[100D<red>You have to enter a number between 1 and {len(self.active_enemies)}</red>",
                        end="",
                    )
                    sleep(1)
                    print("\u001b[2K\u001b[100D", end="")
                    continue
                return target

    def play_new_card(self, card):
        # Prevents the player from using a card that they don't have enough energy for.
        if card.energy_cost > player.energy:
            ansiprint("<red>You don't have enough energy to use this card.</red>")
            sleep(1)
            view.clear()
            return
        # Todo: Move to Velvet Choker relic
        if player.choker_cards_played == 6:
            ansiprint("You have already played 6 cards this turn!")
            sleep(1)
            view.clear()
            return

        if card.target == "Single":
            target = self.select_target()
            player.use_card(card, target=self.active_enemies[target], exhaust=False, pile=player.hand)
        else:
            player.use_card(card, target=self.active_enemies, exhaust=False, pile=player.hand)

    def update_death_messages(self):
        current_states = tuple(enemy.state for enemy in self.all_enemies)
        for i in range(0, max(1, len(self.all_enemies) - 1)):
            if self.previous_enemy_states[i] != current_states[i]:
                self.death_messages.append(current_states[i])


def rest_site():
    """
    Actions:
    Rest: Heal for 30% of your max hp(rounded down)
    Upgrade: Upgrade 1 card in your deck(Cards can only be upgraded once unless stated otherwise)*
    Lift: Permanently gain 1 Strength(Requires Girya, can only be used 3 times in a run)*
    Toke: Remove 1 card from your deck(Requires Peace Pipe)*
    Dig: Obtain 1 random Relic(Requires Shovel)*
    Recall: Obtain the Ruby Key(Max 1 use, availible in normal runs when Act 4 is unlocked)*
    *Not finished*
    """
    # God I hate how long this is. Reminding myself to rewrite this later.
    valid_inputs = ["rest", "smith"]
    if relics["Ancient Tea Set"] in player.relics and not player.ancient_tea_set:
        player.ancient_tea_set = True
        ansiprint("<bold>Ancient Tea Set activated</bold>")
    while True:
        ansiprint(player)
        ansiprint("You come across a <green>Rest Site</green>")
        if relics["Eternal Feather"] in player.relics:
            player.health_actions(len(player.deck) // 5 * 3, "Heal")
        sleep(1)
        ansiprint(f"<bold>[Rest]</bold> <green>Heal for 30% of your <light-blue>Max HP</light-blue>({math.floor(player.max_health * 0.30 + 15 if relics['Regal Pillow'] in player.relics else 0)})</green> \n<bold>[Smith]</bold> <green><keyword>Upgrade</keyword> a card in your deck</green> ")
        ansiprint("+15 from <bold>Regal Pillow</bold>\n" if relics["Regal Pillow"] in player.relics else "", end="",)
        relic_actions = {
            "Girya": (
                "lift",
                "<bold>[Lift]</bold> <green>Gain 1 <light-cyan>Strength</light-cyan></green>",
            ),
            "Peace Pipe": (
                "toke",
                "<bold>[Toke]</bold> <green>Remove a card from your deck</green>",
            ),
            "Shovel": ("dig", "<bold>[Dig]</bold> <green>Obtain a relic</green>"),
        }
        for relic_name, (action, message) in relic_actions.items():
            if relics[relic_name] in player.relics:
                valid_inputs.append(action)
                ansiprint(message, end="")
        action = input("> ").lower()
        if action not in valid_inputs:
            ansiprint("<red>Valid Inputs: " + valid_inputs + "</red>")
            sleep(1.5)
            view.clear()
            continue
        if action == "rest":
            if relics["Coffee Dripper"] in player.relics:
                ansiprint(
                    "<red>You cannot rest because of </red><bold>Coffee Dripper</bold>."
                )
                sleep(1)
                view.clear()
                continue
            # heal_amount is equal to 30% of the player's max health rounded down.
            heal_amount = math.floor(player.max_health * 0.30)
            if relics["Regal Pillow"] in player.relics:
                heal_amount += 15
            sleep(1)
            view.clear()
            player.health_actions(heal_amount, "Heal")
            if relics["Dream Catcher"] in player.relics:
                ansiprint("<bold><italic>Dreaming...</italic></bold>")
                gen.card_rewards(CombatTier.NORMAL, True, player, cards)
            break
        if action == "smith":
            if relics["Fusion Hammer"] in player.relics:
                ansiprint(
                    "<red>You cannot smith because of <bold>Fusion Hammer</bold>.</red>"
                )
                sleep(1.5)
                view.clear()
                continue
            upgrade_card = view.list_input(
                "What card do you want to upgrade?",
                player.deck,
                view.view_piles,
                lambda card: not card.get("Upgraded")
                and (card["Type"] not in ("Status", "Curse") or card["Name"] == "Burn"),
                "That card is not upgradeable.",
            )
            player.deck[upgrade_card] = player.card_actions(
                player.deck[upgrade_card], "Upgrade", cards
            )
            break
        if action == "lift":
            if player.girya_charges > 0:
                ei.apply_effect(player, "Strength", 1)
                player.girya_charges -= 1
                if player.girya_charges == 0:
                    ansiprint("<bold>Girya</bold> is depleted")
                break
            ansiprint("You cannot use <bold>Girya</bold> anymore")
            sleep(1.5)
            view.clear()
            continue
        if action == "toke":
            option = view.list_input(
                "What card would you like to remove? > ",
                player.deck,
                view.view_piles,
                lambda card: card.get("Removable") is False,
                "That card is not removable.",
            )
            player.deck[option] = player.card_actions(
                player.deck[option], "Remove", cards
            )
            break
        if action == "dig":
            gen.claim_relics(False, player, 1, relics, None, False)
            break
    while True:
        ansiprint("<bold>[View Deck]</bold> or <bold>[Leave]</bold>")
        option = input("> ").lower()
        if option == "view deck":
            view.view_piles(player.deck)
            input("Press enter to leave > ")
            sleep(0.5)
            view.clear()
            break
        if option == "leave":
            sleep(1)
            view.clear()
            break
        print("Invalid input")
        sleep(1.5)
        view.clear()


def unknown(game_map) -> None:
    # Chances
    normal_combat: float = 0.1
    treasure_room: float = 0.02
    merchant: float = 0.03
    random_number = random.random()

    if random_number < treasure_room:
        treasure_room = 0.02
        normal_combat += 0.1
        merchant += 0.03
    elif random_number < merchant:
        merchant = 0.03
        treasure_room += 0.02
        normal_combat += 0.1
    elif random_number < normal_combat:
        normal_combat = 0.1
        treasure_room += 0.02
        merchant += 0.03
        Combat(player, CombatTier.NORMAL).combat()
    else:
        # Chooses an event if nothing else is chosen
        ansiprint(player)
        chosen_event = choose_event(game_map)
        chosen_event()


def play_potion():
    if len(player.potions) == 0:
        ansiprint("<red>You have no potions.</red>")
        return
    if relics["Sacred Bark"] in player.relics:
        activate_sacred_bark()
    view.view_potions(player.potions, player.max_potions)
    input("This is currently not implemented. Press enter to leave > ")

