'''
An example using a message bus to isolate combat logic.

So instead of something like:
    if relics['Strike Dummy'] in self.relics and 'strike' in card.get('Name').lower():
        ...
    if self.debuffs["Weak"] > 0 and card:
        ...
    if target.debuffs["Vulnerable"] > 0:
        ...
    if self.buffs["Vigor"] > 0:
        ...

We can emit messages during different parts of combat, and have players/buffs/debuffs/relics respond and
modify game state.

This example shows a very simple combat with 2 identical attacks across 2 turns (1 each).
The damage is calculated and modified by buffs/debuffs/relics.
I'm simplifying/ignoring a lot of things here (no energy, blocking, discard pile, etc...) to keep it short.

The most important thing to notice is that all the buffs/debuffs/relics logic is completely isolated. To add
a new buff to this combat, none of the combat or player logic would need to change. You would just code the buff
to respond to certain messages, add it to the player's list of buffs, and it would automatically be called during
the correct phases of combat. This also allows for independent testing of buffs/debuffs/relics -- you can stand
up a test where you send it certain messages and verify that it modifies the game state correctly.

Apologies for the long example. Hopefully it makes sense.
'''
from dataclasses import dataclass
from enum import StrEnum
from ansi_tags import am, ansiprint
from uuid import uuid4
import math

class Message(StrEnum):
    '''These represent the types of messages that can be sent to the message bus.'''
    START_OF_COMBAT = 'start_of_combat'
    START_OF_TURN = 'start_of_turn'
    END_OF_TURN = 'end_of_turn'
    BEFORE_ATTACK = 'before_attack'
    AFTER_ATTACK = 'after_attack'

class MessageBus():
  '''This is a Pub/Sub, or Publish/Subscribe, message bus. It allows components to subscribe to messages,
  registering a callback function that will be called when that message is published.
  '''
  def __init__(self, debug=True):
    self.subscribers = dict(dict())
    self.debug = debug

  def subscribe(self, event_type: Message, callback, uid):
    if event_type not in self.subscribers:
      self.subscribers[event_type] = dict()
    self.subscribers[event_type][uid] = callback
    if self.debug:
      ansiprint(f"<basic>MESSAGEBUS</basic>: <blue>{event_type}</blue> | Subscribed <bold>{callback.__qualname__}</bold>")

  def publish(self, event_type: Message, data):
    if event_type in self.subscribers:
      for uid, callback in self.subscribers[event_type].items():
        if self.debug:
          ansiprint(f"<basic>MESSAGEBUS</basic>: <blue>{event_type}</blue> | Calling <bold>{callback.__qualname__}</bold>")
        callback(event_type, data)
    return data

class Registerable():
    '''A mixin so I don't have to repeat the register function in every class that needs it.'''
    registers = []
    def register(self, bus):
        for message in self.registers:
            bus.subscribe(message, self.callback, self.uid)

class Character(Registerable):
    '''This is both the Player and the Enemy. Note that it is also subscribed to the message bus so that it can
    take actions at the end of each turn. This keeps that logic out of the Combat class.'''
    registers = [Message.END_OF_TURN]

    def __init__(self, name, cards, buffs, debuffs, relics, bus) -> None:
        self.name = name
        self.health = 100
        self.cards = cards
        self.buffs = buffs
        self.debuffs = debuffs
        self.relics = relics
        self.bus = bus
        self.uid = uuid4()
        [x.register(self.bus) for x in self.buffs + self.debuffs + self.relics]
        self.register(self.bus)

    def pretty_string(self):
       buffs_pretty = [buff.pretty_string() for buff in self.buffs]
       debuffs_pretty = [debuff.pretty_string() for debuff in self.debuffs]
       relics_pretty = [relic.pretty_string() for relic in self.relics]
       return f"{self.name:7}: {self.health:3}hp | <blue>Buffs</blue>: {buffs_pretty} | <green>Debuffs</green>: {debuffs_pretty} | <basic>Relics</basic>: {relics_pretty}"

    def take_damage(self, damage, reasons):
        self.health -= damage
        ansiprint(f"<red>{self.name}</red> took <red>{damage}</red> damage from {reasons}")

    def callback(self, message, context):
        if message == Message.END_OF_TURN:
            removing = [buff for buff in self.buffs if buff.duration <= 0] + [debuff for debuff in self.debuffs if debuff.duration <= 0]
            for modifier in removing:
                ansiprint(f"<red>{self.name}</red>: <bold>{modifier.name}</bold> wore off.")
            self.buffs = [buff for buff in self.buffs if buff.duration > 0]
            self.debuffs = [debuff for debuff in self.debuffs if debuff.duration > 0]

class StrikeCard():
    '''A basic attack card. It allows you to modify the damage it deals, and keeps track of what is modifying it.'''
    def __init__(self) -> None:
        self.name = 'Strike'
        self.base_damage = 6
        self.damage = self.base_damage
        self.damage_affected_by = [f"Strike({self.base_damage:+d} dmg)"]

    def modify_damage(self, change, reason):
        self.damage += change
        self.damage_affected_by.append(f"{reason}({change:+d} dmg)")

    def apply(self, target):
        target.take_damage(self.damage, " | ".join(self.damage_affected_by))

class Modifiers(Registerable):
    '''The base class for all buffs/debuffs/relics. It provides a uid and pretty string'''
    def __init__(self) -> None:
        self.name = "default"
        self.uid = uuid4()

    def pretty_string(self):
       return f"{self.name}"


class Buff_Strength(Modifiers):
    registers = [Message.BEFORE_ATTACK, Message.END_OF_TURN]

    def __init__(self, duration) -> None:
        super().__init__()
        self.name = "Strength"
        self.info = 'Increases damage of attacks.'
        self.duration = duration
        self.amount = 2

    def callback(self, message, context):
        if message == Message.END_OF_TURN:
            self.duration -= 1
        if message == Message.BEFORE_ATTACK and self.duration > 0:
            origin, target, card = context
            dmg_affected_by = "<buff>Strength</buff>"
            card.modify_damage(self.amount, reason=dmg_affected_by)

class Debuff_Vulnerable(Modifiers):
    registers = [Message.BEFORE_ATTACK, Message.END_OF_TURN]

    def __init__(self, duration) -> None:
        super().__init__()
        self.name = "Vulnerable"
        self.duration = duration
        self.info = 'You/It takes 50%% more damage from attacks.'

    def callback(self, message, context):
        if message == Message.END_OF_TURN:
            self.duration -= 1
        if message == Message.BEFORE_ATTACK and self.duration > 0:
            origin, target, card = context
            if self in target.debuffs:
                dmg_affected_by = "<debuff>Vulnerable</debuff>"
                card.modify_damage(math.floor(card.damage * 0.50), reason=dmg_affected_by)

class Relic_Akabeko(Modifiers):
    registers = [Message.START_OF_COMBAT, Message.BEFORE_ATTACK, Message.AFTER_ATTACK]

    def __init__(self) -> None:
        super().__init__()
        self.name = "Akabeko"
        self.first_attack = False
        self.amount = 8
        self.info = f'Your first <keyword>Attack</keyword> each combat deals {self.amount} additional damage.'

    def pretty_string(self):
       return f"{self.name}"

    def callback(self, message, context):
      if message == Message.START_OF_COMBAT:
        self.first_attack = True
      if message == Message.BEFORE_ATTACK and self.first_attack:
          origin, target, card = context
          dmg_affected_by = "<buff>Akabeko</buff>"
          card.modify_damage(self.amount, reason=dmg_affected_by)
      if message == Message.AFTER_ATTACK:
        self.first_attack = False

@dataclass
class Combat():
    player: Character
    enemy: Character
    bus: MessageBus
    turn: int = 1

    def demo(self):
        self.show_everything()
        self.bus.publish(Message.START_OF_COMBAT, self)
        self.bus.publish(Message.START_OF_TURN, self)
        self.play_card(origin=self.player, target=self.enemy, card=self.player.cards[0])
        self.bus.publish(Message.END_OF_TURN, self)
        self.turn += 1
        self.show_everything()
        self.bus.publish(Message.START_OF_TURN, self)
        self.play_card(origin=self.player, target=self.enemy, card=self.player.cards[1])
        self.show_everything()

    def play_card(self, origin, target, card):
        # Emit a message that a card is about to be played
        self.bus.publish(Message.BEFORE_ATTACK, (origin, target, card))
        card.apply(target)
        self.bus.publish(Message.AFTER_ATTACK, (origin, target, card))

    def show_everything(self):
       ansiprint(f"\n<bold>Turn {self.turn}</bold>")
       ansiprint(self.player.pretty_string())
       ansiprint(self.enemy.pretty_string())
       print()

def main():
  # Create the universe
  bus = MessageBus(debug=False)   # Switch debug to True to see all the messages being sent
  card1 = StrikeCard()
  card2 = StrikeCard()
  strength = Buff_Strength(duration=1)        # Change the duration to see it expire or not
  vulnerable = Debuff_Vulnerable(duration=2)  # Change the duration to see it expire or not
  akabeko = Relic_Akabeko()
  player = Character(name="Player", cards=[card1, card2], buffs=[strength], debuffs=[], relics=[akabeko], bus=bus)
  enemy = Character(name="Enemy", cards=[], buffs=[], debuffs=[vulnerable], relics=[], bus=bus)
  game = Combat(player=player, enemy=enemy, bus=bus)

  # This is the demo
  game.demo()

if __name__ == "__main__":
    main()