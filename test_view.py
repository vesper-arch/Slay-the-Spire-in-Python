import helper
import items
import entities

def test_view_piles_on_all_cards(monkeypatch):
  all_cards = [card for card in items.cards.values()]
  entity = entities.create_player()
  entity.energy = 3
  all_conditions = [(lambda card: card.get("Upgraded") is True, "Upgraded"), (lambda card: not card.get("Upgraded") and (card['Type'] not in ("Status", "Curse") or card['Name'] == 'Burn'), "Upgradeable"),
                    (lambda card: card.get("Removable") is False, "Removable"), (lambda card: card['Type'] == 'Skill', "Skill"), (lambda card: card['Type'] == 'Attack', "Attack"), (lambda card: card['Type'] == 'Power', "Power"), 
                    (lambda card: card.get("Energy", float('inf')) <= entity.energy, "Playable")]

  with monkeypatch.context() as m:
    # Patch sleeps so it's faster
    m.setattr(helper, 'sleep', lambda x: None)
    m.setattr(entities, 'sleep', lambda x: None)

    for function, condition_name in all_conditions:
      print(f"===== Condition: {condition_name} ======")
      helper.view.view_piles(pile=all_cards, entity=entity, end=False, validator=function)

    # Also test the default condition
    print(f"===== Condition: Default ======")
    helper.view.view_piles(pile=all_cards, entity=entity, end=False)

