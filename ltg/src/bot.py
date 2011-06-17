
from rules import card, card_by_name, SLOTS, LEFT_APP, RIGHT_APP
from game import Game


__all__ = [
    'Bot',
    'IdleBot',
    'InteractiveBot',
]


class Bot(object):
    def begin_game(self, game, your_number):
        assert your_number in range(2)
        self.number = your_number
        self.game = game
        
    def end_game(self):
        pass
        
    def receive_move(self, dir, slot, card):
        raise NotImplementedError()
    
    def make_move(self):
        'return tuple (dir, slot, card_name)'
        raise NotImplementedError()
    
    
class IdleBot(Bot):
    def make_move(self):
        return (LEFT_APP, 0, card.I)

    def receive_move(self, *move):
        pass


class InteractiveBot(Bot):
    def __init__(self, bot_io):
        self.io = bot_io

    def begin_game(self, game, your_number):
        super(InteractiveBot, self).begin_game(game, your_number)
        self.io.notify_begin_game(self)
        
    def receive_move(self, *move):
        self.io.notify_opp_move(self, move)

    def make_move(self):
        move = self.choose_move()
        return move 

    def choose_move(self):
        self.io.dump_game(self)
        direction, slot, card = self.io.read_move()
        return (direction, slot, card)

