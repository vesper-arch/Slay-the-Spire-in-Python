from os import system
from time import sleep
import math
import random
from entities import player, encounters, generate_card_rewards, generate_potion_rewards
from utility import display_ui, active_enemies, combat_turn, start_combat
import events
from ansimarkup import parse, ansiprint



def combat(tier):
    killed_enemies = False
    escaped = False
    start_combat(player, encounters)
    while len(active_enemies) > 0:
        # Removes the player's block at the beginning of their turn
        player.start_turn()
        for enemy in active_enemies:
            enemy.start_turn()
        # Player's turn ends when the their energy is out
        while True:
            print(f"Turn {combat_turn}: ")
            display_ui(player)
            # Asks the user what card they want to use
            ansiprint("1: <blue>Play a card</blue> \n2: <light-red>View debuffs and buffs</light-red> \n3: <green>Use potions</green> \n4: <magenta>View relics</magenta> \n5: View deck \n6: View draw pile \n7: View discard pile \n8: End turn")
            option = input('')
            if option == '1':
                card_used = integer_input('What card do you want to play?', player.hand)
                if card_used is False:
                    system("clear")
                    continue
                playing_card = player.hand[card_used]
                # Prevents the player from using a card that they don't have enough energy for.
                if playing_card.get("Energy") > player.energy:
                    ansiprint("<red>You don't have enough energy to use this card.</red>")
                    sleep(1.5)
                    system("clear")
                    continue
                # Lets the player go back if they don't want to use the card.
                option = input("Are you sure? (y|n) > ").lower()
                if option == 'n':
                    sleep(1.5)
                    system("clear")
                    continue
                # Cards that either target the player or target all enemies won't ask for a target.
                if playing_card.get("Target") is None:
                    target = integer_input("What enemy do you want to use it on? >", active_enemies)
                    if target is False:
                        system("clear")
                        continue
                elif len(active_enemies) == 1:
                    target = 0
                else:
                    target = 0
                player.use_card(playing_card, target)
                continue
            elif option == '2':
                print(player.name + ': ')
                player.show_status(True)
                input("Press enter to continue > ")
                sleep(1.5)
                system("clear")
                continue
            elif option == '3':
                counter = 1
                for potion in player.potions:
                    ansiprint(f"{counter}: {potion['Name']} | {potion['Class']} | <light-black>{potion['Rarity']}</light-black> | <yellow>{potion['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
                for i in range(player.potion_bag - len(player.potions)):
                    ansiprint(f"<light-black>{counter}: (Empty)</light-black>")
                    counter += 1
                    sleep(0.05)
                "Machine, turn back now."
            elif option == '4':
                counter = 1
                for relic in player.relics:
                    ansiprint(f"{counter}: {relic['Name']} | {relic['Class']} | <light-black>{relic['Rarity']}</light-black> | <yellow>{relic['Info']}</yellow> | <blue><italic>{relic['Flavor']}</italic></blue>")
                    counter += 1
                    sleep(0.05)
                input("Press enter to continue > ")
                sleep(1.5)
                system("clear")
                continue
            elif option == '5':
                counter = 1
                for card in player.deck:
                    ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
                input("Press enter to continue > ")
                sleep(1.5)
                system("clear")
                continue
            elif option == '6':
                shuffled_draw_pile = random.sample(player.draw_pile, len(player.draw_pile))
                counter = 1
                for card in shuffled_draw_pile:
                    ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
                input("Press enter to continue > ")
                sleep(1.5)
                system("clear")
                continue
            elif option == '7':
                counter = 1
                for card in player.discard_pile:
                    ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
                input("Press enter to continue > ")
                sleep(1.5)
                system("clear")
                continue
            elif option == '8':
                sleep(1.5)
                system("clear")
                break
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
