from os import system
from time import sleep
import math
import random
from entities import player, encounters, generate_card_rewards, generate_potion_rewards
from utility import display_ui, active_enemies, combat_turn, start_combat
import events
from ansimarkup import parse, ansiprint
# Outer loop is for the whole game


def neow_interact():
    print("1: WIP \n2: Enemies in your first 3 combats will have 1 hp \n3:")


def combat(tier):
    killed_enemies = False
    escaped = False
    start_combat(player, encounters)
    while len(active_enemies) > 0:
        # Removes the player's block at the beginning of their turn
        player.block = 0
        for enemy in active_enemies:
            if enemy.barricade is True:
                ansiprint(f"{enemy.name}'s block was not removed because of <light-cyan>Barricade</light-cyan>")
            else:
                enemy.block = 0
        player.energy += player.energy_gain + player.energized
        player.debuff_buff_tick()
        player.draw_cards()
        # Player's turn ends when the their energy is out
        while True:
            print(f"Turn {combat_turn}: ")
            display_ui(player)
            # Asks the user what card they want to use
            try:
                ansiprint("What card do you want to use?(<red>[0] to end turn</red>) > ", end='')
                card_used = int(input("")) - 1
                confirm = input("Are you sure? (y|n) > ").lower()
                if confirm != 'y':
                    sleep(1.5)
                    system("clear")
                    continue
                if len(active_enemies) > 1 and player.hand[card_used].get("Target") is None:
                    target = int(input("What enemy do you want to use it on?")) - 1
                else:
                    target = 0
                if card_used + 1 == 0:
                    system("clear")
                    break
                # Checks if the number the user inputted is within range of the player.hand list
                if card_used in range(0, len(player.hand)) and player.hand[card_used]["Energy"] <= player.energy:
                    player.use_card(player.hand[card_used], active_enemies[target])
                    # if the enemy dies, break out of the current loop, therefore going straight to the end_turn function
                    for enemy in active_enemies:
                        if enemy.health == 0:
                            enemy.die()
                    if len(active_enemies) == 0:
                        killed_enemies = True
                        break
                # prevents from using a card that the player doesn't have enough energy for
                elif player.hand[card_used]["Energy"] > player.energy:
                    system("clear")
                    ansiprint("<red>Not enough energy</red>")
                    sleep(1.5)
                    system("clear")
                    continue
                # Numbers less than one will cause problems and this catches it
                else:
                    system("clear")
                    ansiprint("<red>Card not in inventory.</red>")
                    sleep(1.5)
                    system("clear")
                    continue
            # Won't crash if the user inputted something that wasn't a number
            except ValueError:
                system("clear")
                ansiprint("<red>Please enter an number</red>")
                sleep(1.5)
                system("clear")
                continue
            # Won't crash if the user inputted a card that they didn't have
            except IndexError:
                system("clear")
                ansiprint("<red>Card not in inventory</red>")
                sleep(1.5)
                system("clear")
                continue
        if killed_enemies is True and escaped is False:
            player.hand = []
            player.discard_pile = []
            player.draw_pile = []
            player.exhaust_pile = []
            ansiprint("<green>Combat finished!</green>")
            player.gain_gold(random.randint(10, 20))
            generate_potion_rewards(1)
            generate_card_rewards(tier, 3)
            combat_turn = 0
            sleep(1.5)
            break
        elif escaped is True:
            print("Escaped...")
            sleep(0.8)
            print("You recieve nothing.")
            sleep(1.5)
            system("clear")
            combat_turn = 1
            break
        else:
            player.end_player_turn()
            for enemy in active_enemies:
                enemy.enemy_turn()
                sleep(1.5)
                system("clear")
            combat_turn += 1


def rest():
    """
    Actions:
    Rest: Heal for 30% of you max hp(rounded down)
    Upgrade: Upgrade 1 card in your deck(Cards can only be upgraded once unless stated otherwise)*
    Lift: Permanently gain 1 Strength(Requires Girya, can only be used 3 times in a run)*
    Toke: Remove 1 card from your deck(Requires Peace Pipe)*
    Dig: Obtain 1 random Relic(Requires Shovel)*
    Recall: Obtain the Ruby Key(Max 1 use, availible in normal runs when Act 4 is unlocked)*
    *Not finished*
    """
    while True:
        ansiprint("You come across a <green>Rest Site</green>")
        sleep(1)
        player.show_status(False)
        ansiprint(f"<bold>[Rest]</bold> Heal for 30 percent of your Max HP({math.floor(player.max_health * 0.30)}) \n<bold>[Upgrade]</bold> Upgrade a card in your deck > ", end='')
        action = input('').lower()
        if action == 'rest':
            heal_amount = math.floor(player.max_health * 0.30)
            sleep(1)
            system("clear")
            player.heal(heal_amount)
            while True:
                option = input("[View Deck] or [Leave]").lower()
                if action == 'view deck':
                    display_ui(player, False)
                    action = input("Press enter to leave")
                    system("clear")
                    continue
                elif action == 'leave':
                    print("You leave...")
                    print()
                    sleep(1.5)
                    system("clear")
                    break
                else:
                    print("Invalid input")
                    sleep(1.5)
                    system("clear")
        elif action == 'upgrade':
            pass
        else:
            print("Invalid input")
            sleep(1.5)
            system("clear")


order_of_encounters = [combat, rest, combat, combat, rest, rest, combat, combat, combat]
for encounter in order_of_encounters:
    if callable(encounter):
        encounter()
    elif encounter == combat:
        combat("Normal")