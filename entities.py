
from ansi_tags import ansiprint


class Damage:
    def __init__(self, dmg: int):
        self.damage = dmg
    def modify_damage(self, change: int, context: str, *args, **kwargs):
        new_dmg = self.damage + change
        ansiprint(f"Damage modified from {self.damage} --> {new_dmg} by {context}.")
        self.damage = new_dmg
    def set_damage(self, new_dmg: int, context: str, *args, **kwargs):
        ansiprint(f"Damage modified from {self.damage} --> {new_dmg} by {context}.")
        self.damage = new_dmg


class Action:
    def __init__(self, name, action, amount):
        self.name = name
        self.action = action
        self.amount = amount
        self.executed = False
        self.cancelled = False
        self.reason = ""

    def cancel(self, reason=None):
        self.cancelled = True
        if not reason:
            reason = f"{self.name} was cancelled."
        self.reason = reason

    def set_amount(self, new_amount):
        self.amount = new_amount

    def modify_amount(self, change):
        self.amount += change

    def execute(self):
        if self.executed:
            print(f"{self.name} already executed.")
            return
        if self.cancelled:
            ansiprint(self.reason)
            return
        self.action(self.amount)
        self.executed = True

    def __str__(self):
        return f"Action: {self.name} | Amount: {self.amount}"

    def __repr__(self):
        return self.__str__()

