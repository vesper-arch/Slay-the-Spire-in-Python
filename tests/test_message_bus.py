from unittest.mock import MagicMock
import pytest
from message_bus_tools import Message, MessageBus


class TestMessageBus:
  def test_bus_inits_with_no_subscribers(self):
    bus = MessageBus(debug=True)
    assert len(bus.subscribers) == 0

  def test_bus_can_subscribe_and_be_called_once(self):
    bus = MessageBus(debug=True)
    callback = MagicMock(__qualname__="callback")

    # Subscribe to the same message with different uids
    bus.subscribe(Message.START_OF_COMBAT, callback, 1)
    bus.publish(Message.START_OF_COMBAT, "data")

    callback.assert_called_once_with(Message.START_OF_COMBAT, "data")

  def test_bus_can_subscribe_two_callbacks_and_both_receive(self):
    bus = MessageBus(debug=True)
    callbackA = MagicMock(__qualname__="callbackA")
    callbackB = MagicMock(__qualname__="callbackB")

    # Subscribe to the same message with different uids
    bus.subscribe(Message.START_OF_COMBAT, callbackA, 111)
    bus.subscribe(Message.START_OF_COMBAT, callbackB, 222)

    # 2 callbacks
    bus.publish(Message.START_OF_COMBAT, "data")

    callbackA.assert_called_once_with(Message.START_OF_COMBAT, "data")
    callbackB.assert_called_once_with(Message.START_OF_COMBAT, "data")

  def test_bus_can_subscribe_and_unsubscribe(self):
    bus = MessageBus(debug=True)
    callback = MagicMock(__qualname__="callback")

    bus.subscribe(Message.START_OF_COMBAT, callback, 1)
    bus.publish(Message.START_OF_COMBAT, "should receive")
    callback.assert_called_once_with(Message.START_OF_COMBAT, "should receive")

    bus.unsubscribe(Message.START_OF_COMBAT, 1)
    bus.publish(Message.START_OF_COMBAT, "should not receive")
    callback.assert_called_once_with(Message.START_OF_COMBAT, "should receive")

  def test_bus_can_unsubscribe_twice(self):
    bus = MessageBus(debug=True)
    callback = MagicMock(__qualname__="callback")

    bus.subscribe(Message.START_OF_COMBAT, callback, 1)
    bus.publish(Message.START_OF_COMBAT, "should receive")
    callback.assert_called_once_with(Message.START_OF_COMBAT, "should receive")

    bus.unsubscribe(Message.START_OF_COMBAT, 1)
    bus.publish(Message.START_OF_COMBAT, "should not receive")
    callback.assert_called_once_with(Message.START_OF_COMBAT, "should receive")

    bus.unsubscribe(Message.START_OF_COMBAT, 1)
    bus.publish(Message.START_OF_COMBAT, "should not receive")
    callback.assert_called_once_with(Message.START_OF_COMBAT, "should receive")

  def test_bus_can_subscribe_twice_with_same_uid_and_second_one_overwrites_first(self):
      bus = MessageBus(debug=True)
      callbackA = MagicMock(__qualname__="callbackA")
      callbackB = MagicMock(__qualname__="callbackB")

      # Subscribe to the same message with same uid
      bus.subscribe(Message.BEFORE_ATTACK, callbackA, 111)
      bus.subscribe(Message.BEFORE_ATTACK, callbackB, 111)  # this should overwrite the previous callbackA

      # 1 callback
      bus.publish(Message.BEFORE_ATTACK, "data")

      callbackA.assert_not_called()
      callbackB.assert_called_once_with(Message.BEFORE_ATTACK, "data")

  def test_callback_with_complex_data(self):
      # A test to see if the callback can handle complex data.
      # In this test, the callback will call a provided function with modified data.
      # This is a complex pattern but allows deocoupling of the receiver from knowing about the sender's details
      bus = MessageBus(debug=True)
      def callbackA(_, data):
          value = data["value"] + 5
          data["function"](value)
      callbackB = MagicMock(__qualname__="callback")

      data = {
          "value": 5,
          "function": callbackB
      }
      bus.subscribe(Message.START_OF_COMBAT, callbackA, 1)
      bus.publish(Message.START_OF_COMBAT, data)

      callbackB.assert_called_once_with(10)

  def test_can_subscribe_during_publish(self):
      bus = MessageBus(debug=True)
      def side_effect(*args, **kwargs):
        bus.subscribe(Message.BEFORE_ATTACK, callbackB, 2)
      callbackA = MagicMock(__qualname__="callbackA", side_effect=side_effect)
      callbackB = MagicMock(__qualname__="callbackB")

      bus.subscribe(Message.BEFORE_ATTACK, callbackA, 1)

      bus.publish(Message.BEFORE_ATTACK, "data")

      callbackA.assert_called_once_with(Message.BEFORE_ATTACK, "data")
      callbackB.assert_not_called()

      bus.publish(Message.BEFORE_ATTACK, "second time")

      assert callbackA.call_count == 2, "Callback A should have been called twice"
      callbackB.assert_called_once_with(Message.BEFORE_ATTACK, "second time") 


  def test_can_unsubscribe_during_publish(self):
      bus = MessageBus(debug=True)
      def side_effect(*args, **kwargs):
        bus.unsubscribe(Message.BEFORE_ATTACK, 1)
      callbackA = MagicMock(__qualname__="callbackA", side_effect=side_effect)
      callbackB = MagicMock(__qualname__="callbackB")

      bus.subscribe(Message.BEFORE_ATTACK, callbackA, 1)
      bus.subscribe(Message.BEFORE_ATTACK, callbackB, 2)

      bus.publish(Message.BEFORE_ATTACK, "data")

      callbackA.assert_called_once_with(Message.BEFORE_ATTACK, "data")
      callbackB.assert_called_once_with(Message.BEFORE_ATTACK, "data")

      bus.publish(Message.BEFORE_ATTACK, "data")

      callbackA.assert_called_once_with(Message.BEFORE_ATTACK, "data")
      assert callbackB.call_count == 2, "Callback B should have been called twice"
     
  def test_can_unsubscribe_during_nested_publish(self):
      # What happens when you try to unsubscribe from a nested publish?
      bus = MessageBus(debug=True)
      def side_effect_A(*args, **kwargs):
        print("A called.")
        bus.publish(Message.AFTER_ATTACK, "calls B")
        bus.unsubscribe(Message.BEFORE_ATTACK, 1)
      callbackA = MagicMock(__qualname__="callbackA", side_effect=side_effect_A)
      
      def side_effect_B(*args, **kwargs):
        print("B called.")  
        bus.unsubscribe(Message.AFTER_ATTACK, 2)
      callbackB = MagicMock(__qualname__="callbackB", side_effect=side_effect_B)

      bus.subscribe(Message.BEFORE_ATTACK, callbackA, 1)
      bus.subscribe(Message.AFTER_ATTACK, callbackB, 2)

      bus.publish(Message.BEFORE_ATTACK, "calls A")

      callbackA.assert_called_once_with(Message.BEFORE_ATTACK, "calls A")
      callbackB.assert_called_once_with(Message.AFTER_ATTACK, "calls B")

      bus.publish(Message.BEFORE_ATTACK, "data")

      # No additional calls should be made (i.e. unsubscribe was successful)
      callbackA.assert_called_once() 
      callbackB.assert_called_once()