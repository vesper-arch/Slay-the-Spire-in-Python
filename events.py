import inspect
import math
import random
from time import sleep
from typing import Callable

from ansi_tags import ansiprint
from definitions import CombatTier
from entities import player
from helper import gen, view
from items import cards, potions, relics


def event_Neow():
    if player.player_class == "Ironclad":
        max_hp_increase = 8
        # max_hp_decrease = 8
    elif player.player_class == "Silent":
        max_hp_increase = 6
        # max_hp_decrease = 7
    elif player.player_class in ('Defect', 'Watcher'):
        max_hp_increase = 7
        # max_hp_decrease = 7

    ansiprint(f"1: <green>+{max_hp_increase} Max HP</green> \n2: <green>Enemies in your first 3 combats have 1 HP.")
    option = 'placehold'
    if option == 1:
        player.health_actions(max_hp_increase, 'Max Health')


def event_BonfireSpirits():
    while True:
        ansiprint("<bold>Bonfire Spirits</bold>")
        ansiprint("""You happen upon a group of what looks like <magenta>purple fire spirits</magenta> dancing around a large bonfire.

The spirits toss small bones and fragments unto the fire, which brilliantly erupts each time. As you approach, the spirits all turn to you, expectantly...""")
        sleep(0.8)
        ansiprint("<bold>[Offer]</bold> Recieve a reward based on the offer.")
        input('Press enter > ')
        offering = view.list_input("What card do you want to offer? > ", player.deck, view.view_piles, lambda card: card.get("Removable") is False, "The card you chose is not removable.")
        ansiprint("<bold>You toss an offering into the bonfire</bold>")
        if player.deck[offering].get("Rarity") == "Curse":
            ansiprint("However, the spirits aren't happy that you offered a <italic><magenta>Curse...</magenta></italic> The card fizzles a meek black smoke. You recieve a... <italic><magenta>something</italic></magenta> in return.")
            sleep(1.5)
            view.clear()
            break
        if player.deck[offering].get("Rarity") == "Basic":
            ansiprint("<italic>Nothing happens...</italic>\n \nThe spirits seem to be ignoring you now. Disapointing...")
            sleep(1.5)
            view.clear()
            break
        if player.deck[offering].get("Rarity") in ('Common', 'Basic'):
            ansiprint("""<italic>The flames grow slightly brighter.</italic>

The spirits continue dancing. You feel slightly warmer from their presense..\n""")
            player.health_actions(5, "Heal")
            sleep(1.5)
            view.clear()
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
    del player.deck[offering]


def event_TheDivineFountain():
    while True:
        ansiprint("<bold>The Divine Fountain</bold>\n")
        sleep(0.8)
        ansiprint("You come across <light-blue>shimmering water</light-blue> flowing endlessly from a fountain on a nearby wall.")
        sleep(0.8)
        ansiprint("<bold>[Drink]</bold> <green>Remove all <bold>Curses</bold></green> from your deck. \n<bold>[Leave]</bold> Nothing happens")
        option = input('> ').lower()
        if option == "drink":
            for card in player.deck:
                if card.get("Type") == "Curse":
                    player.deck.remove(card)
            ansiprint("As you drink the <light-blue>water</light-blue>, you feel a <magenta>dark grasp</magenta> loosen.")
            sleep(1.5)
            view.clear()
            break
        if option == 'leave':
            print("Unsure of the nature of this water, you continue on your way, parched.")
            sleep(1.5)
            view.clear()
            break
        ansiprint("<red>Valid inputs: ['drink', 'leave']</red>(not caps sensitive)")
        sleep(1.5)
        view.clear()


def event_Duplicator():
    while True:
        ansiprint("<bold>Duplicator</bold>\n")
        sleep(0.8)
        print("Before you lies a dedicated altar to some ancient entity.")
        sleep(0.8)
        ansiprint("<bold>[Pray]</bold> <green>Duplicate a card in your deck</green> \n<bold>[Leave]</bold> Nothing happens")
        option = input('> ').lower()
        if option == 'pray':
            duplicate = view.list_input("What card do you want to duplicate? > ", player.deck, view.view_piles)
            player.deck.append(player.deck[duplicate])
            print("You kneel respectfully. A ghastly mirror image appears from the shrine and collides into you.")
            sleep(1.5)
            view.clear()
            break
        if option == 'leave':
            print("You ignore the shrine, confident in your choice.")
            sleep(1.5)
            view.clear()
            break
        ansiprint("<red>Valid inputs: ['leave', 'pray']</red>(not caps sensitive)")
        sleep(1.5)
        view.clear()


def event_GoldenShrine():
    while True:
        ansiprint("<bold>Golden Shrine</bold>")
        sleep(0.8)
        print("Before you lies an elaborate shrine to an ancient spirit.")
        sleep(0.8)
        ansiprint("<bold>[Pray]</bold> <green>Gain 100 gold</green> \n<bold>[Desecrate]</bold> <green>Gain 275 gold.</green> <red>Become <bold>Cursed - <keyword>Regret</keyword></bold></red> \n<bold>[Leave]</bold> Nothing happens")
        ansiprint("<curse>Regret</curse> | <yellow><keyword>Unplayable</keyword>. At the end of your turn, lose 1 HP for each card in your hand.</yellow>")
        option = input('> ').lower()
        if option == 'pray':
            player.gain_gold(100, False)
            ansiprint("As your hand touches the shrine, <yellow>gold</yellow> rains from the ceiling showering you in riches.")
            sleep(1.5)
            view.clear()
            break
        if option == 'desecrate':
            player.gain_gold(275, False)
            ansiprint("""Each time you strike the shrine, <yellow>gold</yellow> pours forth again and again!

As you pocket the riches, something <red>weighs heavily on you.</red>""")
            player.deck.append(cards["Regret"])
            ansiprint(f"{player.name} gained <curse>Regret</curse>")
            sleep(1.5)
            view.clear()
            break
        if option == 'leave':
            print("You ignore the shrine.")
            sleep(1.5)
            view.clear()
            break
        ansiprint("<red>Valid inputs: ['pray', 'desecrate', 'leave']</red>(Not caps sensitive)")
        sleep(1.5)
        view.clear()


def event_Lab():
    ansiprint("<bold>Lab</bold>")
    print()
    sleep(1)
    print("""You find yourself in a room filled with racks of test tubes, beakers, flasks, forceps, pinch clamps, stirring rods, tongs, goggles, funnels, pipets, cylinders, condensers, and even a rare spiral tube of glass.

Why do you know the name of all these tools? It doesn't matter, you take a look around.""")
    ansiprint("<bold>[Search]</bold> <green>Obtain 3 random potions</green>")
    input('Press enter > ')
    gen.claim_potions(True, 3, player, potions)

# Won't add the Match and Keep event because i just don't know how to.


def event_OminousForge():
    while True:
        ansiprint("<bold>Ominous Forge</bold>")
        sleep(0.8)
        print("You duck into a small hut. Inside, you find what appears to be a forge. The smithing tools are covered with dust, yet a fire roars inside the furnace. You feel on edge...")
        sleep(0.8)
        ansiprint("<bold>[Forge]</bold> <green>Upgrade a Card</green> \n<bold>[Rummage]</bold> <green>Obtain Warped Tongs.</green> <red>Become <keyword>Cursed | Pain</keyword></red> \n<bold>[Leave]</bold> Nothing happens")
        option = input('> ').lower()
        if option == 'forge':
            option = view.list_input("What card do you want to upgrade? > ", player.deck, view.upgrade_preview, lambda card: not card.get("Upgraded") and (card['Name'] == "Burn" or card['Type'] not in ("Status", "Curse")), "That card is not upgradeable.")
            player.deck[option] = player.card_actions(player.deck[option], "Upgrade", cards)
            break
        if option == 'rummage':
            ansiprint('''You decide to see if you can find anything of use. After uncovering tarps, looking through boxes, and checking nooks and crannies, you find a dust covered <yellow>relic!</yellow>.

Taking the relic, you can't shake a sudden feeling of <red>sharp pain</red> as you exit the hut. Maybe you disturbed some sort of spirit?''')
            gen.claim_relics(False, player, 1, relics, [relics['Warped Tongs']])
            gen.card_rewards(CombatTier.NORMAL, False, player, cards, [cards['Pain']])
            break
    input('Press enter to continue > ')
    sleep(1)
    view.clear()


def event_Purifier():
    while True:
        ansiprint('<bold>Purifier</bold>')
        sleep(0.8)
        ansiprint('Before you lies an elaborate shrine to a forgotten spirit.')
        sleep(0.8)
        ansiprint("<bold>[Pray]</bold> <green>Remove a card from your deck.</green> \n<bold>[Leave]</bold> Nothing happens.")
        option = input('')
        if option == 'pray':
            view.view_piles(player.deck, player, False, 'Removable')
            remove_card = view.list_input('What card do you want to remove?', player.deck, view.view_piles, lambda card: card.get("Removable") is False, "That card is not removable.")
            player.deck[remove_card] = player.card_actions(player.deck[remove_card], 'Remove', cards)
            print('As you kneel in reverence, you feel a weight lifted off your shoulders.')
            break
        if option == 'leave':
            print('You ignore the shrine.')
            break
        ansiprint('<red>Valid inputs: ["pray", "leave"]</red>')
        sleep(1.5)
        view.clear()
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()


def event_Transmogrifier():
    while True:
        ansiprint('<bold>Transmogrifier</bold>')
        sleep(0.8)
        ansiprint('Before you lies an elaborate shrine to a forgotten spirit.')
        sleep(0.8)
        ansiprint('<bold>[Pray]</bold> <green>Transform a card.</green> \n<bold>[Leave]</bold> Nothing happens.')
        option = input('> ').lower()
        if option == 'pray':
            view.view_piles(player.deck, player, False, 'Removable')
            transform_card = view.list_input('What card would you like to transform?', player.deck, view.view_piles, lambda card: card.get("Removable") is False, "That card is not transformable.")
            player.deck[transform_card] = player.card_actions(player.deck[transform_card], 'Transform', cards)
            print('As the power of the shrine flows through you, your mind feels altered.')
            break
        if option == 'leave':
            print('You ignore the shrine.')
            break
        ansiprint("<red>Valid inputs: ['pray'], ['leave']</red>")
        sleep(1.5)
        view.clear()
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()


def event_UpgradeShrine():
    while True:
        ansiprint('<bold>Upgrade Shrine</bold>')
        sleep(0.8)
        print('Before you lies an elaborate shrine to a forgotten spirit.')
        sleep(0.8)
        ansiprint('<bold>[Pray]</bold> <green>Upgrade a card.</green> \n<bold>[Leave]</bold> Nothing happens.')
        option = input('> ').lower()
        if option == 'pray':
            view.upgrade_preview(player.deck)
            upgrade_card = view.list_input('What card do you want to upgrade?', player.deck, view.upgrade_preview, lambda card: not card.get("Upgraded") and (card['Type'] not in ("Status", "Curse") or card['Name'] == 'Burn'), "That card is not upgradeable.")
            player.deck[upgrade_card] = player.card_actions(player.deck[upgrade_card], 'Upgrade', cards)
            break
        if option == 'leave':
            print('You ignore the shrine.')
            break
        ansiprint('<red>Valid inputs: ["pray", "leave"]</red>')
        sleep(1.5)
        view.clear()
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()


def event_WeMeetAgain():
    while True:
        ansiprint('<bold>We Meet Again!</bold>')
        sleep(0.8)
        ansiprint(""""We meet again!"

A cheery disheveled fellow approaches you gleefully. You do not know this man.

"It's me, <yellow>Ranwid!</yellow> Have any goods for me today? The usual? A fella like me can't make it alone, you know?

You eye him suspiciously and consider your options...""")
        sleep(0.8)
        ansiprint("<bold>[Give Potion]</bold> <red>Lose a potion.</red> <green>Recieve a relic.</green> \n<bold>[Give Gold]</bold> <red>Lose a varying amount of gold.</red> <green>Recieve a relic.</green> \n<bold>[Give Card]</bold> <red>Lose a card.</red> <green>Recieve a relic.</green> \n<bold>[Attack]</bold> Nothing happens.")
        option = input('> ').lower()
        if 'give' in option:
            relic_rewards = [relic for relic in relics.values() if relic.get('Rarity') in ('Common', 'Uncommon', 'Rare')]
            if 'potion' in option:
                if len(player.potions) == 0:
                    print("You don't have any potions.")
                    sleep(1.5)
                    view.clear()
                    continue
                remove_potion = random.choice(player.potions)
                print(f"You lost {remove_potion.get('Name')}")
                player.potions.remove(remove_potion)
                ansiprint("""<bold>Ranwid</bold>: "Exquisite! Was feeling parched."

<light-blue>Glup glup glup</light-blue>

He downs the potion in one go and lets out a satisfied burp.""")
            if 'gold' in option:
                if player.gold < 50:
                    print("You don't have enough gold.")
                    sleep(1.5)
                    view.clear()
                    continue
                gold_max = min(player.gold, 150)
                gold_loss = random.randint(50, gold_max)
                player.gold -= gold_loss
                print(f'You lost {gold_loss - abs(player.gold)} Gold.')
                player.gold = max(0, player.gold)
                print(f'You now have {player.gold} Gold.')
                ansiprint('Ranwid: "Magnificent! This will be quite handy if I run into those <red>mask wearing hoodlums</red> again."')
            if 'card' in option:
                valid_cards = [card for card in player.deck if card.get('Removable') is not False and card.get('Bottled') is not True]
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
            ansiprint('''<bold>Ranwid</bold>: "Aaaaagghh!! What a jerk you are sometimes!"

He runs away.''')
            break
        ansiprint("<red>Valid inputs: ['give potion', 'give gold', 'give card', 'attack']</red>")
        sleep(1.5)
        view.clear()
    sleep(1.5)
    view.clear()


def event_TheWomanInBlue():
    valid_potions = {potion: stats for potion, stats in potions.items() if stats.get('Class') == player.player_class}
    while True:
        ansiprint('<bold>The Woman in Blue</bold>')
        sleep(0.8)
        ansiprint("""From the darkness, an arm pulls you into a small shop. As your eyes adjust, you see a pale woman in sharp clothes gesturing towards a wall of potions.

<bold>Pale Woman</bold>: 'Buy a potion. <italic>Now!</italic>' she states.""")
        print()
        sleep(0.8)
        ansiprint('<bold>[Buy 1 Potion]</bold> <yellow>20 Gold</yellow>. \n<bold>[Buy 2 Potions]</bold> <yellow>30 Gold</yellow>. \n<bold>[Buy 3 Potions]</bold> <yellow>40 Gold</yellow>. \n<bold>[Leave]</bold> Nothing happens.')
        option = input('> ').lower()
        if 'potion' in option:
            if '1' in option:
                gen.claim_potions(True, 1, player, valid_potions, False)
                break
            if '2' in option:
                gen.claim_potions(True, 2, player, valid_potions, False)
                break
            if '3' in option:
                gen.claim_potions(True, 3, player, valid_potions, False)
                break
            print('Invalid potion amount.')
            sleep(1.5)
            view.clear()
    ansiprint('''<bold>Pale Woman</bold>: "Good, now leave."

You exit the shop cautiously.''')
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()


def event_FaceTrader():
    face_relics = [relics['Cultist Headpiece'], relics['Face of Cleric'],
                   relics['Ssserpent Head'], relics['Gremlin Visage'], relics["N'loth's Hungry Face"]]
    while True:
        ansiprint('<bold>Face Trader</bold>\n')
        sleep(0.8)
        ansiprint('''You walk by an eerie statue holding several masks...
Something behind you softly whispers, "Stop."

You swerve around to face the statue which is now facing you!

On closer inspection, it's not a statue but a statuesque, gaunt man. Is he even breathing?

<bold>Eerie Man</bold>: "Face. Let me touch? Maybe trade?"''')
        sleep(0.8)
        ansiprint(f'<bold>[Touch]</bold> <green>Gain 75 gold</green>. <red>Lose {math.floor(player.max_health * 0.1)} HP</red> \n<bold>[Trade]</bold> <green>50% Good Face</green> <red>50% Bad Face</red> \n<bold>[Leave]</bold> Nothing happens.')
        option = input('> ').lower()
        if option == 'touch':
            player.gain_gold(75)
            player.take_sourceless_dmg(math.floor(player.max_health * 0.1))
            ansiprint('''<bold>Eerie Man</bold>: "Compensation. Compensation."

Mechanically, he cranes out a neat stack of <yellow>gold</yellow> and places it into your pouch.

<bold>Eerie Man</bold>: "What a nice face. Nice face."

While he touches your face, you begin to feel your life drain out of it!

During this, his mask falls off and shatters. Screaming, he quickly covers his face with all six arms dropping even more masks! Amidst all the screaming and shattering, you escape.

His face was completely blank.''')
            break
        if option == 'trade':
            gen.claim_relics(False, player, 1, relics, [random.choice(face_relics)], False)
            sleep(0.8)
            ansiprint('''<bold>Eerie Man</bold>: "For me? <italic>FOR ME?</italic> Oh yes.. Yes. Yes.. mmm..."

You see one of his arms flicker, <red>and your face is in its hand</red>! Your face has been swapped.

<bold>Eerie Man</bold>: "Nice face. Nice face."''')
            break
        if option == 'leave':
            ansiprint('''<bold>Eerie Man</bold>: "Stop. Stop. Stop. Stop. Stop."

This was probably the right call.''')
            break
        ansiprint('<red>Valid inputs: ["trade", "touch", "leave"]</red>')
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()


def event_BigFish():
    while True:
        ansiprint('<bold>Big Fish</bold> \n')
        sleep(0.8)
        ansiprint('''As you make your way down a long corridor you see a <yellow>banana</yellow>, a <yellow>donut</yellow>, and a <yellow>box</yellow> floating about. No... upon closer inspection they are tied to strings coming from holes in the ceiling. There is a quiet cackling from above as you approach the objects.

What do you do?''')
        print()
        sleep(0.8)
        ansiprint(f'<bold>[Banana]</bold> <green>Heal {math.floor(player.max_health / 3)} HP</green> \n<bold>[Donut]</bold> <green>Max HP +5</green> \n<bold>[Box]</bold> <green>Recieve a relic.</green> <red>Become Cursed: <bold>Regret</bold></red>')
        ansiprint(f'<keyword>Regret</keyword> | <yellow>{cards["Regret"]["Info"]}</yellow>') # curse is purple
        option = input('> ').lower()
        if option == 'banana':
            ansiprint('You eat the <yellow>banana</yellow>. It is nutritious and slightly <light-blue>magical</light-blue>, healing you.')
            sleep(0.5)
            player.health_actions(math.floor(player.max_health / 3), "Heal")
            break
        if option == 'donut':
            ansiprint('You eat the <yellow>donut</yellow>. It really hits the spot! Your Max HP increases.')
            sleep(0.5)
            player.health_actions(5, "Max Health")
            break
        if option == 'box':
            ansiprint('You grab the box. Inside you find a <yellow>relic</yellow>! \nHowever, you really craved the donut... \nYou are filled with sadness, but mostly <red>regret</red>.')
            sleep(1.3)
            gen.claim_relics(False, player, 1, relics, None, False)
            player.deck.append(cards['Regret'])
            ansiprint(f'You obtained <magenta>Regret</magenta> | {cards["Regret"]["Info"]}')
            break
        ansiprint('<red>Valid inputs:</red> ["banana", "donut", "box"]')
        sleep(1.5)
        view.clear()
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()


def event_TheCleric():
    while True:
        ansiprint('<bold>The Cleric</bold>')
        sleep(0.7)
        ansiprint('''A strange blue humanoid with a golden helm approaches you with a huge smile.

"Hello friend! I am <light-blue>Cleric</light-blue>! Are you interested in my services!?" the creature shouts, loudly.''')
        sleep(0.5)
        ansiprint(f'<bold>[Heal]</bold> <red>Lose 35 Gold</red>. <green>Heal {math.floor(player.max_health * 0.25)} HP</green> \n<bold>[Purify]</bold> <red>Lose 50 Gold</red>. Remove a card from your deck. \n<bold>[Leave]</bold> Nothing happens.')
        option = input('> ').lower()
        if option == 'heal':
            if player.gold < 35:
                ansiprint("<red>You don't have enough gold.</red>")
                sleep(1)
                view.clear()
                continue
            player.gold -= 35
            ansiprint("You spent 35 <yellow>Gold</yellow>.")
            player.health_actions(math.floor(player.max_health * 0.25), "Heal")
            break
        if option == 'purify':
            if player.gold < 50:
                ansiprint("<red>You don't have enough gold.</red>")
                sleep(1)
                view.clear()
                continue
            player.gold -= 50
            ansiprint("You spent 50 <yellow>Gold</yellow>.")
            view.view_piles(player.deck, player, False, 'Removable')
            option = view.list_input("What card would you like to remove? > ", player.deck, view.view_piles, lambda card: card.get("Removable") is False, "That card is not removable.")
            ansiprint('''A cold blue flame envelops your body and dissipates.

The creature grins.

<bold>Cleric</bold>: "Cleric talented. Have a good day!"''')
            player.deck[option] = player.card_actions(player.deck[option], "Remove", cards)
            break
        if option == 'leave':
            ansiprint("You don't trust this <light-blue>'Cleric'</light-blue>, so you leave.")
            break
        ansiprint("<red>Valid inputs: ['heal', 'purify', 'leave']</red>")
        sleep(1.5)
        view.clear()
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()

def event_GoldenIdol():
    while True:
        ansiprint("<bold>Golden Idol</bold>")
        sleep(0.8)
        ansiprint("""You come across an inconspicuous pedastal with a <yellow>shining gold idol</yellow> sitting peacefully atop. It looks incredibly valuable.

You're sure you don't see any traps nearby.\n""")
        ansiprint("<bold>[Take]</bold> <green>Obtain <bold>Golden Idol</bold>.</green> <red>Trigger a trap</red> \n<bold>[Leave]</bold> Nothing happens")
        option = input('> ').lower()
        if option.lower() not in ('take', 'leave'):
            sleep(1)
            view.clear()
            continue
        if option == 'take':
            gen.claim_relics(False, player, 1, relics, [relics['Golden Idol']], False)
            ansiprint("""As you grab the idol and stow it away, a giant boulder smashes through the ceiling into the ground next to you.

You realize that the floor is slanted downwards as the boulder starts to roll towards you.""")
            ansiprint(f"<bold>[Outrun]</bold> <red>Become <bold>Cursed</bold></red> - <keyword>Injury</keyword> \n<bold>[Smash]</bold> <red>Take {math.floor(player.max_health * 0.25)} damage</red> \n<bold>[Hide]</bold> <red>Lose {math.floor(player.max_health * 0.08)} Max HP</red>")
            option = input('> ').lower()
            if option == 'outrun':
                ansiprint("""<italic>RUUUUUUUUUUUUUUUN!</italic>

You barely leap into a side passageway as the boulder rushes by. Unfortunatly, it feels like you sprained something.""")
                gen.card_rewards("Normal", False, player, cards, [cards['Injury']])
                break
            if option == 'smash':
                player.take_sourceless_dmg(math.floor(player.max_health * 0.25))
                print('You throw yourself at the boulder with everything you have. When the dust clears, you can make a safe way out.')
                break
            if option == 'hide':
                player.health_actions(-math.floor(player.max_health * 0.08), "Max Health")
                ansiprint('''<italic>SQUISH!</italic>

The boulder flattens you a little as it passes by, but otherwise you can get out of here.''')
                break
        if option == 'leave':
            ansiprint('''If there was ever an obvious trap, this would be it.

You decide not to interfere with objects placed on pedastals.''')
            break
    input('Press enter to leave > ')
    sleep(1.5)
    view.clear()


global_events = [event_BonfireSpirits, event_TheDivineFountain, event_Duplicator, event_GoldenShrine, event_Lab, event_OminousForge,
                 event_Purifier, event_Transmogrifier, event_UpgradeShrine, event_WeMeetAgain, event_TheWomanInBlue]
act1_events = [event_FaceTrader, event_BigFish, event_TheCleric, event_GoldenIdol, ]

def choose_event(game_map) -> Callable:
    while True:
        valid_events: list[Callable] = global_events
        valid_events.extend(act1_events)
        chosen_event = random.choice(valid_events)
        if chosen_event == event_TheCleric and player.gold < 35:
            continue
        if chosen_event == event_TheWomanInBlue and player.gold < 10:
            continue
        if chosen_event == event_WeMeetAgain and player.gold < 50:
            continue
        # Should enable me to have events that need the game map for combat.
        event_args = inspect.getfullargspec(chosen_event)
        return lambda: chosen_event(game_map=game_map) if 'game_map' in event_args[0] else chosen_event

