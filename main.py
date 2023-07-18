from os import system
from time import sleep
import math
import random
from entities import player, encounters, generate_card_rewards
from utility import display_ui, active_enemies, combat_turn, start_combat
from ansimarkup import parse, ansiprint
# Outer loop is for the whole game


def neow_interact():
    print("1: WIP \n2: Enemies in your first 3 combats will have 1 hp \n3:")


def combat(tier):
    global combat_turn
    combat_turn = 1
    killed_enemies = False
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
        if player.energized > 0:
            player.energized = 0
            ansiprint("<light-cyan>Energized</light-cyan> wears off.")
        if player.strength_down > 0:
            player.strength -= player.strength_down
            ansiprint(f"{player.name}'s <light-red>Strength</light-red> was reduced by {player.strength_down} because of Strength Down")
            ansiprint(f"<light-red>Strength: {player.strength}</light-red>")
            player.strength_down = 0
            print("<light-cyan>Strength Down</light-cyan> wears off.")
        player.draw_cards()
        # Player's turn ends when the their energy is out
        while True:
            display_ui(player)
            # Asks the user what card they want to use
            try:
                ansiprint("What card do you want to use?(<red>[0] to end turn</red>) > ", end='')
                card_used = int(input("")) - 1
                if len(active_enemies) > 1:
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
                    if not active_enemies:
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
        # After the player's energy has run out, discard their cards, give them 5 new ones, refil their energy, and make the enemy attack
        if killed_enemies is True:
            player.hand = []
            player.discard_pile = []
            player.draw_pile = []
            ansiprint("<green>Combat finished!</green>")
            player.gain_gold(random.randint(10, 20))
            generate_card_rewards(tier, 3)
        else:
            player.end_player_turn()
            for enemy in active_enemies:
                enemy.enemy_turn()


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
        try:
            action = int(input("1:Rest(Heal for 30 percent of your max health)\nor \n2:Upgrade a card in you deck?"))
        except ValueError:
            print("You have to enter a number")
            sleep(1)
            system("clear")
            continue
        if action == 1:
            heal_amount = math.floor(player.max_health * 0.30)
            sleep(1)
            system("clear")
            player.heal(heal_amount)
            while True:
                try:
                    action = int(input("1: View your deck \nor \n2: Leave"))
                except ValueError:
                    print("You have to enter a number")
                    sleep(1)
                    system("clear")
                    continue
                break
            if action == 1:
                display_ui(player, False)
                action = input("Press enter to leave")
            elif action == 2:
                print("You leave...")
                print()
                sleep(1.5)
                system("clear")
                break
        elif action == 2:
            pass


order_of_encounters = [combat, rest, combat, combat, rest, rest, combat, combat, combat]
for encounter in order_of_encounters:
    if callable(encounter):
        encounter()
    elif encounter == combat:
        combat("Normal")
