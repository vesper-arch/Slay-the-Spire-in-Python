import math
from time import sleep

import card_catalog
import displayer as view
import effect_interface as ei
import generators as gen
import relic_catalog
from ansi_tags import ansiprint
from definitions import CardType
from message_bus_tools import Message, bus


class RestSite():
    def __init__(self, player):
        self.player = player

    def rest_site(self):
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
        while True:
            ansiprint(self.player)
            ansiprint("You come across a <green>Rest Site</green>")
            bus.publish(Message.WHEN_ENTERING_CAMPFIRE, (self.player))
            sleep(1)
            ansiprint(f"<bold>[Rest]</bold> <green>Heal for 30% of your <light-blue>Max HP</light-blue>({math.floor(self.player.max_health * 0.30)})</green> \n<bold>[Smith]</bold> <green><keyword>Upgrade</keyword> a card in your deck</green> ")
            ansiprint("+15 from <bold>Regal Pillow</bold>\n")
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
            for relic, (action, message) in relic_actions.items():
                if relic in self.player.relics:
                    valid_inputs.append(action)
                    ansiprint(message, end="")
            action = input("> ").lower()
            if action not in valid_inputs:
                ansiprint("<red>Valid Inputs: " + str(valid_inputs) + "</red>")
                sleep(1.5)
                view.clear()
                continue
            if action == "rest":
                # heal_amount is equal to 30% of the player's max health rounded down.
                heal_amount = math.floor(self.player.max_health * 0.30)
                sleep(1)
                view.clear()
                self.player.health_actions(heal_amount, "Heal")
                break
            if action == "smith":
                upgrade_card = view.list_input(
                    "What card do you want to upgrade?",
                    self.player.deck,
                    view.view_piles,
                    lambda card: not card.upgraded
                    and (card.type not in (CardType.STATUS, CardType.CURSE) or card.name == "Burn"),
                    "That card is not upgradeable.",
                )
                if upgrade_card is not None:
                    self.player.deck[upgrade_card].upgrade()
                break
            if action == "lift":
                if self.player.girya_charges > 0:
                    ei.apply_effect(self.player, "Strength", 1)
                    self.player.girya_charges -= 1
                    if self.player.girya_charges == 0:
                        ansiprint("<bold>Girya</bold> is depleted")
                    break
                ansiprint("You cannot use <bold>Girya</bold> anymore")
                sleep(1.5)
                view.clear()
                continue
            if action == "toke":
                option = view.list_input(
                    "What card would you like to remove? > ",
                    self.player.deck,
                    view.view_piles,
                    lambda card: card.get("Removable") is False,
                    "That card is not removable.",
                )
                self.player.deck[option] = self.player.card_actions(self.player.deck[option], "Remove", card_catalog.create_all_cards())
                break
            if action == "dig":
                gen.claim_relics(False, self.player, 1, relic_catalog.create_all_relics(), None, False)
                break
        while True:
            ansiprint("<bold>[View Deck]</bold> or <bold>[Leave]</bold>")
            option = input("> ").lower()
            if option == "view deck":
                view.view_piles(self.player.deck)
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
