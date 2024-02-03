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
