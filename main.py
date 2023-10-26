from time import sleep
import math
import random
from ansimarkup import ansiprint
from events import choose_event
from items import relics, potions, cards, activate_sacred_bark
from entities import player, enemy_encounters
from utility import display_ui, active_enemies, combat_turn, combat_potion_dropchance, start_combat, list_input, claim_potions, card_rewards, view_piles, calculate_actual_damage, calculate_actual_block, clear


def combat(tier) -> None:
    """There's too much to say here."""
    global combat_turn, combat_potion_dropchance
    killed_enemies: bool = False
    # The Smoke Bomb potion allows you to escape from a non-boss encounter but you recieve no rewards.
    escaped: bool = False
    # Spawns enemies and shuffles the player's deck into their draw pile.
    start_combat(player, enemy_encounters)
    if relics['Preserved Insect'] in player.relics and tier == 'Elite':
        for enemy in active_enemies:
            enemy.health -= round(enemy.health * 0.25)
        ansiprint('<bold>Preserved Insect</bold> <blue>activated</blue>.')
    # Combat automatically ends when all enemies are dead.
    while len(active_enemies) > 0:
        # Draws cards, removes block, ticks debuffs, and activates start-of-turn buffs, debuffs, and relics.
        player.start_turn()
        for enemy in active_enemies:
            # Removes block, ticks debuffs and buffs, and triggers buffs and debuffs.
            enemy.start_turn()
        killed_enemies = True
        while True:
            print(f"Turn {combat_turn}: ")
            # Shows the player's potions, cards(in hand), amount of cards in discard and draw pile, and shows the status for you and the enemies.
            display_ui(player)
            ansiprint("1: <blue>Play a card</blue> \n2: <light-red>Play Potion</light-red> \n3: <green>View Relics</green> \n4: <magenta>View debuffs and buffs</magenta> \n5: View deck \n6: View draw pile \n7: View discard pile \n8: End turn")
            commands: dict = {'1': play_card, '2': play_potion, '3': view_relics, '4': (player.show_status, True), '5': player.deck, '6': player.draw_pile, '7': player.discard_pile}
            option = input('')
            if option in ('1', '2', '3'):
                commands.get(option)()
            elif option == '4':
                player.show_status(True)
            elif option in ('5', '6', '7'):
                pile, entity = (commands[option], player)
                view_piles(pile, entity, True)
            elif option == '8':
                sleep(1.5)
                clear()
                break
            else:
                print("Invalid input")
            sleep(1.5)
            clear()
            if len(active_enemies) == 0:
                killed_enemies = True
                break
            continue
        if killed_enemies is True and escaped is False:
            player.hand.clear()
            player.discard_pile.clear()
            player.draw_pile.clear()
            player.exhaust_pile.clear()
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
            clear()
            break
        if escaped is True:
            print("Escaped...")
            sleep(0.8)
            print("You recieve nothing.")
            sleep(1.5)
            clear()
            combat_turn = 1
            break
        # Discards the player's hand, triggers end of turn relics, buffs, and debuffs.
        player.end_player_turn()
        for enemy in active_enemies:
            # Lets the enemy use their moves.
            enemy.enemy_turn()
            input('Press enter to continue > ')
            sleep(1.5)
            clear()
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
    if relics['Ancient Tea Set'] in player.relics and not player.ancient_tea_set:
        player.ancient_tea_set = True
        ansiprint('<italic><light-black>Ancient Tea Set activated</light-black></italic>')
    while True:
        ansiprint("You come across a <green>Rest Site</green>")
        if relics['Eternal Feather'] in player.relics:
            player.health_actions(len(player.deck) // 5 * 3, "Heal")
        sleep(1)
        player.show_status(False)
        ansiprint(f"<bold>[Rest]</bold> Heal for 30 percent of your Max HP({math.floor(player.max_health * 0.30)} {'+ 15 from <bold>Regal Pillow</bold>' if relics['Regal Pillow'] in player.relics else ''}) \n<bold>[Upgrade]</bold> Upgrade a card in your deck > ", end='')
        action = input('').lower()
        if action == 'rest':
            # heal_amount is equal to 30% of the player's max health rounded down.
            heal_amount = math.floor(player.max_health * 0.30)
            if relics['Regal Pillow'] in player.relics:
                heal_amount += 15
            sleep(1)
            clear()
            player.health_actions(heal_amount, "Heal")
            if relics['Dream Catcher'] in player.relics:
                ansiprint('<bold><italic>Dreaming...</italic></bold>')
                card_rewards('Normal', True, player, cards)
            break
        elif action == 'upgrade':
            # Prints all of the non-upgraded cards in the player's deck.
            view_piles(player.deck, player)
            upgrade_card = list_input('What card do you want to upgrade?', player.deck)
            if not upgrade_card:
                sleep(1.5)
                clear()
                continue
            # Upgrades the selected card
            player.card_actions(player.deck[upgrade_card], 'Upgrade')
            break
        else:
            print("Invalid input")
            sleep(1.5)
            clear()
    while True:
        option = input("[View Deck] or [Leave]").lower()
        if option == 'view deck':
            view_piles(player.deck, player)
        elif option == 'leave':
            print("You leave...")
            print()
            sleep(1.5)
            clear()
            break
        else:
            print("Invalid input")
            sleep(1.5)
            clear()

def unknown() -> None:
    # CHances
    normal_combat: float = 0.1
    treasure_room: float = 0.02
    merchant: float = 0.03
    # Event chance is equal to 1 minus all the previous chances
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
        combat('Normal')
    else:
        chosen_event = choose_event()
        chosen_event()

def view_relics():
    counter = 1
    for relic in player.relics:
        ansiprint(f"{counter}: {relic['Name']} | {relic['Class']} | <light-black>{relic['Rarity']}</light-black> | <yellow>{relic['Info']}</yellow> | <blue><italic>{relic['Flavor']}</italic></blue>")
        counter += 1
        sleep(0.05)
    input("Press enter to continue > ")
    sleep(1.5)
    clear()

def play_potion():
    if relics['Sacred Bark'] in player.relics:
        activate_sacred_bark()
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
        view_piles(player.hand, player, False, 'card.get("Playable") is not False')
        card_used = list_input('What card do you want to play?', player.hand)
        if player.hand[card_used].get('Type') == 'Curse' and relics['Blue Candle'] not in player.relics:
            print('<red>This card is a <bold>Curse</bold>.</red>')
            sleep(1.5)
            clear()
            break
        if player.hand[card_used].get('Type') == 'Status' and not player.hand[card_used].get('Playable') and relics['Medical Kit'] not in player.relics:
            print('This card is an <bold>Unplayable Status</bold> card.')
            sleep(1)
            clear()
            break
        if card_used is None:
            sleep(1.5)
            clear()
            break
        playing_card = player.hand[card_used]
        # Prevents the player from using a card that they don't have enough energy for.
        if playing_card.get("Energy") > player.energy:
            ansiprint("<red>You don't have enough energy to use this card.</red>")
            sleep(1.5)
            clear()
            continue
        if playing_card.get("Target") is None and len(active_enemies) > 1:
            target = list_input("What enemy do you want to use it on? >", active_enemies)
            if not target:
                clear()
                continue
        elif len(active_enemies) == 1:
            target = 0
        else:
            target = 0
        # Lets the player go back if they don't want to use the card.
        if player.hand[card_used].get("Block") is None:
            effect, affected_by = calculate_actual_damage(player.hand[card_used]['Info'], active_enemies[target], player, player.hand[card_used])
        else:
            effect, affected_by = calculate_actual_block(player.hand[card_used]['Info'], player)
        ansiprint(f"True effect | {effect}")
        ansiprint(affected_by, '\n')
        option = input("Are you sure? (y|n) > ").lower()
        if option == 'n':
            sleep(1.5)
            clear()
            break
        player.use_card(playing_card, active_enemies[target], False, player.hand)
        break



order_of_encounters = [combat, unknown, rest, combat, combat, unknown, rest]
for encounter in order_of_encounters:
    if encounter.__name__ == 'combat':
        combat('Normal')
    else:
        encounter()
