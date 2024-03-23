# game_map.py
from __future__ import annotations

import random
from enum import StrEnum, auto
from typing import List

from grandalf.graphs import Edge, Graph, Vertex

from dagascii import draw
from definitions import EncounterType


class MapError(Exception):
  pass


class Encounter():
  def __init__(self, type: EncounterType, children: List[Encounter] = None, parents: List[Encounter] = None, name=None, selected=False):
    self.type = type
    self.children = children or []
    self.parents = parents or []
    self.add_self_to_parents()
    self.name = name  # unsure if this is needed
    self.selected = selected

  def add_self_to_parents(self):
    for parent in self.parents:
      if self not in parent.children:
        parent.children.append(self)

  def get_edges(self):
    return [(self, child) for child in self.children]

  def __repr__(self):
    if self.selected:
      return f"--> {self.type.upper()} <--"
    else:
      return f"{self.type.upper()}"


class GameMap():
    def __init__(self, start_node):
        self.current_floor = 0
        self.current = start_node
        self.current.selected = True
        self.verts = self.recursive_get_verts(node=self.current)
        self.edges = self.recursive_get_edges(node=self.current)
        self.floor = 0  # can this be calculated dynamically?

    def recursive_get_verts(self, node, vertices=None):
        if vertices is None:
            vertices = set()
            vertices.add(node)
        for child in node.children:
            vertices.add(child)
            self.recursive_get_verts(child, vertices)
        return list(vertices)

    def recursive_get_edges(self, node, edges=None):
        DEBUG = False
        def debug_print(*args, **kwargs):
           if DEBUG:
              print(*args, **kwargs)
        debug_print(f"NODE: {node}")
        if edges is None:
            edges = []
        if len(node.children) == 0:
            debug_print(f"--> Node has no children, returning base case")
            return []
        for edge in node.get_edges():
            debug_print(f"  EDGE: {edge}")
            edges.append(edge)
            debug_print(f"  --> edges: {edges}")
            self.recursive_get_edges(edge[1], edges)
            debug_print(f"  --> Edges after recursion: {edges}")
        debug_print(f"--> Returning edges: {edges}")
        return edges

    def pretty_print(self):
      print()
      draw(self.verts,self.edges)

    def update_current(self, node):
      self.current.selected = False
      self.current = node
      self.current.selected = True

    def choice(self, choices):
      # Todo: move this to a helper function
      print()
      for idx, choice in enumerate(choices):
        print(f"{idx+1}: {choice}")
      while True:
        try:
          choice = int(input("Choose next encounter: "))
          if choice in range(1, len(choices)+1):
            break
          else:
             print(f"Choose between 1 and {len(choices)}")
        except ValueError:
          print("Invalid choice")
      return choices[choice-1]

    def __iter__(self):
      return self

    def __next__(self):
      if len(self.current.children) == 0:
        raise StopIteration
      else:
        next_node = self.choice(self.current.children)
        self.update_current(next_node)
        return self.current

    def __repr__(self):
      return f"GameMap | Current encounter: {self.current}"


def create_first_map():
    ET = EncounterType   # shorthard for readability

    # Build the map by connecting encounters
    start = Encounter(ET.START)

    F1a = Encounter(ET.NORMAL, parents=[start])
    F1b = Encounter(ET.SHOP, parents=[start])
    F1c = Encounter(ET.NORMAL, parents=[start])
    F1d = Encounter(ET.NORMAL, parents=[start])

    F2a = Encounter(ET.UNKNOWN, parents=[F1a, F1b])
    F2b = Encounter(ET.REST_SITE, parents=[F1c, F1d])

    F3a = Encounter(ET.ELITE, parents=[F2a, F2b])
    F3b = Encounter(ET.ELITE, parents=[F2a, F2b])

    F4a = Encounter(ET.NORMAL, parents=[F3a])
    F4b = Encounter(ET.NORMAL, parents=[F3a])
    F4c = Encounter(ET.NORMAL, parents=[F3b])
    F4d = Encounter(ET.NORMAL, parents=[F3b])

    boss = Encounter(ET.BOSS, parents=[F4a, F4b, F4c, F4d])

    return GameMap(start)
