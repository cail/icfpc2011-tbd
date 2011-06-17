from rules import *

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
    def __init__(self, target, slot = 0):
        self.target = target
        self.slot = slot
        self.slot_value = 0
        self.zeroed = False
        #self.turns = target + 1

    def minimum_slots(self):
        return 1

    def available_moves(self):
        return 1

    def current_priority(self):
        return 0

    def pop_move(self):
        #self.turns = self.turns - 1

        if not self.zeroed:
            self.zeroed = True
            return (RIGHT_APP, self.slot, 'zero')
        elif (self.slot_value > 0) and (self.slot_value <= (self.target / 2)):
            self.slot_value = self.slot_value * 2
            return (LEFT_APP, self.slot, 'dbl')
        elif self.slot_value < self.target:
            self.slot_value = self.slot_value + 1
            return (LEFT_APP, self.slot, 'succ')
        else:
            return None
