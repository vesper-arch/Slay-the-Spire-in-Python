from __future__ import annotations

from ansi_tags import ansiprint
from definitions import (
    EffectType,
)
from message_bus_tools import bus


def apply_effect(target, user, effect, amount=0, recursion_tag=False) -> None:
    """recurstion_tag is only meant for internal use to stop infinite loops with Champion Belt."""
    # HACK HACK HACK Dynamically search for the effect class if it's a string. This is icky and should be avoided.
    if isinstance(effect, str) and effect in globals():
        effect = globals()[effect]
    from effects import Effect
    assert isinstance(
        effect, type(Effect)
    ), f"Effect must be an Effect class. You passed {effect} (type: {type(effect)})."
    current_relic_pool = (
        [relic.name for relic in user.relics]
        if getattr(user, "player_class", "placehold") in str(user)
        else []
    )
    effect = effect(target, amount)
    effect_type = EffectType.DEBUFF if effect.amount < 0 else effect.type
    if str(user) == "Player" and effect in ("Weak", "Frail"):
        if "Turnip" in current_relic_pool and effect.name == "Frail":
            ansiprint(
                "<debuff>Frail</debuff> was blocked by your <bold>Turnip</bold>."
            )
        elif "Ginger" in current_relic_pool and effect.name == "Weak":
            ansiprint("<debuff>Weak</debuff> was blocked by <bold>Ginger</bold>")
        return
    if (
        effect_type == EffectType.DEBUFF and "Artifact" in current_relic_pool
    ):  # TODO: Make Artifact buff.
        subject = getattr(target, "third_person_ref", "Your")
        ansiprint(
            f"<debuff>{effect.name}</debuff> was blocked by {subject} <buff>Artifact</buff>."
        )
    else:
        effect.register(bus)
        if effect_type == EffectType.DEBUFF:
            target.debuffs.append(effect)
            target.debuffs = merge_duplicates(target.debuffs)
        else:
            target.buffs.append(effect)
            target.buffs = merge_duplicates(target.buffs)

        if "Player" in str(target) and user is None:
            # If the player applied an effect to themselves
            ansiprint(f"You gained {effect.get_name()}")
        elif ("Enemy" in str(target) and user is None) or (
            target == user and "Enemy" in str(target)
        ):
            # If the enemy applied an effect to itself
            ansiprint(f"{target.name} gained {effect.get_name()}")
        elif "Enemy" in str(user) and "Player" in str(target):
            # If the enemy applied an effect to you
            ansiprint(f"{user.name} applied {effect.get_name()} to you.")
        elif "Player" in str(user) and "Enemy" in str(target):
            # If the player applied an effect to the enemy
            ansiprint(f"You applied {effect.get_name()} to {target.name}")
        elif "Enemy" in str(user) and "Enemy" in str(target) and user != target:
            # If the enemy applied an effect to another enemy
            ansiprint(f"{user.name} applied {effect.get_name()} to {target.name}.")

        if (
            "Champion Belt" in current_relic_pool
            and "Player" in str(user)
            and not recursion_tag
        ):
            apply_effect(target, user, "Weak", 1, True)
        if "Enemy" in str(user) and hasattr(target, "fresh_effects"):
            target.fresh_effects.append(effect)

def tick_effects(subject):
    for buff in subject.buffs:
        buff.tick()
    for debuff in subject.debuffs:
        debuff.tick()

    def clean(effect):
        if effect.amount >= 1:
            return True
        else:
            effect.unsubscribe()
            return False

    subject.buffs = list(filter(clean, subject.buffs))
    subject.debuffs = list(filter(clean, subject.debuffs))

def merge_duplicates(effect_list):
    # Thank you Claude Sonnet
    result = []
    seen = {}

    for effect in effect_list:
        if effect.name in seen:
            seen[effect.name] += effect
        else:
            seen[effect.name] = effect
            result.append(effect)

    return [seen[effect.name] for effect in result]

def full_view(entity, enemies):
    ansiprint(f"<bold>{entity.name}</bold>")
    for effect in entity.buffs + entity.debuffs:
        ansiprint(effect.pretty_print())
    for enemy in enemies:
        ansiprint(f"<bold>{enemy.name}</bold>:")
        for effect in enemy.buffs + enemy.debuffs:
            ansiprint(effect.pretty_print())
