import helper
import entities

def test_view_piles_on_all_cards(monkeypatch):
  all_cards = [card for card in entities.cards.values()]
  entity = entities.create_player()
  entity.energy = 3
  all_conditions = ['Upgraded' ,'Upgradable' ,'Removable' ,'Skill' ,'Attack' ,'Power' ,'Playable']

  with monkeypatch.context() as m:
    # Patch sleeps so it's faster
    # m.setattr(helper, 'sleep', lambda x: None)
    # m.setattr(entities, 'sleep', lambda x: None)

    for condition in all_conditions:
      print(f"===== Condition: {condition} ======")
      helper.view.view_piles(pile=all_cards, entity=entity, end=False, condition=condition)

