from game import *

__all__ = [
    'Strategy',
    'GenerateValueStrategy',
]

class Strategy(object):
    def minimum_slots(self):
        '''return minimum number of own slots this stratety requires'''
        return 0

    def activate(self, slots):
        ''' slots is a set with available free slots indexes '''
        self.slots = list(slots)
        print self.slots
        
    def available_moves(self):
        '''return current number of moves, this strategy may already offer'''
        return 0

    def current_priority(self):
        '''estimated priority of this strategy. 0 - minimal, 100 - superextremeimportant'''
        return 0
    
    def pop_move(self):
        '''return tuple (dir, slot, card_name)'''
        raise NotImplementedError()


class GenerateValueStrategy(Strategy):
    def __init__(self, value):
        self.target = value
        self.turns = value+1
        self.zeroed = False

    def minimum_slots(self):
        return 1

    def available_moves(self):
        return self.turns-1

    def current_priority(self):
        return 0

    def pop_move(self):
        self.turns = self.turns - 1

        if not self.zeroed:
            self.zeroed = True
            return (RIGHT_APP, self.slots[0], 'zero')
        elif self.turns > 0:
            return (LEFT_APP, self.slots[0], 'succ')
        else:
            return None
