from os import system
from time import sleep
import math
import random
from ansimarkup import ansiprint
from entities import player, enemy_encounters, cards, potions, relics
from utility import display_ui, active_enemies, combat_turn, combat_potion_dropchance, start_combat, list_input, claim_potions, card_rewards



def combat(tier):
    """There's too much to say here."""
    global combat_turn, combat_potion_dropchance
    killed_enemies = False
    # The Smoke Bomb potion allows you to escape from a non-boss encounter but you recieve no rewards.
    escaped = False
    # Spawns enemies and shuffles the player's deck into their draw pile.
    start_combat(player, enemy_encounters)
    if relics['Preserved Insect'] in player.relics and tier == 'Elite':
        for enemy in active_enemies:
            enemy.health -= round(enemy.health * 0.75)
        ansiprint('<bold>Preserved Insect</bold> <blue>activated</blue>.')
    # Combat automatically ends when all enemies are dead.
    while len(active_enemies) > 0:
        # Draws cards, removes block, ticks debuffs, and activates start-of-turn buffs, debuffs, and relics.
        player.start_turn()
        for enemy in active_enemies:
            # Removes block, ticks debuffs and buffs, and triggers buffs and debuffs.
            enemy.start_turn()
        while True:
            print(f"Turn {combat_turn}: ")
            # Shows the player's potions, cards(in hand), amount of cards in discard and draw pile, and shows the status for you and the enemies.
            display_ui(player)
            ansiprint("1: <blue>Play a card</blue> \n2: <light-red>Play Potion</light-red> \n3: <green>View Relics</green> \n4: <magenta>View debuffs and buffs</magenta> \n5: View deck \n6: View draw pile \n7: View discard pile \n8: End turn")
            commands = {'1': play_card, '2': play_potion, '3': view_relics, '4': (player.show_status, True), '5': (view_piles, player.deck), '6': (view_piles, player.draw_pile), '7': (view_piles, player.discard_pile)}
            option = input('')
            if option in ('1', '2', '3'):
                commands.get(option)()
            elif option in ('4', '5', '6', '7'):
                func, args = commands[option]
                func(args)
            elif option == '8':
                sleep(1.5)
                system("clear")
                break
            else:
                print("Invalid input")
            sleep(1.5)
            system("clear")
            continue
        if killed_enemies is True and escaped is False:
            player.hand = []
            player.discard_pile = []
            player.draw_pile = []
            player.exhaust_pile = []
            potion_chance = random.randint(0, 100)
            ansiprint("<green>Combat finished!</green>")
            player.gain_gold(random.randint(10, 20))
            if potion_chance < combat_potion_dropchance:
                claim_potions(True, 1, potions, player)
                combat_potion_dropchance -= 10
            else:
                combat_potion_dropchance += 10
            card_rewards(tier, True, player, cards)
            combat_turn = 0
            sleep(1.5)
            break
        if escaped is True:
            print("Escaped...")
            sleep(0.8)
            print("You recieve nothing.")
            sleep(1.5)
            system("clear")
            combat_turn = 1
            break
        # Discards the player's hand, triggers end of turn relics, buffs, and debuffs.
        player.end_player_turn()
        for enemy in active_enemies:
            # Lets the enemy use their moves.
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
    **Not finished
    """
    if relics['Ancient Tea Set'] in player.relics:
        player.ancient_tea_set = True
        ansiprint('<italic><light-black>Art of War activated</light-black></italic>')
    while True:
        ansiprint("You come across a <green>Rest Site</green>")
        sleep(1)
        player.show_status(False)
        ansiprint(f"<bold>[Rest]</bold> Heal for 30 percent of your Max HP({math.floor(player.max_health * 0.30)}) \n<bold>[Upgrade]</bold> Upgrade a card in your deck > ", end='')
        action = input('').lower()
        if action == 'rest':
            # heal_amount is equal to 30% of the player's max health rounded down.
            heal_amount = math.floor(player.max_health * 0.30)
            if relics['Regal Pillow'] in player.relics:
                heal_amount += 15
            sleep(1)
            system("clear")
            player.health_actions(heal_amount, "Heal")
            if relics['Dream Catcher'] in player.relics:
                ansiprint('<underline><italic>Dreaming...</italic></underline>')
                card_rewards('Normal', True, player, cards)
            break
        elif action == 'upgrade':
            while True:
                # Prints all of the non-upgraded cards in the player's deck.
                view_piles(player.deck, False, True)
                upgrade_card = list_input('What card do you want to upgrade?', player.deck)
                if not upgrade_card:
                    sleep(1.5)
                    system('clear')
                    continue
                # Upgrades the selected card
                player.card_actions(player.deck[upgrade_card], 'Upgrade')
                break
        else:
            print("Invalid input")
            sleep(1.5)
            system("clear")
    while True:
        option = input("[View Deck] or [Leave]").lower()
        if option == 'view deck':
            view_piles(player.deck)
        elif option == 'leave':
            print("You leave...")
            print()
            sleep(1.5)
            system("clear")
            break
        else:
            print("Invalid input")
            sleep(1.5)
            system("clear")


def view_piles(pile, end=False, upgraded=False):
    """Prints a numbered list of all the cards in a certain pile."""
    if pile == player.draw_pile:
        pile = random.sample(pile, len(pile))
    counter = 1
    for card in pile:
        if upgraded is True and card.get('Upgraded'):
            ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            counter += 1
            sleep(0.05)
        else:
            ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
            counter += 1
            sleep(0.05)
    if end:
        input("Press enter to continue > ")
    sleep(1.0)
    if end:
        sleep(0.5)
        system("clear")

def view_relics():
    counter = 1
    for relic in player.relics:
        ansiprint(f"{counter}: {relic['Name']} | {relic['Class']} | <light-black>{relic['Rarity']}</light-black> | <yellow>{relic['Info']}</yellow> | <blue><italic>{relic['Flavor']}</italic></blue>")
        counter += 1
        sleep(0.05)
    input("Press enter to continue > ")
    sleep(1.5)
    system("clear")

def play_potion():
    counter = 1
    for potion in player.potions:
        ansiprint(f"{counter}: {potion['Name']} | {potion['Class']} | <light-black>{potion['Rarity']}</light-black> | <yellow>{potion['Info']}</yellow>")
        counter += 1
        sleep(0.05)
    for _ in range(player.max_potions - len(player.potions)):
        ansiprint(f"<light-black>{counter}: (Empty)</light-black>")
        counter += 1
        sleep(0.05)
    print("Machine, turn back now.")

def play_card():
    while True:
        print()
        view_piles(player.hand, False)
        card_used = list_input('What card do you want to play?', player.hand)
        if not card_used:
            sleep(1.5)
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
        if playing_card.get("Target") is None and len(active_enemies) > 1:
            target = list_input("What enemy do you want to use it on? >", active_enemies)
            if not target:
                system("clear")
                continue
        elif len(active_enemies) == 1:
            target = 0
        else:
            target = 0
        player.use_card(playing_card, active_enemies[target], False, player.hand)
        break



order_of_encounters = [combat, rest, combat, combat, rest, rest, combat, combat, combat]
for encounter in order_of_encounters:
    if callable(encounter):
        if encounter == combat:
            encounter('Normal')
        elif encounter == rest:
            encounter()
