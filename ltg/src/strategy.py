from rules import *

__all__ = [
    'Strategy',
    'GenerateValueStrategy',
    'SequenceStrategy',
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
        self.intermediate_targets = [target]
        while target > 1:
            target = target / 2
            self.intermediate_targets.append(target)
        self.slot = slot
        self.slot_value = 0
        self.zeroed = False
        #self.turns = target + 1

    def minimum_slots(self):
        return 1

    def available_moves(self):
        if self.target == self.slot_value:
            return 0
        else:
            return 1

    def current_priority(self):
        return 0

    def pop_move(self):
        #self.turns = self.turns - 1
        if self.target == self.slot_value:
            return None
        elif not self.zeroed:
            self.zeroed = True
            return (RIGHT_APP, self.slot, 'zero')
        elif self.slot_value == 0:
            self.slot_value = self.slot_value + 1
            return (LEFT_APP, self.slot, 'succ')
        else:
            cur_target = self.intermediate_targets.pop()
            if cur_target == self.slot_value:
                self.slot_value = self.slot_value * 2
                return (LEFT_APP, self.slot, 'dbl')
            else:
                self.intermediate_targets.append(cur_target)
                self.slot_value = self.slot_value + 1
                return (LEFT_APP, self.slot, 'succ')

class SequenceStrategy(Strategy):
    def __init__(self, *args):
        self.strategies = args

    def minimum_slots(self):
        return reduce(lambda x, y: x.minimum_slots() + y.minimum_slots(), self.strategies)

    def available_moves(self):
        return reduce(lambda x, y: x.available_moves() + y.available_moves(), self.strategies)

    def current_priority(self):
        return 0
    
    def pop_move(self):
        for strategy in self.strategies:
            move = strategy.pop_move()
            if move != None:
                return move
        return None

