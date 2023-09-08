import random
# import math
from os import system
from time import sleep
from ansimarkup import ansiprint

from entities import player, cards, potions, relics
from utility import list_input, claim_potions

def event_Neow():
    if player.player_class == "Ironclad":
        max_hp_increase = 8
        #max_hp_decrease = 8
    elif player.player_class == "Silent":
        max_hp_increase = 6
        #max_hp_decrease = 7
    elif player.player_class in ('Defect', 'Watcher'):
        max_hp_increase = 7
        #max_hp_decrease = 7

    ansiprint(f"1: <green>+{max_hp_increase} Max HP</green> \n2: <green>Enemies in your first 3 combats have 1 HP.")
    option = 'placehold'
    if option == 1:
        player.health_actions(max_hp_increase, 'Max Health')

def event_BonfireSpirits():
    while True:
        ansiprint("<bold>Bonfire Spirits</bold")
        ansiprint("""You happen upon a group of what looks like <magenta>purple fire spirits</magenta> dancing around a large bonfire.
                 
                  The spirits toss small bones and fragments unto the fire, which brilliantly erupts each time. As you approach, the spirits all turn to you, expectantly...""")
        sleep(0.8)
        ansiprint("<bold>[Offer]</bold> Choose a card in your deck and offer it to the spirits. The offered card will be removed from your deck, and you will receive a reward based on the card's rarity. > ", end="")
        input('Press enter>>')
        counter = 1
        for using_card in player.deck:
            ansiprint(f"{counter}: <light-black>{using_card['Type']}</light-black> | <blue>{using_card['Name']}</blue> | <light-red>{using_card['Energy']} Energy</light-red> | <yellow>{using_card['Info']}</yellow>")
            counter += 1

        offering = list_input("What card do you want to offer? > ", player.deck)

        ansiprint("<bold>You toss an offering into the bonfire</bold>")
        if player.deck[offering].get("Rarity") == "Curse":
            ansiprint("However, the spirits aren't happy that you offered a <italic><magenta>Curse...</magenta></italic> The card fizzles a meek black smoke. You recieve a... <italic><magenta>something</italic></magenta> in return.")
            sleep(1.5)
            system("clear")
            break
        if player.deck[offering].get("Rarity") == "Basic":
            ansiprint("<italic>Nothing happens...</italic>\n \nThe spirits seem to be ignoring you now. Disapointing...")
            sleep(1.5)
            system("clear")
            break
        if player.deck[offering].get("Rarity") in ('Common', 'Basic'):
            ansiprint("""<italic>The flames grow slightly brighter.</italic>
                                            
                        The spirits continue dancing. You feel slightly warmer from their presense..\n""")
            player.health_actions(5, "Heal")
            sleep(1.5)
            system("clear")
            break
        if player.deck[offering].get("Rarity") == "Uncommon":
            ansiprint("""<italic>The flames erupt, growing significantly stronger!</italic>
                                        
                        The spirits dance around you exitedly, filling you with a sense of warmth.\n""")
            player.health_actions(player.max_health, "Heal")
            break
        if player.deck[offering].get("Rarity") == "Rare":
            ansiprint("""<italic>The flames burst, nearly knocking you off your feet, as the fire doubles in strength.</italic>
                             
                        The spirits dance around you excitedly before merging into your form, filling you with warmth and strength\n""")
            player.health_actions(10, "Max Health")
            player.health_actions(player.max_health, "Heal")
            break

def event_TheDivineFountain():
    while True:
        ansiprint("<bold>The Divine Fountain</bold>\n")
        sleep(0.8)
        ansiprint("You come across <light-blue>shimmering water</light-blue> flowing endlessly from a fountain on a nearby wall.")
        sleep(0.8)
        ansiprint("<bold>[Drink]</bold> Remove all <yellow>Curses</yellow> from your deck. \n<bold>[Leave]</bold> Nothing happens", end='')
        option = input('').lower()
        if option == "drink":
            for card in player.deck:
                if card.get("Type") == "Curse":
                    player.deck.remove(card)
            ansiprint("As you drink the <light-blue>water</light-blue>, you feel a <magenta>dark grasp</magenta> loosen.")
            sleep(1.5)
            system("clear")
            break
        if option == 'leave':
            print("Unsure of the nature of this water, you continue on your way, parched.")
            sleep(1.5)
            system("clear")
            break
        ansiprint("<red>Valid inputs: ['drink', 'leave']</red>(not caps sensitive)")
        sleep(1.5)
        system("clear")

def event_Duplicator():
    while True:
        ansiprint("<bold>Duplicator</bold>\n")
        sleep(0.8)
        print("Before you lies a dedicated altar to some ancient entity.")
        sleep(0.8)
        ansiprint("<bold>[Pray]</bold> Duplicate a card in your deck \n<bold>[Leave]</bold> Nothing happens", end='')
        option = input('').lower()
        if option == 'pray':
            for card in player.deck:
                ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                counter += 1
            duplicate = list_input("What card do you want to duplicate? > ", player.deck)
            player.deck.append(player.deck[duplicate])
            print("You kneel respectfully. A ghastly mirror image appears from the shrine and collides into you.")
            sleep(1.5)
            system("clear")
            break
        if option == 'leave':
            print("You ignore the shrine, confident in your choice.")
            sleep(1.5)
            system("clear")
            break
        ansiprint("<red>Valid inputs: ['leave', 'pray']</red>(not caps sensitive)")
        sleep(1.5)
        system("clear")

def event_GoldenShrine():
    while True:
        ansiprint("<bold>Golden Shrine</bold>")
        sleep(0.8)
        print("Before you lies an elaborate shrine to an ancient spirit.")
        sleep(0.8)
        ansiprint("<bold>[Pray]</bold> Gain 100 gold \n<bold>[Desecrate]</bold> Gain 275 gold. Become <yellow>Cursed - Regret</yellow> \n<bold>[Leave]</bold> Nothing happens", end='')
        ansiprint("Regret: <yellow>Unplayable</yellow>. At the end of your turn, lose 1 HP for each card in your hand")
        option = input('').lower()
        if option == 'pray':
            player.gain_gold(100, False)
            ansiprint("As your hand touches the shrine, <yellow>gold</yellow> rains from the ceiling showering you in riches.")
            sleep(1.5)
            system("clear")
            break
        if option == 'desecrate':
            player.gain_gold(275, False)
            ansiprint("""Each time you strike the shrine, <yellow>gold</yellow> pours forth again and again!
                      
                      As you pocket the riches, something <red>weighs heavily on you.</red>""")
            player.deck.append(cards["Regret"])
            ansiprint(f"{player.name} gained <yellow>Regret</yellow>")
            sleep(1.5)
            system("clear")
            break
        if option == 'leave':
            print("You ignore the shrine.")
            sleep(1.5)
            system("clear")
            break
        ansiprint("<red>Valid inputs: ['pray', 'desecrate', 'leave']</red>(Not caps sensitive)")
        sleep(1.5)
        system("clear")

def event_Lab():
    ansiprint("<bold>Lab</bold>")
    print()
    sleep(1)
    print("""You find yourself in a room filled with racks of test tubes, beakers, flasks, forceps, pinch clamps, stirring rods, tongs, goggles, funnels, pipets, cylinders, condensers, and even a rare spiral tube of glass.
          
          Why do you know the name of all these tools? It doesn't matter, you take a look around.""")
    ansiprint("<bold>[Search]</bold> Obtain 3 random potions", end='')
    input('Press enter|')
    claim_potions(True, 3, potions, player)

# Won't add the Match and Keep event because i just don't know how to.

def event_OminousForge():
    while True:
        ansiprint("<bold>Ominous Forge</bold>")
        sleep(0.8)
        print("You duck into a small hut. Inside, you find what appears to be a forge. The smithing tools are covered with dust, yet a fire roars inside the furnace. You feel on edge...")
        sleep(0.8)
        ansiprint("<bold>[Forge]</bold> <green>Upgrade a Card</green> \n<bold>[Rummage]</bold> <green>Obtain Warped Tongs.</green> <red>Become Cursed | Pain</red> \n<bold>[Leave]</bold> Nothing happens", end='')
        option = input('').lower()
        if option == 'forge':
            counter = 1
            for card in player.deck:
                if card.get("Upgraded") is not True:
                    ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                    counter += 1
            try:
                option = int(input("What card do you want to upgrade? > ")) - 1
            except ValueError:
                print("You have to enter a number")
                sleep(1.5)
                system("clear")
                continue
            player.card_actions(player.deck[option], "Upgrade")
            sleep(1.5)
            system('clear')
            break
        if option == 'rummage':
            ansiprint('''You decide to see if you can find anything of use. After uncovering tarps, looking through boxes, and checking nooks and crannies, you find a dust covered <yellow>relic!</yellow>.

Taking the relic, you can't shake a sudden feeling of <red>sharp pain</red> as you exit the hut. Maybe you disturbed some sort of spirit?''')
                      
            

def event_Purifier():
    while True:
        ansiprint('<bold>Purifier</bold>')
        sleep(0.8)
        ansiprint('Before you lies an elaborate shrine to a forgotten spirit.')
        sleep(0.8)
        ansiprint("<bold>[Pray]</bold> <green>Remove a card from you deck.</green> \n<bold>[Leave]</bold> Nothing happens.")
        option = input('')
        if option == 'pray':
            counter = 1
            for card in player.deck:
                if card.get('Removable'):
                    ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
            remove_card = list_input('What card do you want to remove?', player.deck)
            if player.deck[remove_card].get('Removable') is False:
                print(f'{player.deck[remove_card]} cannot be removed from your deck.')
                sleep(1.5)
                system("clear")
                continue
            player.card_actions(player.deck[remove_card], 'Remove')
            print('As you kneel in reverence, you feel a weight lifted off your shoulders.')
            break
        if option == 'leave':
            print('You ignore the shrine.')
            break
        ansiprint('<red>Valid inputs: ["pray", "leave"]</red>')
        sleep(1.5)
        system("clear")
        continue
    sleep(1.5)
    system("clear")

def event_Transmogrifier():
    while True:
        ansiprint('<bold>Transmogrifier</bold>')
        sleep(0.8)
        ansiprint('Before you lies an elaborate shrine to a forgotten spirit.')
        sleep(0.8)
        ansiprint('<bold>[Pray]</bold> <green>Transform a card.</green> \n<bold>[Leave]</bold> Nothing happens.')
        option = input('').lower()
        if option == 'pray':
            counter = 1
            for card in player.deck:
                if card.get('Removable'):
                    ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
            transform_card = list_input('What card would you like to transform?', player.deck)
            if player.deck[transform_card].get('Removable') is False:
                print(f'{player.deck[transform_card]} cannot be transformed.')
                sleep(1.5)
                system("clear")
                continue
            player.card_actions(player.deck[transform_card], 'Transform')
            print('As the power of the shrine flows through you, your mind feels altered.')
            break
        if option == 'leave':
            print('You ignore the shrine.')
            break
        ansiprint("<red>Valid inputs: ['pray'], ['leave']</red>")
        sleep(1.5)
        system("clear")
    sleep(1.5)
    system("clear")

def event_UpgradeShrine():
    while True:
        ansiprint('<bold>Upgrade Shrine</bold>')
        sleep(0.8)
        print('Before you lies an elaborate shrine to a forgotten spirit.')
        sleep(0.8)
        ansiprint('<bold>[Pray]</bold> <green>Upgrade a card.</green> \n<bold>[Leave]</bold> Nothing happens.')
        option = input('').lower()
        if option == 'pray':
            counter = 1
            for card in player.deck:
                if not card.get('Upgraded') and card.get('Type') != 'Curse':
                    ansiprint(f"{counter}: <light-black>{card['Type']}</light-black> | <blue>{card['Name']}</blue> | <light-red>{card['Energy']} Energy</light-red> | <yellow>{card['Info']}</yellow>")
                    counter += 1
                    sleep(0.05)
            upgrade_card = list_input('What card do you want to upgrade?', player.deck)
            if player.deck[upgrade_card].get('Upgraded'):
                print(f'{player.deck[upgrade_card]} is already upgraded.')
                sleep(1.5)
                system("clear")
                continue
            if player.deck[upgrade_card].get('Type') == 'Curse':
                print(f'{player.deck[upgrade_card]} is a Curse.')
                sleep(1.5)
                system("clear")
                continue
            player.card_actions(player.deck[upgrade_card], 'Upgrade')
            break
        if option == 'leave':
            print('You ignore the shrine.')
            break
        ansiprint('<red>Valid inputs: ["pray", "leave"]</red>')
        sleep(1.5)
        system("clear")
    sleep(1.5)
    system("clear")

def event_WeMeetAgain():
    while True:
        ansiprint('<bold>We Meet Again!</bold>')
        sleep(0.8)
        ansiprint(""""We meet again!"
                  
A cheery disheveled fellow approaches you gleefully. You do not know this man.

"It's me, <yellow>Ranwid!</yellow> Have any goods for me today? The usual? A fella like me can't make it alone, you know?

You eye him suspiciously and consider your options...""")
        sleep(0.8)
        ansiprint("<bold>[Give Potion]</bold> <red>Lose a potion.</red> <green>Recieve a relic.</green> \n<bold>[Give Gold]</gold> <red>Lose a varying amount of gold.</red> <green>Recieve a relic.</green> \n<bold>[Give Card]</bold> <red>Lose a card.</red> <green>Recieve a relic.</green> \n<bold>[Attack]</bold> Nothing happens.")
        option = input('').lower()
        if 'give' in option:
            relic_rewards = [relic for relic in relics if relic.get('Rarity') in ('Common', 'Uncommon', 'Rare')]
            if 'potion' in option:
                if len(player.potions) == 0:
                    print("You don't have any potions.")
                    sleep(1.5)
                    system("clear")
                    continue
                remove_potion = random.choice(player.potions)
                print(f"You lost {remove_potion.get('Name')}")
                player.potions.remove(remove_potion)
                ansiprint("""<bold>Ranwid</bold>: "Exquisite! Was feeling parched."
                          
<light-blue>Glup glup glup</light-blue>

He downs the potion in one go and lets out a satisfied burp.""")
            if 'gold' in option:
                if player.gold > 50:
                    print("You don't have enough gold.")
                    sleep(1.5)
                    system("clear")
                    continue
                if player.gold < 150:
                    gold_max = player.gold
                else:
                    gold_max = 150
                gold_loss = random.randint(50, gold_max)
                player.gold -= gold_loss
                print(f'You lost {gold_loss - abs(player.gold)} Gold.')
                player.gold = max(0, player.gold)
                print(f'You now have {player.gold} Gold.')
                ansiprint('Ranwid: "Magnificent! This will be quite handy if I run into those <red>mask wearing hoodlums</red> again."')
            if 'card' in option:
                valid_cards = [card for card in player.deck if card.get('Rarity') not in ('Curse', 'Basic') and card.get('Bottled') is False]
                spend_card = random.choice(valid_cards)
                print(f"You lost {spend_card.get('Name')}")
                player.deck.remove(spend_card)
                print('<bold>Ranwid</bold>: "Exemplary! I shall study this further in my chambers."')
            sleep(0.9)
            ansiprint('''He rummages around his various pockets...

<bold>Ranwid</bold>: "Here, look what I've got for you today! Take it take it!"''')
            player.relics.append(random.choice(relic_rewards))
            print(f'You obtained {player.relics[-1].get("Name")}.')
            sleep(1)
            break
        if option == 'attack':
            print('''<bold>Ranwid</bold>: "Aaaaagghh!! What a jerk you are sometimes!"
                  
                  He runs away.''')
            break
        ansiprint("<red>Valid inputs: ['give potion', 'give gold', 'give card', 'attack']</red>")
        sleep(1.5)
        system("clear")
    sleep(1.5)
    system("clear")

def event_TheWomanInBlue():
    valid_potions = [potion for potion in potions if potion.get('Class') == player.player_class]
    while True:
        ansiprint('<bold>The Woman in Blue</bold>')
        sleep(0.8)
        ansiprint("""From the darkness, an arm pulls you into a small shop. As your eyes adjust, you see a pale woman in sharp clothes gesturing towards a wall of potions.
              
<bold>Pale Woman</bold>: 'Buy a potion. <italic>Now!</italic>' she states.""")
        print()
        sleep(0.8)
        ansiprint('<bold>[Buy 1 Potion]</bold> 20 Gold \n<bold>[Buy 2 Potions]</bold> 30 Gold. \n<bold>[Buy 3 Potions]</bold> 40 Gold. \n<bold>[Leave]</bold> Nothing happens.')
        option = input('').lower()
        if 'potion' in option:
            if '1' in option:
                claim_potions(True, 1, valid_potions, player, False)
                break
            if '2' in option:
                claim_potions(True, 2, valid_potions, player, False)
                break
            if '3' in option:
                claim_potions(True, 3, valid_potions, player, False)
                break
            print('Invalid potion amount.')
            sleep(1.5)
            system("clear")
    ansiprint('''<bold>Pale Woman</bold>: "Good, now leave."
                      
You exit the shop cautiously.''')
    sleep(1.5)
    system("clear")

def event_BigFish():
    # valid_relics = [relic for relic in relics if relic.get('Rarity') not in ('Special', 'Event')]
    ansiprint('''As you make your way down a long corridor you see a <yellow>banana</yellow>, a <yellow>donut</yellow>, and a <yellow>box</yellow> floating about. No... upon closer inspection they are tied to strings coming from holes in the ceiling. There is a quiet cackling from above as you approach the objects.

What do you do?''')
    print()
    sleep(0.8)
    ansiprint()
