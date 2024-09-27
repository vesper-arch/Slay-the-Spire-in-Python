from copy import deepcopy
from enum import StrEnum
from uuid import uuid4

from ansi_tags import ansiprint
from definitions import CardType, PlayerClass, Rarity, StackType, TargetType, STACK_TYPE_COLOR_MAPPING


class Message(StrEnum):
    '''Messages that can be sent to the message bus.'''
    START_OF_COMBAT = 'start_of_combat'
    END_OF_COMBAT = 'end_of_combat'
    START_OF_TURN = 'start_of_turn'
    END_OF_TURN = 'end_of_turn'
    BEFORE_ATTACK = 'before_attack'
    AFTER_ATTACK = 'after_attack'
    BEFORE_BLOCK = 'before_block'
    AFTER_BLOCK = 'after_block'
    WHEN_ENTERING_CAMPFIRE = 'when_entering_campfire'
    ON_PLAYER_HEALTH_LOSS = 'on_player_health_loss'
    ON_ATTACKED = 'on_attacked'
    ON_PICKUP = 'on_pickup' # For relics
    ON_DRAW = 'on_draw'
    ON_EXHAUST = 'on_exhaust'
    ON_CARD_PLAY = 'on_card_play'
    ON_CARD_ADD = 'on_card_add'
    ON_RELIC_ADD = 'on_relic_add'
    ON_DEATH_OR_ESCAPE = 'on_death_or_escape'
    BEFORE_PLAYER_DEATH = 'before_player_death'
    BEFORE_DRAW = 'before_draw'
    AFTER_DRAW = 'after_draw'
    BEFORE_APPLY_EFFECT = 'before_apply'
    AFTER_APPLY_EFFECT = 'after_apply'
    BEFORE_SET_INTENT = 'before_intent'
    AFTER_SET_INTENT = 'after_intent'

class MessageBus():
    '''This is a Pub/Sub, or Publish/Subscribe, message bus. It allows components to subscribe to messages,
    registering a callback function that will be called when that message is published.
    '''
    def __init__(self, debug=True):
        self.subscribers = dict(dict())  # noqa: C408
        self.debug = debug
        self.death_messages = []  # what is this?
        self.unsubscribe_set = set()
        self.subscribe_set = set()
        self.lock_count = 0

    def _clear_subscribes(self):
        if self.lock_count > 0:
            return
        for event_type, callback, uid in self.subscribe_set:
            self.subscribe(event_type, callback, uid)
        self.subscribe_set.clear()

    def subscribe(self, event_type: Message, callback, uid):
        if self.lock_count > 0:
            if self.debug:
                ansiprint(f"<basic>MESSAGEBUS</basic>: <blue>{event_type}</blue> | Locked. Adding <bold>{callback.__qualname__}</bold> to subscribe list.")
            self.subscribe_set.add((event_type, callback, uid))
        else:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = {}
            self.subscribers[event_type][uid] = callback
            if self.debug:
                ansiprint(f"<basic>MESSAGEBUS</basic>: <blue>{event_type}</blue> | Subscribed <bold>{callback.__qualname__}</bold>")

    def _clear_unsubscribes(self):
        if self.lock_count > 0:
            return
        for event_type, uid in self.unsubscribe_set:
            if self.debug:
                ansiprint(f"<basic>MESSAGEBUS</basic>: Unsubscribing <bold>{self.subscribers[event_type][uid].__qualname__}</bold> from {', '.join(event_type).replace(', ', '')}")
            self.unsubscribe(event_type, uid)
        self.unsubscribe_set.clear()

    def unsubscribe(self, event_type, uid):
        if self.lock_count > 0:
            if self.debug:
                ansiprint(f"<basic>MESSAGEBUS</basic>: Locked. Adding <bold>{event_type} - {uid}</bold> to unsubscribe list.")
            self.unsubscribe_set.add((event_type, uid))
        else:
            if uid in self.subscribers[event_type]:
                if self.debug:
                    ansiprint(f"<basic>MESSAGEBUS</basic>: Unsubscribed <bold>{self.subscribers[event_type][uid].__qualname__}</bold> from {', '.join(event_type).replace(', ', '')}")
                del self.subscribers[event_type][uid]

    def publish(self, event_type: Message, data):
        self.lock_count += 1
        if event_type in self.subscribers:
            for uid, callback in self.subscribers[event_type].items():
                _ = uid
                if self.debug:
                    ansiprint(f"<basic>MESSAGEBUS</basic>: <blue>{event_type}</blue> | Calling <bold>{callback.__qualname__}</bold>")
                callback(event_type, data)
        self.lock_count -= 1
        self._clear_subscribes()
        self._clear_unsubscribes()
        return data

class Registerable():
    registers = []

    def register(self, bus):
        for message in self.registers:
            bus.subscribe(message, self.callback, self.uid)
        self.subscribed = True

    def unsubscribe(self, event_types: list[Message]=None):
        '''Unsubscribes the object from certain events. Unsubscribes from all registers by default.'''
        if not event_types:
            event_types = self.registers
        for message in event_types:
            bus.unsubscribe(message, self.uid)
        self.subscribed = False


class Relic(Registerable):
    def __init__(self, name: str, info: str, flavor_text: str, rarity: Rarity, player_class: PlayerClass=PlayerClass.ANY):
        self.uid = uuid4()
        self.subscribed = False
        self.name = name
        self.info = info
        self.flavor_text = flavor_text
        self.rarity = rarity
        self.player_class = player_class

    def __eq__(self, other: object) -> bool:
        '''This is a custom __eq__ method that allows for comparison of relics by name, class, or object.'''
        if type(other) is type(self):
            original = self.__dict__ == other.__dict__
        else:
            original = False
        by_string = isinstance(other, str) and other == self.name
        by_class = other == type(self) and other.__name__ == self.__class__.__name__
        return original or by_string or by_class

    def pretty_print(self):
        rarity_color = self.rarity.lower()
        return f"<{rarity_color}>{self.name}</{rarity_color}> | <yellow>{self.info}</yellow> | <italic><dark-blue>{self.flavor_text}</dark-blue></italic>"

class Potion(Registerable):
    def __init__(self, name: str, info: str, rarity: Rarity, target: TargetType, player_class: PlayerClass=PlayerClass.ANY):
        self.name = name
        self.subscribed = False
        self.info = info
        self.rarity = rarity
        self.target = target
        self.player_class = player_class
        self.playable = True
        self.golden_stats = [] # This is a list of the attributes that will be doubled when Golden Bark is collected.
        self.golden_info = ""

    def pretty_print(self):
        rarity_color = self.rarity.lower()
        color_map = {"Ironclad": "red", "Silent": "dark-green", "Defect": "true-blue", "Watcher": "watcher-purple", "Any": "white"}
        class_color = color_map[self.player_class]
        return f"""<{rarity_color}>{self.name}</{rarity_color}> | <yellow>{self.info}</yellow>{f" | <{class_color}>{self.player_class}</{class_color}>" if self.player_class != PlayerClass.ANY else ""}"""

    def callback(self, message, data):
        if message == Message.ON_RELIC_ADD:
            _, relic = data
            if relic.name == "Golden Bark":
                self.info = self.golden_info
                for stat in self.golden_stats:
                    stat *= 2

bus = MessageBus(debug=False)
