
from rules import card_by_name, SLOTS, LEFT_APP, RIGHT_APP
from game import Game


__all__ = [
    'Bot',
    'GameTrackingBot',
    'IdleBot',
    'InteractiveBot',
]


class Bot(object):
    def begin_game(self, your_number):
        assert your_number in range(2)
        self.number = your_number
        
    def end_game(self):
        pass
        
    def receive_move(self, dir, slot, card):
        raise NotImplementedError()
    
    def make_move(self):
        'return tuple (dir, slot, card_name)'
        raise NotImplementedError()
    
    
class IdleBot(Bot):
    def make_move(self):
        return (LEFT_APP, 0, 'I')

    def receive_move(self, *move):
        pass


class GameTrackingBot(Bot):
    def begin_game(self, your_number):
        Bot.begin_game(self, your_number)
        self.game = Game()
        
    def receive_move(self, *move):
        assert self.game.half_moves % 2 == 1 - self.number
        self.game.make_half_move(*move)
        
    def make_move(self):
        assert self.game.half_moves % 2 == self.number
        move = self.choose_move()
        self.game.make_half_move(*move)
        return move
    
    def choose_move(self):
        raise NotImplementedError()
        
        
class InteractiveBot(GameTrackingBot):
    def __init__(self, bot_io):
        self.io = bot_io

    def begin_game(self, your_number):
        super(InteractiveBot, self).begin_game(your_number)
        self.io.notify_begin_game(self)
        
    def receive_move(self, *move):
        self.io.notify_opp_move(self, move)
        super(InteractiveBot, self).receive_move(*move)  
       
    def choose_move(self):
        self.io.dump_game(self, self.game)
        direction, slot, card = self.io.read_move()
        return (direction, slot, card)

