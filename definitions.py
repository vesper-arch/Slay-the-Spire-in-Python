from enum import StrEnum, auto


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

class EnemyState(StrEnum):
    ALIVE = 'alive'
    DEAD = 'dead'
    ESCAPED = 'escaped'
    INTANGIBLE = 'intangible' # Enemies that revive have a period where they cannot be attacked and have no intent.
