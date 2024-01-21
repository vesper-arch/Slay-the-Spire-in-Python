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
    UNKNOWN = auto()