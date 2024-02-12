from pprint import pprint

import pytest

from message_bus_tools import Message, MessageBus


@pytest.mark.only
def test_message_bus():
  bus = MessageBus(debug=True)
  assert bus.subscribers == {}

  def callbackA(event_type, data):
    print(f"A: Got called with {event_type} and {data}")

  def callbackB(event_type, data):
    print(f"B: Got called with {event_type} and {data}")

  # Subscribe to the same message with different uids
  bus.subscribe(Message.START_OF_COMBAT, callbackA, 111)
  bus.subscribe(Message.START_OF_COMBAT, callbackB, 222)

  # Subscribe to the same message with the same uid
  bus.subscribe(Message.BEFORE_ATTACK, callbackA, 111)
  bus.subscribe(Message.BEFORE_ATTACK, callbackB, 111)  # this will overwrite the previous callbackA

  pprint(bus.subscribers)

  # 2 callbacks
  bus.publish(Message.START_OF_COMBAT, "data")

  # 1 callback
  bus.publish(Message.BEFORE_ATTACK, "data")

  # Unsubscribe
  bus.unsubscribe(Message.BEFORE_ATTACK, 111)

  # No callback
  bus.publish(Message.BEFORE_ATTACK, "data")

