import math
import random
from copy import deepcopy
from time import sleep
from uuid import uuid4

import displayer as view
import effect_interface as ei
from ansi_tags import ansiprint
from definitions import State
from entities import Damage
from message_bus_tools import Message, Registerable, bus
from card_catalog import Card
from player import Player
from effect_catalog import Effect



class Action():
    '''A single action that an enemy takes'''
    def __init__(self, action_type, ) -> None:
        pass

    def execute(self):
        pass

class Enemy(Registerable):
    registers = [Message.START_OF_TURN, Message.END_OF_TURN, Message.ON_DEATH_OR_ESCAPE]
    player = None

    def __init__(self, health_range: list, block: int, name: str, powers: list[Effect] | None = None):
        self.uid = uuid4()
        if not powers:
            powers = []
        actual_health = random.randint(health_range[0], health_range[1])
        self.health = actual_health
        self.max_health = actual_health
        self.block = block
        self.name = name
        self.third_person_ref = (
            f"{self.name}'s"  # Python f-strings suck so I have to use this
        )
        self.past_moves = ["place"] * 3
        self.intent: str = ""
        self.next_move: list[tuple[str, str, tuple] | tuple[str, tuple]] = ""
        self.state = State.ALIVE
        self.buffs = powers
        self.debuffs = []
        self.stolen_gold = 0
        self.awake_turns = 0
        self.mode = ""
        self.flames = -1
        self.upgrade_burn = False
        self.active_turns = 1

    def __str__(self):
        return "Enemy"

    def __repr__(self):
        status = f"{self.name} (<red>{self.health} </red>/ <red>{self.max_health}</red> | <light-blue>{self.block} Block</light-blue>)"
        for effect in self.buffs + self.debuffs:
            status += " | " + effect.get_name()
        if self.flames > 0:
            status += f" | <yellow>{self.flames} Flames</yellow>"
        status += " | Intent: " + self.intent.replace('Σ', '')
        return status

    def set_intent(self):
        pass

    def execute_move(self, player: Player, enemies: list["Enemy"]):
        moves = 1
        display_name = "DEFAULT: UNKNOWN"
        for action in self.next_move:
            if moves == 1 and len(action) > 2:
                display_name, action, parameters = action
            else:
                action, parameters = action
            if action not in ("Attack", "Buff", "Debuff", "Remove Effect", "Status", "Block"):
                self.misc_move(enemies)
                sleep(1)
                view.clear()
                return
            ansiprint(f"<bold>{display_name}</bold>\n" if moves == 1 else "", end="")
            sleep(0.6)
            if action == "Attack":
                dmg = parameters[0]
                times = parameters[1] if len(parameters) > 1 else 1
                self.attack(dmg, times, target=player)
            elif action == "Buff":
                buff = parameters[0]
                amount = parameters[1] if len(parameters) > 1 else 1
                target = parameters[2] if len(parameters) > 2 else self
                ei.apply_effect(self, self, buff, amount)
            elif action == "Debuff":
                debuff = parameters[0]
                amount = parameters[1] if len(parameters) > 1 else 1
                target = parameters[2] if len(parameters) > 2 else player
                ei.apply_effect(target, self, debuff, amount)
            elif action == "Remove Effect":
                effect_name = parameters[0]
                effect_type = parameters[1]
                self.remove_effect(effect_name, effect_type)
            elif action == "Status":
                assert (len(parameters) >= 3), f"Status action requires 3 parameters: given {parameters}"
                status = parameters[0]
                amount = parameters[1]
                location = parameters[2].lower()
                self.status(status, amount, location, player=player)
            elif action == "Block":
                block = parameters[0]
                target = parameters[1] if len(parameters) > 1 else None
                self.blocking(block, target)
            sleep(0.2)
            moves += 1
        if display_name == "Inferno" and self.flames > -1:
            self.upgrade_burn = True
            self.flames = 0
        sleep(0.5)
        self.past_moves.append(display_name)
        self.active_turns += 1
        if self.flames > -1:
            self.flames += 1

    def misc_move(self, enemies):
        if len(self.next_move[0]) > 2:
            name, func_name, parameters = self.next_move[0]
        else:
            name, func_name = self.next_move[0]
        ansiprint(f"<bold>{name}</bold>")
        sleep(0.6)
        if func_name == "Cowardly":
            ansiprint("<italic>Hehe. Thanks for the money.<italic>")
            self.state = State.ESCAPED
            ansiprint(f"<italic><red>{self.name} has escaped</red></italic>")
        elif func_name == "Sleeping":
            sleeptalk = parameters[0]
            ansiprint(f"<italic>{sleeptalk}</italic>")
        elif func_name == "Stunned":
            ansiprint("<italic>Stunned!</italic>")
        elif func_name == "Summon":
            enemies = tuple(parameters[0])
            amount = int(parameters[1]) if len(parameters) > 1 else 1
            choice = bool(parameters[2]) if len(parameters) > 2 else False
            self.summon(enemies, amount, choice)
        elif func_name == "Explode":
            pass
        elif func_name == "Rebirth":
            for debuff in self.debuffs:
                if debuff not in ei.NON_STACKING_EFFECTS:
                    self.debuffs[debuff] = 0
                else:
                    self.debuffs[debuff] = False
            self.buffs["Curiosity"] = False
            self.buffs["Unawakened"] = False
        elif func_name == "Revive":
            self.health = math.floor(self.health * 0.5)
            ansiprint(f"<bold>{self.name}</bold> revived!")
        elif func_name == "Charging":
            message = parameters[0]
            ansiprint(f"{message}")
        elif func_name == "Split":
            split_into = {
                "Slime Boss": (
                    Enemy(self.health, 0, "Acid Slime(L)"),
                    Enemy(self.health, 0, "Spike Slime (L)"),
                ),
                "Acid Slime (L)": (
                    Enemy(self.health, 0, "Acid Slime(M)"),
                    Enemy(self.health, 0, "Acid Slime(M)"),
                ),
                "Spike Slime (L)": (
                    Enemy(self.health, 0, "Spike Slime (M)"),
                    Enemy(self.health, 0, "Spike Slime (M)"),
                ),
            }
            for _ in range(2):
                enemies.append(split_into[self.name])
            ansiprint(f"{self.name} split into 2 {split_into[self.name].name}s")
        self.active_turns += 1

    def die(self):
        """
        Dies.
        """
        print(f"{self.name} has died.")
        self.state = State.DEAD
        for effect in self.buffs + self.debuffs:
            effect.unsubscribe()
        bus.publish(Message.ON_DEATH_OR_ESCAPE, (self))

    def debuff_and_buff_check(self):
        """
        Not finished
        """

    def move_spam_check(self, target_move, max_count) -> bool:
        """Returns False if the move occurs [max_count] times in a row. Otherwise returns True"""
        enough_moves = len(self.past_moves) >= max_count
        return not(enough_moves and all(move == target_move for move in self.past_moves[-max_count:]))

    def attack(self, dmg: int, times: int, target: Player):
        for _ in range(times):
            if target.state == State.DEAD:
                ansiprint(f"{self.name} stopped attacking: {target.name} is already dead.")
                return
            modifiable_dmg = Damage(dmg)
            bus.publish(Message.BEFORE_ATTACK, (self, target, modifiable_dmg))  # allows for damage modification from relics/effects
            dmg = modifiable_dmg.damage
            if dmg <= target.block:
                target.block -= dmg
                dmg = 0
                ansiprint("<light-blue>Blocked</light-blue>")
            elif dmg > target.block:
                dmg -= target.block
                dmg = max(0, dmg)
                ansiprint(f"{self.name} dealt {dmg}(<light-blue>{target.block} Blocked</light-blue>) damage to you.")
                target.block = 0
                target.health -= dmg
                bus.publish(Message.ON_PLAYER_HEALTH_LOSS, None)
            if target.health <= 0:
                target.die()
            bus.publish(Message.AFTER_ATTACK, (self, target, dmg))
        sleep(1)

    def remove_effect(self, effect_name, effect_type):
        if effect_name not in ei.ALL_EFFECTS:
            raise ValueError(f"{effect_name} is not a member of any debuff or buff list.")
        effect_types = {"Buffs": self.buffs, "Debuffs": self.debuffs}
        if effect_name not in ei.NON_STACKING_EFFECTS:
            effect_types[effect_type][effect_name] = 0
        else:
            effect_types[effect_type][effect_name] = False

    def blocking(self, block: int, target: "Enemy" = None, context: str=None):
        if not target:
            target = self
        target.block += block
        if context:
            ansiprint(f"{target.name} gained {block} <blue>Block</blue> from {context}")
        else:
            ansiprint(f"{target.name} gained {block} <blue>Block</blue>")
        sleep(1)

    def status(self, status_card: Card, amount: int, location: str, player: Player):
        locations = {
            "draw pile": player.draw_pile,
            "discard pile": player.discard_pile,
            "hand": player.hand,
        }
        pile = locations[location]
        status_card = status_card()
        for _ in range(amount):
            upper_bound = len(location) - 1 if len(location) > 0 else 1
            insert_index = random.randint(0, upper_bound)
            pile.insert(insert_index, deepcopy(status_card))
        ansiprint(f"{player.name} gained {amount} {status_card.name} \nPlaced into {location}")
        sleep(1)

    def summon(self, enemy, amount: int, random_enemy: bool, enemies):
        if len(enemy) == 1:
            enemy = enemy[0]
        for _ in range(amount):
            chosen_enemy = random.choice(enemy) if random_enemy else enemy
            enemies.append(chosen_enemy)
            ansiprint(f"<bold>{chosen_enemy.name}</bold> summoned!")

    def start_turn(self):
        ansiprint(f"{self.name}'s current state: {self.state}")
        if self.state == State.ALIVE:
            for effect in self.buffs + self.debuffs:
                if effect.subscribed is False:
                    effect.register(bus)
            ansiprint(f"<underline><bold>{self.name}</bold></underline>:")
            if "Block" not in self.intent:  # Checks the last move(its intent hasn't been updated yet) used to see if the enemy Blocked last turn
                self.block = 0
            ei.tick_effects(self)
            print()
            self.set_intent()

    def take_turn(self, player: Player, enemies: list["Enemy"]):
        if self.state == State.ALIVE:
            self.execute_move(player, enemies)

    def callback(self, message, data):
        global bus
        if message == Message.START_OF_TURN:
            self.start_turn()
        elif message == Message.END_OF_TURN:
            player, enemies = data
            self.take_turn(player, enemies)
        elif message == Message.ON_DEATH_OR_ESCAPE:
            # This is meant to react to OTHER entities dying, not itself
            dead_entity = data
            if dead_entity != self:
                ansiprint(f"{self.name} observes {dead_entity.name}'s death.")
