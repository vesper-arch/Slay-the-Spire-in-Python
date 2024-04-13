import copy
from enum import StrEnum, auto


# Convienience classes so I don't have to deepcopy every time I want to get a card.
class DeepCopyList(list):
    def __getitem__(self, index):
        item = super().__getitem__(index)
        return copy.deepcopy(item)

class DeepCopyTuple(tuple):
    def __getitem__(self, index):
        item = super().__getitem__(index)
        return copy.deepcopy(item)

class CombatTier(StrEnum):
    NORMAL = 'Normal'
    ELITE = 'Elite'
    BOSS = 'Boss'

class EncounterType(StrEnum):
    START = auto()
    NORMAL = auto()
    ELITE = auto()
    REST_SITE = auto()
    BOSS = auto()
    SHOP = auto()
    UNKNOWN = auto()

class Rarity(StrEnum):
    BASIC = 'Basic'
    STARTER = 'Starter'
    COMMON = 'Common'
    UNCOMMON = 'Uncommon'
    RARE = 'Rare'
    SPECIAL = 'Special'
    CURSE = 'Curse'
    STATUS = 'Status'
    BOSS = 'Boss'
    EVENT = 'Event'
    SHOP = 'Shop'

class CardType(StrEnum):
    ATTACK = 'Attack'
    SKILL = 'Skill'
    POWER = 'Power'
    CURSE = 'Curse'
    STATUS = 'Status'

class PlayerClass(StrEnum):
    IRONCLAD = 'Ironclad'
    SILENT = 'Silent'
    DEFECT = 'Defect'
    WATCHER = 'Watcher'
    COLORLESS = 'Colorless'
    ANY = 'Any'

class TargetType(StrEnum):
    ANY = 'Any'
    AREA = 'Area' # Also use for cards that target a random enemy
    ENEMY = 'Enemy' # Only for use in enemy moves when the enemy targets another enemy
    NOTHING = 'Nothing'
    SINGLE = 'Single'
    YOURSELF = 'Yourself'

class CardCategory(StrEnum):
    CARD = 'Card'
    POTION = 'Potion'
    RELIC = 'Relic'

class State(StrEnum):
    ALIVE = 'alive'
    DEAD = 'dead'
    ESCAPED = 'escaped'
    INTANGIBLE = 'intangible' # Enemies that revive have a period where they cannot be attacked and have no intent.

class StackType(StrEnum):
    DURATION = 'duration'
    INTENSITY = 'intensity'
    COUNTER = 'counter'
    NONE = 'none'
    DURATION_AND_INTENSITY = 'Duration and Intensity'

class EffectType(StrEnum):
    DEBUFF = 'debuff'
    BUFF = 'buff'
