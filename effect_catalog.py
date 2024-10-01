from __future__ import annotations

import math
from copy import deepcopy
from typing import TYPE_CHECKING
from uuid import uuid4

import definitions
import effect_interface as ei
from ansi_tags import ansiprint
from definitions import (
    CardType,
    EffectType,
    StackType,
)
from message_bus_tools import Message, Registerable

if TYPE_CHECKING:
    from enemy import Enemy
    from entities import Action
    from card_catalog import Card
    from player import Player


def get_attribute(item, attribute):
    '''While refactoring, some items (Cards) have properties that are on the object, whereas others have them in a dictionary.
        This function bridges the difference.
    '''
    if isinstance(item, dict):
        return item[attribute]
    else:
        return getattr(item, attribute.lower())

def effect_amount(effect: type[Effect], buffs_or_debuffs: list[Effect]) -> int:
    ''' Returns the total amounts of a specific effect in a given list of effects.'''
    return sum([e.amount for e in buffs_or_debuffs if isinstance(e, effect)])


class Effect(Registerable):
    def __init__(self, host, name, stack_type: StackType, effect_type, info, amount=0, one_turn=False):
        self.uid = uuid4()
        self.subscribed = False
        self.host = host
        self.name = name
        self.stack_type = stack_type
        self.type = effect_type
        self.info = info # For convenience purposes, this will be a generalized description of the effect.
        self.amount = amount
        self.one_turn = one_turn

    def __add__(self, other):
        if self.name != other.name:
            raise ValueError(f"Effects of names {self.name} and {other.name} cannot be merged. Addition only works with the same effect.")
        new_effect = deepcopy(self)
        new_effect.amount = self.amount + other.amount
        return new_effect

    def pretty_print(self):
        return f"{self.get_name()} | <yellow>{self.info}</yellow>"

    def get_name(self):
        # shorter vars for readability
        c = definitions.STACK_TYPE_COLOR_MAPPING
        st = self.stack_type
        return f"<{c[st]}>{self.name}</{c[st]}>{f' {self.amount}' if self.stack_type is not None else ''}"

    def tick(self):
        if self.one_turn is True:
            self.amount = 0
        elif self.stack_type == StackType.DURATION:
            self.amount -= 1


class Invulnerable(Effect):
    '''Prevents all damage. Great for testing!'''
    registers = [Message.BEFORE_ATTACK]
    priorities = [100]   # Called last so it can cancel all other effects.

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Invulnerable",
            StackType.DURATION_AND_INTENSITY,
            EffectType.BUFF,
            "Prevents all damage.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.BEFORE_ATTACK:
            attacker, target, damage_dealer = data
            if self.host == target:
                damage_dealer.set_damage(0, "<buff>,.-~*´¨¯¨`*·~-.¸-INVULNERABLE-,.-~*´¨¯¨`*·~-.¸</buff>")
            else:
                pass


class Strength(Effect):
    registers = [Message.BEFORE_ATTACK]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Strength",
            StackType.INTENSITY,
            EffectType.BUFF,
            "Increases attack damage by X.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.BEFORE_ATTACK:
            attacker, target, damage_dealer = data
            if self.host == attacker:
                damage_dealer.modify_damage(
                    self.amount, f"<buff>Strength</buff>({self.amount:+d} dmg)"
                )
            elif self.host == target:
                pass  # The target has the Strength effect
            else:
                pass  # Neither attacker nor target has the Strength effect


class StrengthDown(Effect):
    registers = [Message.END_OF_TURN]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Strength Down",
            StackType.INTENSITY,
            EffectType.DEBUFF,
            "At the end of your turn, lose X <buff>Strength</buff>.",
            amount,
            one_turn=True,
        )

    def callback(self, message, data):
        if message == Message.END_OF_TURN:
            player, _ = data
            ei.apply_effect(player, None, Strength, -self.amount)


class Vulnerable(Effect):
    registers = [Message.BEFORE_ATTACK]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Vulnerable",
            StackType.DURATION,
            EffectType.DEBUFF,
            "Target takes 50% more damage from attacks.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.BEFORE_ATTACK:
            attacker, target, damage_dealer = data
            if self.host == attacker:
                pass  # The attacker is the one with the Vulnerable effect
            elif self.host == target:
                damage_dealer.modify_damage(
                    math.floor(damage_dealer.damage * 0.5),
                    "<debuff>Vulnerable</debuff>(x1.5 dmg)",
                )
            else:
                pass  # Neither attacker nor target has the Vulnerable effect


class Weak(Effect):
    registers = [Message.BEFORE_ATTACK]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Weak",
            StackType.DURATION,
            EffectType.DEBUFF,
            "Target deals 25% less attack damage.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.BEFORE_ATTACK:
            attacker, target, damage_dealer = data
            if self.host == attacker:
                damage_dealer.modify_damage(
                    -math.floor(damage_dealer.damage * 0.25),
                    "<debuff>Weak</debuff>(x0.75 dmg)",
                )
            elif self.host == target:
                pass
            else:
                pass


class Frail(Effect):
    registers = [Message.BEFORE_BLOCK]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Frail",
            StackType.DURATION,
            EffectType.DEBUFF,
            "You gain 25% less <keyword>Block</keyword> from cards.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.BEFORE_BLOCK:
            _, card = data
            if card is not None:
                card.modify_block(
                    -math.floor(card.block * 0.25),
                    "<debuff>Frail</debuff>(x0.75 block)",
                )


class CurlUp(Effect):
    registers = [Message.ON_ATTACKED]

    def __init__(self, host, amount):
        # INFO: Due to some very strange bug, the 'C' is interpreted as the end of an escape sequence(^[[?62;4C) which is why it's escaped. wtf
        super().__init__(
            host,
            "Curl Up",
            StackType.INTENSITY,
            EffectType.BUFF,
            "On recieving attack damage, rolls and gains X <keyword>Block</keyword>. (Once per combat)",
            amount,
        )  # noqa: W605

    def callback(self, message, data):
        if message == Message.ON_ATTACKED:
            target = data
            if target != self.host:
                return
            target.blocking(block=self.amount, context=self.name)
            self.amount = 0


class Ritual(Effect):
    registers = [Message.END_OF_TURN]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Ritual",
            StackType.INTENSITY,
            EffectType.BUFF,
            "At the end of its turn, gains X <buff>Strength</buff>.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.END_OF_TURN:
            _ = data
            ei.apply_effect(self.host, None, Strength, self.amount)


class Enrage(Effect):
    registers = [Message.ON_CARD_PLAY]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Enrage",
            StackType.INTENSITY,
            EffectType.BUFF,
            f"Whenever you play a Skill, gains {amount} Strength..",
            amount,
        )

    def callback(self, message, data):
        if message == Message.ON_CARD_PLAY:
            origin, card, target, enemies = data
            if card.type == CardType.SKILL:
                ei.apply_effect(self.host, None, Strength, self.amount)


class Corruption(Effect):
    registers = [Message.ON_CARD_PLAY]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Corruption",
            StackType.INTENSITY,
            EffectType.BUFF,
            "Whenever you play a Skill, exhaust it.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.ON_CARD_PLAY:
            origin, card, target, enemies = data
            if card.type == CardType.SKILL:
                # TODO: Exhaust the card
                pass


class NoDraw(Effect):
    registers = [Message.BEFORE_DRAW, Message.END_OF_TURN]

    def __init__(self, host, _):
        super().__init__(
            host,
            "No Draw",
            StackType.NONE,
            EffectType.DEBUFF,
            "You may not draw any more cards this turn.",
        )

    def callback(self, message, data: tuple[Player, Action]):
        if message == Message.BEFORE_DRAW:
            player, action = data
            ansiprint(
                f"{player.name} cannot draw any more cards because of <debuff>No Draw</debuff>."
            )
            action.cancel(
                reason="You cannot draw any cards because of <debuff>No Draw</debuff>."
            )
        if message == Message.END_OF_TURN:
            self.unsubscribe()


class Combust(Effect):
    registers = [Message.END_OF_TURN]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Combust",
            StackType.INTENSITY,
            EffectType.BUFF,
            "At the end of your turn, deals X damage to ALL enemies.",
            amount,
        )

    def callback(self, message, data: tuple[Player, list[Enemy]]):
        if message == Message.END_OF_TURN:
            player, enemies = data
            for enemy in enemies:
                enemy.health -= self.amount


class DarkEmbrace(Effect):
    registers = [Message.ON_EXHAUST]

    def __init__(self, target, amount=1):
        # "Whenever a card is <keyword>Exhausted</keyword>, draw 1 card
        super().__init__(
            None,
            name="Dark Embrace",
            stack_type=StackType.NONE,
            effect_type=EffectType.BUFF,
            info="Whenever a card is <keyword>Exhausted</keyword>, draw 1 card.",
            amount=amount,
        )

    def callback(self, message, data: tuple[Player, Card]):
        if message == Message.END_OF_TURN:
            player, card = data
            player.draw_cards(self.amount)


class Evolve(Effect):
    registers = [Message.ON_CARD_PLAY]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Evolve",
            StackType.NONE,
            EffectType.BUFF,
            "Whenever you play a Status or Curse, draw 1 card.",
            amount,
        )

    def callback(self, message, data: tuple[Player, Card, Enemy, list[Enemy]]):
        if message == Message.ON_CARD_PLAY:
            origin, card, target, enemies = data
            if card.type in (CardType.STATUS, CardType.CURSE):
                origin.draw_cards(1)


class FeelNoPain(Effect):
    registers = [Message.ON_CARD_PLAY]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Feel No Pain",
            StackType.INTENSITY,
            EffectType.BUFF,
            "Whenever you play a Skill, gain X <keyword>Block</keyword>.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.ON_CARD_PLAY:
            origin, card, target, enemies = data
            if card.type == CardType.SKILL:
                origin.blocking(block=self.amount, context=self.name)


class FireBreathing(Effect):
    registers = [Message.ON_CARD_PLAY]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Fire Breathing",
            StackType.INTENSITY,
            EffectType.BUFF,
            "Whenever you play an Attack, deal X damage to ALL enemies.",
            amount,
        )

    def callback(self, message, data: tuple[Player, Card, Enemy, list[Enemy]]):
        if message == Message.ON_CARD_PLAY:
            player, card, target, enemies = data
            if card.type == CardType.ATTACK:
                for enemy in enemies:
                    enemy.health -= self.amount
                    ansiprint(
                        f"{enemy.name} took {self.amount} damage from <buff>Fire Breathing</buff>."
                    )


class FlameBarrier(Effect):
    # "Gain 12 <keyword>Block</keyword>. Whenever you're attacked this turn, deal 4 damage back."
    registers = [Message.ON_ATTACKED]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Flame Barrier",
            StackType.NONE,
            EffectType.BUFF,
            "Gain 12 <keyword>Block</keyword>. Whenever you're attacked this turn, deal 4 damage back.",
            amount,
        )

    def callback(self, message, data):
        if message == Message.ON_ATTACKED:
            target = data
            target.health -= 4


class Metallicize(Effect):
    registers = [Message.END_OF_TURN]

    def __init__(self, host, amount=3):
        super().__init__(
            host,
            "Metallicize",
            StackType.INTENSITY,
            EffectType.BUFF,
            "At the end of your turn, gain 3 <keyword>Block</keyword>.",
            amount,
            one_turn=True,
        )

    def callback(self, message, data: tuple[Player, list[Enemy]]):
        if message == Message.END_OF_TURN:
            player, enemies = data
            self.host.blocking(block=self.amount, context=f"{self.name}{self.amount}")


class Rage(Effect):
    # "Whenever you play an <keyword>Attack</keyword> this turn, gain 3 <keyword>Block</keyword>.""
    registers = [Message.ON_CARD_PLAY, Message.END_OF_TURN]

    def __init__(self, host, amount=3):
        super().__init__(
            host,
            "Rage",
            StackType.NONE,
            EffectType.BUFF,
            "Whenever you play an <keyword>Attack</keyword> this turn, gain 3 <keyword>Block</keyword>.",
            amount=amount,
        )

    def callback(self, message, data):
        if message == Message.ON_CARD_PLAY:
            player, card, target, enemies = data
            if card.type == CardType.ATTACK:
                player.blocking(block=self.amount, context=self.name)
        elif message == Message.END_OF_TURN:
            self.unsubscribe()


class Barricade(Effect):
    # "Barricade", "<keyword>Block</keyword> is not removed at the start of your turn."
    registers = [Message.BEFORE_BLOCK, Message.END_OF_TURN]

    def __init__(self, host, amount=0):
        super().__init__(
            host,
            "Barricade",
            StackType.NONE,
            EffectType.BUFF,
            "<keyword>Block</keyword> is not removed at the start of your turn.",
            amount,
        )
        self.end_of_turn_block = None

    def callback(
        self, message, data: tuple[Player, Action] | tuple[Player, list[Enemy]]
    ):
        if message == Message.END_OF_TURN:
            player, enemies = data
            self.end_of_turn_block = player.block
        elif message == Message.BEFORE_BLOCK and self.end_of_turn_block is not None:
            player, action = data
            action.set_amount(self.end_of_turn_block)
            self.unsubscribe()


class Berzerk(Effect):
    # "Gain 2 <debuff>Vulnerable</debuff>. At the start of your turn, gain 1 <keyword>Energy</keyword>."
    registers = [Message.START_OF_TURN]

    def __init__(self, host, amount=2):
        super().__init__(
            host,
            "Berzerk",
            StackType.NONE,
            EffectType.BUFF,
            "Gain 2 <debuff>Vulnerable</debuff>. At the start of your turn, gain 1 <keyword>Energy</keyword>.",
            amount,
        )

    def callback(self, message, data: tuple[int, Player]):
        if message == Message.START_OF_TURN:
            turn, player = data
            player.energy += 1


class Brutality(Effect):
    # "At the start of your turn, lose 1 HP and draw 1 card."
    registers = [Message.START_OF_TURN]

    def __init__(self, host, amount=1):
        super().__init__(
            host,
            "Brutality",
            StackType.NONE,
            EffectType.BUFF,
            "At the start of your turn, lose 1 HP and draw 1 card.",
            amount=amount,
        )

    def callback(self, message, data: tuple[int, Player]):
        if message == Message.START_OF_TURN:
            turn, player = data
            player.take_sourceless_dmg(1)
            player.draw_cards(1)


class Split(Effect):
    # When activated, splits into two smaller enemies.
    registers = [Message.ON_DEATH_OR_ESCAPE]

    def __init__(self, host, amount=0):
        super().__init__(
            host,
            "Split",
            StackType.NONE,
            EffectType.BUFF,
            "When activated, splits into two smaller enemies.",
            amount=amount,
        )

    def callback(self, message, data: Player | Enemy):
        if message == Message.ON_DEATH_OR_ESCAPE:
            dead_entity = data
            if dead_entity != self.host:
                return
            print("Split effect activated")
            split_into = {
                "Slime Boss": (
                    Enemy(self.host.health, 0, "Acid Slime(L)"),
                    Enemy(self.host.health, 0, "Spike Slime (L)"),
                ),
                "Acid Slime (L)": (
                    Enemy(self.host.health, 0, "Acid Slime(M)"),
                    Enemy(self.host.health, 0, "Acid Slime(M)"),
                ),
                "Spike Slime (L)": (
                    Enemy(self.host.health, 0, "Spike Slime (M)"),
                    Enemy(self.host.health, 0, "Spike Slime (M)"),
                ),
            }
            if self.host.name in split_into:
                self.host.health = 0
                for new_enemy in split_into[self.host.name]:
                    new_enemy.health = self.host.max_health // 2

                    # enemies.append(new_enemy)
                # del enemies[enemies.index(enemy)]
                ansiprint(f"{self.name} split into 2 {split_into[self.name].name}s")


class Artifact(Effect):
    """Artifact is a buff that will negate the next Debuff on that unit.

    Each stack of Icon Artifact Artifact can block 1 application of a Debuff. For example:

    Bouncing Flask will remove 1 Icon Artifact Artifact with each bounce.
    Envenom will remove 1 Icon Artifact Artifact with each unblocked Attack damage.
    Shockwave and Crippling Cloud will remove up to 2 Icon Artifact Artifacts from each enemy, since they inflict 2 Debuffs.
    Effects that apply multiple Debuffs will do so in the order listed on the card. For instance, if an enemy has 1 Icon Artifact Artifact and is hit by Shockwave, the card will apply Icon Weak Weak then apply Icon Vulnerable Vulnerable as per its description, and the enemy will lose 1 Icon Artifact Artifact to negate Icon Weak Weak and only has Icon Vulnerable Vulnerable inflicted on it."""

    registers = [Message.BEFORE_APPLY_EFFECT]

    def __init__(self, host, amount=1):
        super().__init__(
            host,
            "Artifact",
            StackType.INTENSITY,
            EffectType.BUFF,
            "Negates the next Debuff on the target.",
            amount=amount,
        )

    def callback(self, message, data: tuple[Effect, Player, Player]):
        if message == Message.BEFORE_APPLY_EFFECT:
            print("Artifact effect activated")
            effect, target, user = data
            if effect.type == EffectType.DEBUFF and self.amount > 0:
                effect.unsubscribe()
                self.amount -= 1
                ansiprint(
                    f"{target.name} blocked {effect.name} with <buff>Artifact</buff>."
                )
                return False
            return True


class Asleep(Effect):
    # The Lagavulin will start with the unique debuff "Asleep", as well as a Icon Metallicize Metallicize buff, preventing it from taking any action, but granting it 8 Icon Block Block at the start of every turn. The Lagavulin will awake at the end of its 3rd turn or when any HP damage is taken through the Icon Block Block, and will lose its Icon Metallicize Metallicize buff in the process.
    # When the Lagavulin wakes up by being attacked, it will be stunned for one turn. If the Lagavulin is left unharmed for three turns, it will wake up on its own and begin the fourth turn unstunned.
    registers = [Message.START_OF_TURN, Message.ON_ATTACKED]

    def __init__(self, host: Enemy, amount=3):
        super().__init__(
            host,
            "Asleep",
            StackType.NONE,
            EffectType.DEBUFF,
            "Prevents the enemy from taking any action.",
            amount=amount,
        )

    def callback(self, message, data: Enemy):
        if message == Message.START_OF_TURN:
            if self.amount > 0:
                ei.apply_effect(self.host, None, Metallicize, 8)
        elif message == Message.ON_ATTACKED:
            target = data
            self.host.debuffs.append(Stunned(self.host, 1))


class Stunned(Effect):
    # Stunned is a debuff that prevents the target from taking any action for a certain number of turns.
    registers = [Message.AFTER_SET_INTENT]

    def __init__(self, host, amount=1):
        super().__init__(
            host,
            "Stunned",
            StackType.NONE,
            EffectType.DEBUFF,
            "Prevents the target from taking any action.",
            amount=amount,
        )

    def callback(self, message, data: Action):
        if message == Message.AFTER_SET_INTENT:
            print("TBD: Stunned Effect")


class Dexterity(Effect):
    # Dexterity is a buff that increases the amount of Block gained from cards.
    registers = [Message.BEFORE_BLOCK]

    def __init__(self, host, amount):
        super().__init__(
            host,
            "Dexterity",
            StackType.INTENSITY,
            EffectType.BUFF,
            "Increases the amount of Block gained from cards.",
            amount,
        )

    def callback(self, message, data: tuple[Player, Card]):
        if message == Message.BEFORE_BLOCK:
            player, card = data
            if card is not None:
                card.modify_block(
                    self.amount,
                    f"<buff>Dexterity</buff>({self.amount:+d} block)",
                    permanent=False,
                )


class SporeCloud(Effect):
    # On death, applies X Vulnerable to the player.
    registers = [Message.START_OF_COMBAT, Message.ON_DEATH_OR_ESCAPE]

    def __init__(self, host, amount=2):
        super().__init__(
            host,
            "Spore Cloud",
            StackType.NONE,
            EffectType.DEBUFF,
            f"On death, applies {amount} Vulnerable to the player.",
            amount=amount,
        )
        self.target = None

    def callback(self, message, data: tuple[Enemy, list[Enemy]]):
        if message == Message.START_OF_COMBAT:
            tier, enemies, player = data
            self.target = player
        elif message == Message.ON_DEATH_OR_ESCAPE:
            dead_entity = data
            if dead_entity == self.host and self.target is not None:
                ei.apply_effect(target=self.target, user=None, effect=Vulnerable, amount=self.amount)


class Thievery(Effect):
    # X Gold is stolen with every attack. Total Gold stolen is returned if the enemy is killed.
    registers = [Message.AFTER_ATTACK, Message.ON_DEATH_OR_ESCAPE]

    def __init__(self, host, amount=15):
        super().__init__(
            host,
            "Thievery",
            StackType.NONE,
            EffectType.DEBUFF,
            "X Gold is stolen with every attack. Total Gold stolen is returned if the enemy is killed.",
            amount=amount,
        )
        self.stolen_gold = 0

    def callback(self, message, data: tuple[Player, int] | tuple[Enemy, list[Enemy]]):
        if message == Message.AFTER_ATTACK:
            attacker, target, dmg = data
            if attacker == self.host:
                target.gold -= self.amount
                self.stolen_gold += self.amount
                ansiprint(
                    f"{attacker.name} stole {self.amount} gold from {target.name}."
                )
        elif message == Message.ON_DEATH_OR_ESCAPE:
            player, enemies, dead_entity = data
            if dead_entity == self.host:
                player.gold += self.stolen_gold
                ansiprint(
                    f"{player.name} received {self.stolen_gold} gold from {self.host.name}."
                )


class Angry(Effect):
    # Increases Strength by X when taking attack damage.
    registers = [Message.AFTER_ATTACK]

    def __init__(self, host, amount=1):
        super().__init__(
            host,
            "Angry",
            StackType.INTENSITY,
            EffectType.BUFF,
            "Increases Strength by X when taking attack damage.",
            amount=amount,
        )

    def callback(self, message, data: tuple[Player, Enemy, int]):
        if message == Message.AFTER_ATTACK:
            attacker, target, dmg = data
            if target == self.host and dmg > 0:
                ei.apply_effect(self.host, None, Strength, self.amount)


class Duplication(Effect):
    # "This turn, your next (1-2) cards are played twice.",
    registers = [Message.ON_CARD_PLAY]

    def __init__(self, host, amount=1):
        super().__init__(
            host,
            "Duplication",
            StackType.NONE,
            EffectType.BUFF,
            "This turn, your next card is played twice.",
            amount=amount,
        )

    def callback(self, message, data: tuple[Player, Card, Enemy, list[Enemy]]):
        if message == Message.ON_CARD_PLAY:
            player, card, target, enemies = data
            if self.amount > 0:
                self.amount -= 1
                player.use_card(card=card, exhaust=False, target=target, pile=None, enemies=enemies)

