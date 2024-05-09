from enum import StrEnum

from ansi_tags import ansiprint


class Message(StrEnum):
    # These are just some basic events to start off with. I will add more as I go along.
    START_OF_COMBAT = 'start_of_combat'
    END_OF_COMBAT = 'end_of_combat'
    START_OF_TURN = 'start_of_turn'
    END_OF_TURN = 'end_of_turn'
    ON_CARD_PLAY = 'on_card_play'
    ON_RELIC_ADD = 'on_relic_add'
    ON_PLAYER_HURT = 'on_player_hurt'

class MessageBus:
    '''
    This is a Pub/Sub, or Publish/Subscribe, message bus. It allows components to subscribe to messages,
    registering a callback function that will be called when that message is published.
    '''
    def __init__(self, debug=True):
        self.subscribers = dict(dict())  # noqa: C408
        self.debug = debug

    def subscribe(self, event_type: Message, callback, uid):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = {}
        self.subscribers[event_type][uid] = callback
        if self.debug:
            ansiprint(f"<basic>MESSAGEBUS</basic>: <blue>{event_type}</blue> | Subscribed <bold>{callback.__qualname__}</bold>")

    def unsubscribe(self, event_type, uid):
        if self.debug:
            ansiprint(f"<basic>MESSAGEBUS</basic>: Unsubscribed <bold>{self.subscribers[event_type][uid].__qualname__}</bold> from {', '.join(event_type).rstrip(', ')}")
        del self.subscribers[event_type][uid]

    def publish(self, event_type: Message, data):
        if event_type in self.subscribers:
            for _uid, callback in self.subscribers[event_type].items():
                if self.debug:
                    ansiprint(f"<basic>MESSAGEBUS</basic>: <blue>{event_type}</blue> | Calling <bold>{callback.__qualname__}</bold>")
                callback(event_type, data)
        return data

class Registerable():
    '''Convenience class so I don't have to repeat the register function in every class that needs it.'''
    registers = []
    def register(self):
        for message in self.registers:
            bus.subscribe(message, self.callback, self.uid)

    def unregister(self, event_types: list[Message]=None):
        event_types = event_types if event_types else []
        for message in self.registers:
            bus.unsubscribe(message, self.uid)

bus = MessageBus(debug=True)
