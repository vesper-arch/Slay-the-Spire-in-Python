import random

import game_map
from ansi_tags import ansiprint
from combat import Combat
from definitions import CombatTier, EncounterType, State
from enemy import Enemy
from events import choose_event
from message_bus_tools import bus
from player import Player
from rest_site import RestSite
from shop import Shop


class Game:
    def __init__(self, seed=None):
        self.bus = bus
        self.bus.reset()
        if seed is not None:
            random.seed(seed)
        self.player = Player.create_player()
        self.game_map = game_map.create_first_map()
        Enemy.player = self.player
        self.current_encounter = None

    def start(self):
        self.game_map.pretty_print()
        for encounter in self.game_map:
            self.play(encounter, self.game_map)
            if self.player.state == State.DEAD:
                break
            self.player.floors += 1
            self.game_map.pretty_print()

    def play(self, encounter: game_map.Encounter, the_map: game_map.GameMap):
        if encounter.type == EncounterType.START:
            pass
        elif encounter.type == EncounterType.REST_SITE:
            return RestSite(self.player).rest_site()
        elif encounter.type == EncounterType.UNKNOWN:
            return self.unknown(self.game_map)
        elif encounter.type in (EncounterType.BOSS, EncounterType.ELITE, EncounterType.NORMAL):
            mapping = {
                EncounterType.BOSS: CombatTier.BOSS,
                EncounterType.ELITE: CombatTier.ELITE,
                EncounterType.NORMAL: CombatTier.NORMAL,
            }
            self.current_encounter = Combat(tier=mapping[encounter.type], player=self.player, game_map=self.game_map)
            retval = self.current_encounter.combat()
            self.current_encounter = None
            return retval
        elif encounter.type == EncounterType.SHOP:
            return Shop(self.player).loop()
        else:
            raise game_map.MapError(f"Encounter type {encounter.type} is not valid.")

    def unknown(self, game_map) -> None:
        # Chances
        normal_combat: float = 0.1
        treasure_room: float = 0.02
        merchant: float = 0.03
        random_number = random.random()

        if random_number < treasure_room:
            treasure_room = 0.02
            normal_combat += 0.1
            merchant += 0.03
        elif random_number < merchant:
            merchant = 0.03
            treasure_room += 0.02
            normal_combat += 0.1
        elif random_number < normal_combat:
            normal_combat = 0.1
            treasure_room += 0.02
            merchant += 0.03
            self.current_encounter = Combat(player=self.player, tier=CombatTier.NORMAL, game_map=self.game_map)
            retval = self.current_encounter.combat()
            self.current_encounter = None
            return retval
        else:
            # Chooses an event if nothing else is chosen
            ansiprint(self.player)
            chosen_event = choose_event(game_map, self.player)
            chosen_event()

    def pretty_print(self):
        print(f"{self.game_map.current.type}")
        if self.current_encounter:
            print(f"Current encounter: {self.current_encounter}")


