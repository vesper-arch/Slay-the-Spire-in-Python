from os import system
from time import sleep as wait
import math
from entities import player
from utility import display_ui, active_enemies, combat_turn
from ansimarkup import parse, ansiprint
# Outer loop is for the whole game


def neow_interact():
    print("1: WIP \n2: Enemies in your first 3 combats will have 1 hp \n3:")


def combat():
    global combat_turn
    combat_turn = 1

    while len(active_enemies) > 0:
        # Removes the player's block at the beginning of their turn
        player.block = 0
        for enemy in active_enemies:
            if enemy.barricade is True:
                ansiprint(f"{enemy.name}'s block was not removed because of <light-cyan>Barricade</light-cyan>")
            else:
                enemy.block = 0
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
                    if active_enemies[target].health == 0:
                        system("clear")
                        break
                # prevents from using a card that the player doesn't have enough energy for
                elif player.hand[card_used]["Energy"] > player.energy:
                    system("clear")
                    ansiprint("<red>Not enough energy</red>")
                    wait(1.5)
                    system("clear")
                    continue
                # Numbers less than one will cause problems and this catches it
                else:
                    system("clear")
                    ansiprint("<red>Card not in inventory.</red>")
                    wait(1.5)
                    system("clear")
                    continue
            # Won't crash if the user inputted something that wasn't a number
            except ValueError:
                system("clear")
                ansiprint("<red>Please enter an number</red>")
                wait(1.5)
                system("clear")
                continue
            # Won't crash if the user inputted a card that they didn't have
            except IndexError:
                system("clear")
                ansiprint("<red>Card not in inventory</red>")
                wait(1.5)
                system("clear")
                continue
        # After the player's energy has run out, discard their cards, give them 5 new ones, refil their energy, and make the enemy attack
        player.end_player_turn()


def rest():
    while True:
        ansiprint("You come across a <green>Rest Site</green>")
        wait(1)
        try:
            action = int(input("1:Rest(Heal for 30 percent of your max health)\nor \n2:Upgrade a card in you deck?"))
        except ValueError:
            print("You have to enter a number")
            wait(1)
            system("clear")
            continue
        if action == 1:
            heal_amount = math.floor(player.max_health//100 * 0.30)
            player.heal(heal_amount)
            while True:
                try:
                    action = int(input("1: View your deck \nor \n2: Leave"))
                except ValueError:
                    print("You have to enter a number")
                    wait(1)
                    system("clear")
                    continue
                break
            if action == 1:
                display_ui(player, False)
                action = input("Press enter to leave")
        elif action == 2:
            pass


combat()
