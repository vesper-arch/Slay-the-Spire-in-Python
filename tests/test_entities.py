from entities import Enemy


def test_move_spam_check():
    enemy = Enemy([100,100],8,"enemy")
    enemy.past_moves = ['move1', 'move1', 'move1', 'move2', 'move2', 'move2']
    assert enemy.move_spam_check('move1', 3) is True  # only count recent moves
    assert enemy.move_spam_check('move2', 4) is True
    assert enemy.move_spam_check('move2', 3) is False
    assert enemy.move_spam_check('move2', 2) is False

def test_move_spam_check_small_list():
    enemy = Enemy([100,100],8,"enemy")
    enemy.past_moves = ['move1']
    assert enemy.move_spam_check('move2', 3) is True
    assert enemy.move_spam_check('move1', 3) is True
    assert enemy.move_spam_check('move1', 2) is True
    assert enemy.move_spam_check('move2', 1) is True
    assert enemy.move_spam_check('move1', 1) is False