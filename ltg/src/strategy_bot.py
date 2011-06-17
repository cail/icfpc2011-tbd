from game import Game
from rules import card_by_name, SLOTS
from bot import GameTrackingBot

__all__ = [
    'StrategyBot',
]

class StrategyBot(GameTrackingBot):
    '''
    This bot is only a proxy to real strategies, hosted inside of it.
    Each strategy have access to the game state and may decide on how to handle it
    Either activate and provide some moves, or wait for a better time
    '''

    def __init__(self):
        self.strategies = []
    def begin_game(self, your_number):
        super(StrategyBot, self).begin_game(your_number)

    def receive_move(self, *move):
        super(StrategyBot, self).receive_move(*move)  

    def choose_move(self):
        print self.game
        choosen_one = self.strategies[0]
        if choosen_one.available_moves() > 0:
            chosen_move = choosen_one.pop_move()
            print chosen_move
            return chosen_move
        else:
            return (1, 0, 'I')

    def acquire_slots(self, slots_count):
        # TODO: fix this
        slots = set()
        for i in range(0, slots_count):
            slots.add(i)
        return slots

    def add_strategy(self, strategy):
        self.strategies.append(strategy)
        strategy.activate(self.acquire_slots(strategy.minimum_slots()))
