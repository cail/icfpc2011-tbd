
from rules import card, LEFT_APP, RIGHT_APP
from bot import Bot


__all__ = [
          'StrategyBot',
          ]


class StrategyBot(Bot):
    '''
    This bot is only a proxy to real strategies, hosted inside of it.
    Each strategy have access to the game state and may decide on how to handle it
    Either activate and provide some moves, or wait for a better time
    '''

    def __init__(self, bot_io):
        super(StrategyBot, self).__init__(bot_io = bot_io)
        self.strategies = []

    def receive_move_impl(self, *move):
        pass

    def make_move_impl(self):
        choosen_one = self.strategies[0]
        if choosen_one.available_moves() > 0:
            chosen_move = choosen_one.pop_move()
            return chosen_move
        else:
            return (LEFT_APP, 0, card.I)

    def acquire_slots(self, slots_count):
        # TODO: fix this
        slots = set()
        for i in range(0, slots_count):
            slots.add(i)
        return slots

    def add_strategy(self, strategy):
        self.strategies.append(strategy)
        strategy.activate(self.acquire_slots(strategy.minimum_slots()))

