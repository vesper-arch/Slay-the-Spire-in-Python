import random, math
from os import system
from time import sleep
from ansimarkup import ansiprint
from entities import player, cards, generate_potion_rewards
from utility import integer_input


def Neow():
    if player.player_class == "Ironclad":
        max_hp_increase = 8
        max_hp_decrease = 8
    elif player.player_class == "Silent":
        max_hp_increase = 6
        max_hp_decrease = 7
    elif player.player_class == "Defect" or player.player_class == "Watcher":
        max_hp_increase = 7
        max_hp_decrease = 7
    
    ansiprint(f"1: <green>+{max_hp_increase} Max HP</green> \n2: <green>Enemies in your first 3 combats have 1 HP.")
    option = integer_input("")
    if option == 1:
        player.ChangeHealth(max_hp_increase, 'Max Health')

def BonfireSpirits():
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
        
        offering = integer_input("What card do you want to offer? > ", player.deck)

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
        if player.deck[offering].get("Rarity") == "Common" or player.deck[offering].get("Rarity") == "Special":
            ansiprint("""<italic>The flames grow slightly brighter.</italic>
                                            
                        The spirits continue dancing. You feel slightly warmer from their presense..\n""")
            player.ChangeHealth(5, "Heal")
            sleep(1.5)
            system("clear")
            break
        if player.deck[offering].get("Rarity") == "Uncommon":
            ansiprint("""<italic>The flames erupt, growing significantly stronger!</italic>
                                        
                        The spirits dance around you exitedly, filling you with a sense of warmth.\n""")
            player.ChangeHealth(player.max_health, "Heal")
            break
        if player.deck[offering].get("Rarity") == "Rare":
            ansiprint("""<italic>The flames burst, nearly knocking you off your feet, as the fire doubles in strength.</italic>              
                             
                        The spirits dance around you excitedly before merging into your form, filling you with warmth and strength\n""")
            player.ChangeHealth(10, "Max Health")
            player.ChangeHealth(player.max_health, "Heal")
            break

def TheDivineFountain():
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
        elif option == 'leave':
            print("Unsure of the nature of this water, you continue on your way, parched.")
            sleep(1.5)
            system("clear")
            break
        else:
            ansiprint("<red>Valid inputs: ['drink', 'leave']</red>(not caps sensitive)")
            sleep(1.5)
            system("clear")

def Duplicator():
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
            duplicate = integer_input("What card do you want to duplicate? > ", player.deck)
            player.deck.append(player.deck[duplicate])
            print("You kneel respectfully. A ghastly mirror image appears from the shrine and collides into you.")
            sleep(1.5)
            system("clear")
            break
        elif option == 'leave':
            print("You ignore the shrine, confident in your choice.")
            sleep(1.5)
            system("clear")
            break
        else:
            ansiprint("<red>Valid inputs: ['leave', 'pray']</red>(not caps sensitive)")
            sleep(1.5)
            system("clear")
        
def GoldenShrine():
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
        elif option == 'desecrate':
            player.gain_gold(275, False)
            ansiprint("""Each time you strike the shrine, <yellow>gold</yellow> pours forth again and again!
                      
                      As you pocket the riches, something <red>weighs heavily on you.</red>""")
            player.deck.append(cards["Regret"])
            ansiprint(f"{player.name} gained <yellow>Regret</yellow>")
            sleep(1.5)
            system("clear")
            break
        elif option == 'leave':
            print("You ignore the shrine.")
            sleep(1.5)
            system("clear")
            break
        else:
            ansiprint("<red>Valid inputs: ['pray', 'desecrate', 'leave']</red>(Not caps sensitive)")
            sleep(1.5)
            system("clear")

def Lab():
    ansiprint("<bold>Lab</bold>")
    print()
    sleep(1)
    print("""You find yourself in a room filled with racks of test tubes, beakers, flasks, forceps, pinch clamps, stirring rods, tongs, goggles, funnels, pipets, cylinders, condensers, and even a rare spiral tube of glass.
          
          Why do you know the name of all these tools? It doesn't matter, you take a look around.""")
    ansiprint("<bold>[Search]</bold> Obtain 3 random potions", end='')
    input('Press enter|')
    generate_potion_rewards(3)

def OminousForge():
    while True:
        ansiprint("<bold>Ominous Forge</bold>")
        sleep(0.8)
        print("You duck into a small hut. Inside, you find what appears to be a forge. The smithing tools are covered with dust, yet a fire roars inside the furnace. You feel on edge...")
        sleep(0.8)
        ansiprint("<bold>[Forge]</bold> <green>Upgrade a Card</green> \n<bold>[Rummage]</bold> <green>Obtain Warped Tongs.</green> <red>Become Cursed | Pain</red> \n<bold>[Leave]</bold> Nothing happens", end='')
        option = input('')
        if option == 'Forge':
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
            player.ModifyCard(player.deck[option], "Upgrade")
            