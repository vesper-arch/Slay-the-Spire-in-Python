import math
import random

import helper
import items
from entities import Enemy


class AcidSlimeL(Enemy):
    def __init__(self, ):
        super().__init__([65, 69], 0, 'Acid Slime (L)', {"Split": True})

    def set_intent(self):
        move_roll = random.random()
        while True:
            if self.health < math.floor(self.max_health * 0.5):
                self.next_move, self.intent = [("Split", "Split")], "<yellow>Unknown</yellow>"
            elif move_roll <= 0.3 and self.move_spam_check("Corrosive Spit", 3):
                self.next_move, self.intent = [("Corrosive Spit", "Attack", (11,)), ("Status", (items.Slimed, 2, "discard pile"))], "<aggresive>Attack</aggresive> Σ11 / <debuff>Debuff</debuff>"
            elif 0.3 < move_roll < 0.7 and self.move_spam_check("Tackle", 2):
                self.next_move, self.intent = [("Tackle", "Attack", (16,))], "<aggresive>Attack</aggresive> Σ16"
            elif 0.7 <= move_roll < 1 and self.move_spam_check("Lick", 2):
                self.next_move, self.intent = [("Lick", "Debuff", (helper.Weak, 2))], "<debuff>Debuff</debuff>"
            else:
                continue
            break

class AcidSlimeM(Enemy):
    def __init__(self, ):
        super().__init__([28, 32], 0, "Acid Slime (M)", )

    def set_intent(self):
        while True:
            move_roll = random.random()
            if move_roll <= 0.3 and self.move_spam_check("Corrosive Spit", 3):
                self.next_move, self.intent = [("Corrosive Spit", "Attack", (7,)), ("Status", (items.Slimed, 1, "discard pile"))], "<aggresive>Attack</aggresive> Σ11 / <debuff>Debuff</debuff>"
            elif 0.3 < move_roll < 0.7 and self.move_spam_check("Tackle", 2):
                self.next_move, self.intent = [("Tackle", "Attack", (10,))], "<aggresive>Attack</aggresive> Σ16"
            elif 0.7 <= move_roll < 1 and self.move_spam_check("Lick", 2):
                self.next_move, self.intent = [("Lick", "Debuff", (helper.Weak, 1))], "<debuff>Debuff</debuff>"
            else:
                continue
            break

class AcidSlimeS(Enemy):
    def __init__(self, ):
        super().__init__([8, 12], 0, "Acid Slime (S)", )

    def set_intent(self):
        while True:
            move_roll = random.random()
            if self.active_turns == 1:
                if move_roll <= 0.5:
                    self.next_move, self.intent = [("Lick", "Debuff", (helper.Weak, 1))], "<debuff>Debuff</debuff>"
                else:
                    self.next_move, self.intent = [("Tackle", "Attack", (3,))], "<aggresive>Attack</aggresive> Σ3"
            else:
                if self.past_moves[-1] == 'Lick':
                    self.next_move, self.intent = [("Tackle", "Attack", (3, ))], "<aggresive>Attack</aggresive> Σ3"
                else:
                    self.next_move, self.intent = [("Lick", "Debuff", (helper.Weak, 1))], "<debuff>Debuff</debuff>"
            break

class SpikeSlimeL(Enemy):
    def __init__(self, ):
        super().__init__([64, 70], 0, "Spike Slime (L)", {"Split": True})

    def set_intent(self):
        while True:
            move_roll = random.random()
            if self.health < math.floor(self.max_health * 0.5):
                self.next_move, self.intent = [("Split", "Split")], "<yellow>Unknown</yellow>"
            elif move_roll <= 0.3 and self.move_spam_check("Flame Tackle", 3):
                self.next_move, self.intent = [("Flame Tackle", "Attack", (16,)), ("Status", (items.Slimed, 2, "discard pile"))], "<aggresive>Attack</aggresive> Σ16 / <debuff>Debuff</debuff>"
            elif move_roll < 0.3 and self.move_spam_check("Lick", 3):
                self.next_move, self.intent = [("Lick", "Debuff", (helper.Frail, 2))], "<debuff>Debuff</debuff>"
            else:
                continue
            break

class SpikeSlimeM(Enemy):
    def __init__(self, ):
        super().__init__([28, 32], 0, "Spike Slime (M)", )

    def set_intent(self):
        while True:
            move_roll = random.random()
            if move_roll <= 0.3 and self.move_spam_check("Flame Tackle", 3):
                self.next_move, self.intent = [("Flame Tackle", "Attack", (16,)), ("Status", (items.Slimed, 2, "discard pile"))], "<aggresive>Attack</aggresive> Σ16 / <debuff>Debuff</debuff>"
            elif move_roll < 0.3 and self.move_spam_check("Lick", 3):
                self.next_move, self.intent = [("Lick", "Debuff", (helper.Frail, 2))], "<debuff>Debuff</debuff>"
            else:
                continue
            break

class SpikeSlimeS(Enemy):
    def __init__(self, ):
        super().__init__([10, 14], 0, "Spike Slime (S)", )

    def set_intent(self):
        self.next_move, self.intent = [("Tackle", "Attack", (5, ))], "<aggresive>Attack</aggresive> Σ5"

class Cultist(Enemy):
    def __init__(self, ):
        super().__init__([48, 54], 0, "Cultist", )

    def set_intent(self):
        if self.active_turns == 1:
            self.next_move, self.intent = [("Incantation", "Buff", ("Ritual", 3))], "<buff>Buff</buff>"
        else:
            self.next_move, self.intent = [("Dark Strike", "Attack", (6, ))], "<aggresive>Attack</aggresive> Σ6"

class JawWorm(Enemy):
    def __init__(self, ):
        super().__init__([40, 44], 0, "Jaw Worm", )

    def set_intent(self):
        while True:
            move_roll = random.random()
            if self.active_turns == 1:
                self.next_move, self.intent = [("Chomp", "Attack", (11,))], "<aggresive>Attack</aggresive> 11"
            elif self.active_turns > 1:
                if move_roll <= 0.45 and self.move_spam_check("Bellow", 2):
                    self.next_move, self.intent = [("Bellow", "Buff", (helper.Strength, 3)), ("Block", (6,))], "<buff>Buff</buff> / <light-blue>Block</light-blue>"
                elif 0.45 < move_roll <= 0.75 and self.move_spam_check("Thrash", 3):
                    self.next_move, self.intent = [("Thrash", "Attack", (7,)), ("Block", (5,))], "<aggresive>Attack</aggresive> 7 / <light-blue>Block</light-blue>"
                elif move_roll > 0.75 and self.move_spam_check("Chomp", 2):
                    self.next_move, self.intent = [("Chomp", "Attack", (11,))], "<aggresive>Attack</aggresive> 11"
            else:
                continue
            break

class RedLouse(Enemy):
    def __init__(self, ):
        self.damage = random.randint(5, 7)
        super().__init__([10, 15], 0, "Red Louse", [helper.CurlUp(self, random.randint(3, 7))])

    def set_intent(self):
        while True:
            move_roll = random.random()
            if move_roll <= 0.25 and self.move_spam_check("Grow", 3):
                self.next_move, self.intent = [("Grow", "Buff", (helper.Strength, 3))], "<buff>Buff</buff>"
            elif move_roll > 0.25 and self.move_spam_check("Bite", 3):
                self.next_move, self.intent = [("Bite", "Attack", (self.damage,))], f"<aggresive>Attack</aggresive> {self.damage}"
            else:
                continue
            break

class GreenLouse(Enemy):
    def __init__(self, ):
        self.damage = random.randint(5, 7)
        super().__init__([11, 17], 0, "Green Louse", [helper.CurlUp(self, random.randint(3, 7))])

    def set_intent(self):
        while True:
            move_roll = random.random()
            if move_roll <= 0.25 and self.move_spam_check("Spit Web", 3):
                self.next_move, self.intent = [("Spit Web", "Debuff", (helper.Weak, 2))], "<debuff>Debuff</debuff>"
            elif move_roll > 0.25 and self.move_spam_check("Bite", 3):
                self.next_move, self.intent = [("Bite", "Attack", (self.damage,))], f"<aggresive>Attack</aggresive> {self.damage}"
            else:
                continue
            break

class FungiBeast(Enemy):
    def __init__(self, ):
        super().__init__([22, 28], 0, "Fungi Beast", {"Spore Cloud": 2})

    def set_intent(self):
        while True:
            move_roll = random.random()
            if move_roll <= 0.6 and self.move_spam_check("Bite", 3):
                self.next_move, self.intent = [("Bite", "Attack", (6, ))], "<aggresive>Attack</aggresive> 6"
            elif move_roll > 0.6 and self.move_spam_check("Grow", 2):
                self.next_move, self.intent = [("Grow", "Buff", (helper.Strength, 3))], "<buff>Buff</buff>"
            else:
                continue
            break

class FatGremlin(Enemy): # Fatass
    def __init__(self, ):
        super().__init__([13, 17], 0, "Fat Gremlin")

    def set_intent(self):
        self.next_move, self.intent = [("Smash", "Attack", (4,)), ("Debuff", (helper.Weak, 1))], "<aggresive>Attack</aggresive> 4 / <debuff>Debuff</debuff>"

class MadGremlin(Enemy):
    def __init__(self, ):
        super().__init__([20, 24], 0, "Mad Gremlin", {"Anger": 1})

    def set_intent(self):
        self.next_move, self.intent = [("Scratch", "Attack", (4,))], "<aggresive>Attack</aggresive> 4"

class ShieldGremlin(Enemy):
    def __init__(self, enemies):
        super().__init__([12, 15], 0, "Shield Gremlin")
        self.enemies = enemies

    def set_intent(self):
        other_gremlins = [enemy for enemy in self.enemies if "Gremlin" in enemy.name and "Shield" not in enemy.name]
        move_roll = random.random()
        if len(other_gremlins) > 0:
            self.next_move, self.intent = [("Protect", "Block", (7, random.choice(other_gremlins)))], "<light-blue>Block</light-blue>"
        else:
            # These stats are made up since the wiki(https://slay-the-spire.fandom.com/wiki/Gremlins) is unclear
            if move_roll <= 0.75:
                self.next_move, self.intent = [("Shield Bash", "Attack", (6,))], "<aggresive>Attack</aggresive> 6"
            else:
                self.next_move, self.intent = [("Protect", "Block", (6,))], "<light-blue>Block</light-blue>"

class SneakyGremlin(Enemy):
    def __init__(self, ):
        super().__init__([10, 14], 0, "Sneaky Gremlin", )

    def set_intent(self):
        self.next_move, self.intent = [("Puncture", "Attack", (9,))], "<aggresive>Attack</aggresive> 9"

class WizardGremlin(Enemy):
    def __init__(self, ):
        super().__init__([23, 25], 0, "Gremlin Wizard", )

    def set_intent(self):
        attack_indices = [2 + 4 * x for x in range(50)]
        if self.active_turns - 1 in attack_indices:
            self.next_move, self.intent = [("Ultimate Blast", "Attack", (25,))], "<aggresive>Attack</aggresive> 25"
        else:
            self.next_move, self.intent = [("Charging.", ("Charging",))], "<yellow>Charging</yellow>"

class Looter(Enemy):
    def __init__(self, ):
        self.escaped = False
        super().__init__([44, 48], 0, "Looter", {"Theivery": 15})

    def set_intent(self):
        while True:
            move_roll = random.random()
            if self.active_turns in (1, 2):
                self.next_move, self.intent = [("Mug", "Attack", (10,))], "<aggresive>Attack</aggresive> 10"
            elif self.active_turns == 3:
                if move_roll <= 0.5:
                    self.next_move, self.intent = [("Lunge", "Attack", (12,))], "<aggresive>Attack</aggresive> 12"
                else:
                    self.next_move, self.intent = [("Smoke Bomb", "Block", (6,))], "<light-blue>Block</light-blue>"
            elif self.active_turns > 3:
                if self.past_moves[-1] == 'Lunge':
                    self.next_move, self.intent = [("Smoke Bomb", "Block", (6,))], "<light-blue>Block</light-blue>"
                elif self.past_moves[-1] == 'Smoke Bomb':
                    self.next_move, self.intent = [("Escape", "Escape")], "<red>Escape</red>"
            else:
                continue
            break

class Mugger(Enemy):
    def __init__(self, ):
        self.escaped = False
        super().__init__([44, 48], 0, "Looter", {"Theivery": 15})

    def set_intent(self):
        while True:
            move_roll = random.random()
            if self.active_turns in (1, 2):
                self.next_move, self.intent = [("Mug", "Attack", (10,))], "<aggresive>Attack</aggresive> 10"
            elif self.active_turns == 3:
                if move_roll <= 0.5:
                    self.next_move, self.intent = [("Lunge", "Attack", (16,))], "<aggresive>Attack</aggresive> 16"
                else:
                    self.next_move, self.intent = [("Smoke Bomb", "Block", (11,))], "<light-blue>Block</light-blue>"
            elif self.active_turns > 3:
                if self.past_moves[-1] == 'Lunge':
                    self.next_move, self.intent = [("Smoke Bomb", "Block", (11,))], "<light-blue>Block</light-blue>"
                elif self.past_moves[-1] == 'Smoke Bomb':
                    self.next_move, self.intent = [("Escape", "Escape")], "<red>Escape</red>"
            else:
                continue
            break

class BlueSlaver(Enemy):
    def __init__(self, ):
        super().__init__([46, 50], 0, "Blue Slaver", )

    def set_intent(self):
        while True:
            move_roll = random.random()
            if move_roll <= 0.6 and self.move_spam_check("Stab", 3):
                self.next_move, self.intent = [("Stab", "Attack", (12,))], "<aggresive>Attack</aggresive> 12"
            elif move_roll > 0.6 and self.move_spam_check("Rake", 3):
                self.next_move, self.intent = [("Rake", "Attack", (7,)), ("Debuff", (helper.Weak, 1))], "<aggresive>Attack</aggresive> 7 / <debuff>Debuff</debuff>"
            else:
                continue
            break

class RedSlaver(Enemy):
    def __init__(self, ):
        super().__init__([46, 50], 0, "Red Slaver", )

    def set_intent(self):
        scrape_pattern = [i + (i // 2) for i in range(1, 50 + 1)]
        stab_pattern = [i * 3 for i in range(1, 50)]
        while True:
            move_roll = random.random()
            if self.active_turns == 1:
                self.next_move, self.intent = [("Stab", "Attack", (13,))], "<aggresive>Attack</aggresive> 13"
            elif self.active_turns > 1 and "Entangled" not in self.past_moves:
                if move_roll <= 0.75:
                    if self.active_turns - 1 in scrape_pattern:
                        self.next_move, self.intent = [("Scrape", "Attack", (8,)), ("Debuff", (helper.Vulnerable, 1))], "<aggresive>Attack</aggresive> 8 / <debuff>Debuff</debuff>"
                    elif self.active_turns - 1 in stab_pattern:
                        self.next_move, self.intent = [("Stab", "Attack", (13,))], "<aggresive>Attack</aggresive> 13"
                else:
                    self.next_move, self.intent = [("Entangle", "Debuff", ("Entangled", 1))], "<debuff>Debuff</debuff>"
            elif "Entangled" in self.past_moves:
                if move_roll <= 0.55 and self.move_spam_check("Scrape", 3):
                    self.next_move, self.intent = [("Scrape", "Attack", (8,)), ("Debuff", (helper.Vulnerable, 1))], "<aggresive>Attack</aggresive> 8 / <debuff>Debuff</debuff>"
                elif move_roll > 0.55 and self.move_spam_check("Stab", 3):
                    self.next_move, self.intent = [("Stab", "Attack", (13,))], "<aggresive>Attack</aggresive> 13"
            else:
                continue
            break

# Elites
class GremlinNob(Enemy):
    def __init__(self, ):
        super().__init__([82, 86], 0, "Gremlin Nob", )

    def set_intent(self):
        while True:
            move_roll = random.random()
            if self.active_turns == 1:
                self.next_move, self.intent = [("Bellow", "Buff", ("Enrage", 2))], "<buff>Buff</buff>"
            elif self.active_turns > 1:
                if move_roll <= 0.33:
                    self.next_move, self.intent = [("Skull Bash", "Attack", (6,)), (helper.Vulnerable, 2)], "<aggresive>Attack</aggresive> 6 / <debuff>Debuff</debuff>"
                elif move_roll > 0.33 and self.move_spam_check("Rush", 3):
                    self.next_move, self.intent = [("Rush", "Attack", (14,))], "<aggresive>Attack</aggresive> 14"
            else:
                continue
            break

class Lagavulin(Enemy):
    def __init__(self, ):
        super().__init__([109, 111], 0, "Lagavulin", {"Asleep": True, "Metallicize": 8})

    def set_intent(self):
        while True:
            if self.debuffs["Asleep"]:
                self.next_move, self.intent = [("Sleeping", "Sleeping", ("..."))], "<yellow>Asleep</yellow>"
            elif not self.debuffs['Asleep'] and self.health < self.max_health:
                self.next_move, self.intent = [("Stunned", "Stunned")], "<yellow>Stunned</yellow>" # Fix later
            elif not self.debuffs['Asleep']:
                if self.awake_turns in (i * 3 for i in range(4, 50)):
                    self.next_move, self.intent = [("Attack", "Attack", (18,))], "<aggresive>Attack</aggresive> 18"
                else:
                    self.next_move, self.intent = [("Siphon Soul", "Debuff", ("Dexterity", -1)), ("Debuff", (helper.Strength, -1))], "<debuff>Debuff</debuff>"
            else:
                continue
            break

class Sentry(Enemy):
    def __init__(self, state):
        self.state = state
        super().__init__([38, 42], 0, "Sentry", {"Artifact": 1})

    def set_intent(self):
        while True:
            if self.active_turns == 1:
                if self.state == 'Beam':
                    self.next_move, self.intent = [("Beam", "Attack", (9,))], "<aggresive>Attack</aggresive> 9"
                elif self.state == 'Bolt':
                    self.next_move, self.intent = [("Bolt", "Status", ("Dazed", 2, 'discard pile'))], "<debuff>Debuff</debuff>"
            elif self.active_turns > 1:
                if self.past_moves[-1] == 'Beam':
                    self.next_move, self.intent = [("Bolt", "Status", ("Dazed", 2, 'discard pile'))], "<debuff>Debuff</debuff>"
                else:
                    self.next_move, self.intent = [("Beam", "Attack", (9,))], "<aggresive>Attack</aggresive> 9"
            else:
                continue
            break

class SlimeBoss(Enemy):
    def __init__(self, **kwargs):
        defaults = {
            "health_range": [140, 140],
            "block": 0,
            "name": "Slime Boss",
            "powers": {"Split": True}
        }
        defaults.update(kwargs)
        super().__init__(**defaults)

    def set_intent(self):
        if self.active_turns in list(range(1, 50 + 1, 3)): # Goop turn
            self.next_move, self.intent = [("Goop Spray", "Status", (items.Slimed, 3, 'discard pile'))], "<debuff>Debuff</debuff>"
        elif self.active_turns in list(range(2, 50 + 1, 3)): # Preparing turns
            self.next_move, self.intent = [("Preparing", "Charging", ("Preparing."))], "<yellow>Unknown</yellow>"
        elif self.active_turns in list(range(3, 50 + 1, 3)):
            self.next_move, self.intent = [("Slam", "Attack", (35,))], "<aggresive>Attack</aggresive> 35"

class Guardian(Enemy):
    def __init__(self, ):
        self.mode = "Offensive"
        self.offensive_turns = 1
        self.defensive_turns = 1
        self.mode_shift_base = 30
        super().__init__([240, 240], 0, "Guardian", {"Mode Shift": 30})

    def set_intent(self):
        if self.mode == 'Offensive':
            self.offensive_turns = 1
            if self.offensive_turns in list(range(1, 50, 4)):
                self.next_move, self.intent = [("Charging Up", "Block", (9,))], "<light-blue>Block</light-blue>"
            elif self.offensive_turns in list(range(2, 50, 4)):
                self.next_move, self.intent = [("Fierce Bash", "Attack", (32,))], "<aggresive>Attack</aggresive> Σ32"
            elif self.offensive_turns in list(range(3, 50, 4)):
                self.next_move, self.intent = [("Vent Steam", "Debuff", (helper.Vulnerable, 2)), ("Debuff", (helper.Weak, 2))], "<debuff>Debuff</debuff>"
            elif self.offensive_turns in list(range(4, 50, 4)):
                self.next_move, self.intent = [("Whirlwind", "Attack", (5, 4))], "<aggresive>Attack</aggresive> Σ5x4"
        elif self.mode == 'Defensive':
            self.defensive_turns = 1
            if self.defensive_turns in list(range(1, 50, 3)):
                self.next_move, self.intent = [("Defensive Mode", "Buff", ("Sharp Hide", 3))], "<buff>Buff</buff>"
            elif self.defensive_turns in list(range(2, 50, 3)):
                self.next_move, self.intent = [("Roll Attack", "Attack", (9,))], "<aggresive>Attack</aggresive> 9"
            elif self.defensive_turns in list(range(3, 50, 3)):
                self.mode_shift_base += 10
                self.next_move, self.intent = [("Twin Slam", "Attack", (8, 2)), ("Remove Effect", ("Sharp Hide", "Buffs")), ("Buff", ("Mode Shift", self.mode_shift_base))], "<aggresive>Attack</aggresive> 8x2 / <buff>Buff</buff>"

class Hexaghost(Enemy):
    def __init__(self, ):
        self.flames = 0
        self.upgrade_burn = False
        self.divider_dmg = (self.player.health / 12) + 1
        super().__init__([250, 250], 0, "Hexaghost", )

    def set_intent(self):
        if self.active_turns == 1:
            self.next_move, self.intent = [("Activate", "Charging", (""))], "<yellow>Unknown</yellow>"
        elif self.active_turns == 2:
            self.next_move, self.intent = [("Divider", "Attack", (self.divider_dmg, 6))], f"<aggresive>Attack</aggresive> Σ{self.divider_dmg}x6"
        elif self.active_turns > 2:
            if self.flames in (0, 2, 5):
                self.next_move, self.intent = [("Sear", "Attack", (6,)), ("Status", (items.Burn if not self.upgrade_burn else items.Burn, 1, "discard pile"))]
            elif self.flames in (1, 4):
                self.next_move, self.intent = [("Tackle", "Attack", (5, 2))], "<aggresive>Attack</aggresive> Σ5x2"
            elif self.flames == 3:
                self.next_move, self.intent = [("Inflame", "Buff", (helper.Strength, 2)), ("Block", (12,))], "<buff>Buff</buff> / <light-blue>Block</light-blue>"
            elif self.flames == 6:
                self.next_move, self.intent = [("Inferno", "Attack", (2, 5)), ("Status", (items.Burn, 3, "discard pile"))]

# Act 1 Encounters
# First 3 Encounters
def cultist():
    return [Cultist()] # 25%
def jaw_worm():
    return [JawWorm()] # 25%
def two_louses():
    return [random.choice([RedLouse, GreenLouse])(), random.choice([RedLouse, GreenLouse])()] # 25%
def small_slimes():
    return [random.choice([SpikeSlimeM, AcidSlimeM])(), random.choice([SpikeSlimeS, AcidSlimeS])()] # 25%
first3_encounters = [cultist, jaw_worm, two_louses, small_slimes]
# Remaining Encounters
def gremlin_gang(enemies):
    return [MadGremlin(), MadGremlin(), SneakyGremlin(), SneakyGremlin(), FatGremlin(), FatGremlin(), WizardGremlin(), ShieldGremlin(enemies)]
def large_slime():
    return [random.choice([SpikeSlimeL, AcidSlimeL])()]
def lots_of_slimes():
    return [enemy() for enemy in [SpikeSlimeS, SpikeSlimeS, SpikeSlimeS, AcidSlimeS, AcidSlimeS]]
def blue_slaver():
    return [BlueSlaver()]
def red_slaver():
    return [RedSlaver()]
def three_louses():
    return [random.choice([GreenLouse, RedLouse])() for _ in range(3)]
def two_fungi_beasts():
    return [FungiBeast(), FungiBeast()]
def exordium_thugs():
    enemy_one = [RedLouse, GreenLouse, SpikeSlimeM, AcidSlimeM]
    enemy_two = [BlueSlaver, RedSlaver, Looter, Cultist]
    return [random.choice(enemy_one)(), random.choice(enemy_two)()]
def exordium_wildlife():
    enemy_one = [FungiBeast, JawWorm]
    enemy_two = [RedLouse, GreenLouse, SpikeSlimeM, AcidSlimeM]
    return [random.choice(enemy_one)(), random.choice(enemy_two)()]
def looter():
    return [Looter()]
# Elites
def gremlin_nob():
    return [GremlinNob()]
def sentries():
    return [Sentry('Bolt'), Sentry('Beam'), Sentry('Bolt')]
def lagavulin():
    return [Lagavulin()]

def create_act1_normal_encounters(enemies):
    remaining_act1_encounters = [lambda: gremlin_gang(enemies), large_slime, lots_of_slimes, blue_slaver, red_slaver,
                                three_louses, two_fungi_beasts, exordium_thugs, exordium_wildlife, looter]
    return [random.choice(first3_encounters)() for _ in range(3)] + [random.choices(remaining_act1_encounters, weights=[6.25, 12.5, 6.35, 12.5, 6.25, 12.5, 12.5, 9.375, 9.375, 12.5], k=1)[0]() for _ in range(15)]

def create_act1_elites():
    return [random.choice([gremlin_nob, sentries, lagavulin])() for _ in range(4)]

def create_act1_boss():
    return [[random.choice([SlimeBoss(), Hexaghost(), Guardian()])]]
