
import copy

from rules import *

__all__ = [
    'Strategy',
    'GenerateValueStrategy',
    'SequenceStrategy',
    'AppNTo0Strategy',
]

class Strategy(object):
    def minimum_slots(self):
        '''return minimum number of own slots this stratety requires'''
        return 0

    def activate(self, slots):
        ''' slots is a set with available free slots indexes '''
        self.slots = list(slots)
        
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
    def __init__(self, slot = 0, target = 0):
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
            return (RIGHT_APP, self.slot, card.zero)
        elif self.slot_value == 0:
            self.slot_value = self.slot_value + 1
            return (LEFT_APP, self.slot, card.succ)
        else:
            cur_target = self.intermediate_targets.pop()
            if cur_target == self.slot_value:
                self.slot_value = self.slot_value * 2
                return (LEFT_APP, self.slot, card.dbl)
            else:
                self.intermediate_targets.append(cur_target)
                self.slot_value = self.slot_value + 1
                return (LEFT_APP, self.slot, card.succ)

class SequenceStrategy(Strategy):
    def __init__(self, *args):
        self.strategies = args

    def minimum_slots(self):
        return reduce(lambda x, y: x + y.minimum_slots(), self.strategies, 0)

    def available_moves(self):
        return reduce(lambda x, y: x + y.available_moves(), self.strategies, 0)

    def current_priority(self):
        return 0
    
    def pop_move(self):
        for strategy in self.strategies:
            move = strategy.pop_move()
            if move != None:
                return move
        return None

class ApplicationSequenceStrategy(Strategy):
    def __init__(self, *args):
        self.apps = []
        for app in args:
            self.apps.insert(0, app)

    def minimum_slots(self):
        return 1

    def available_moves(self):
        return len(self.apps)

    def current_priority(self):
        return 0
    
    def pop_move(self):
        if len(self.apps) == 0:
            return None
        else:
            return self.apps.pop()

class RepeatStrategy(Strategy):
    def __init__(self, n, strategy):
        self.n = n
        self.strategy = strategy
        self.cur_strategy = copy.deepcopy(self.strategy)

    def minimum_slots(self):
        return self.cur_strategy.minimum_slots()

    def available_moves(self):
        return 1

    def current_priority(self):
        return 0
    
    def pop_move(self):
        move = self.cur_strategy.pop_move()
        if move == None:
            self.n = self.n - 1
            if self.n <= 0:
                self.n = 0
                return None
            else:
                self.cur_strategy = copy.deepcopy(self.strategy)
                move = self.cur_strategy.pop_move()
        return move

# Vlad Shcherbina: found [0 r, Succ l, Succ l, get l, K l, S l, get r, 0 r] -> ((get 2) (get 0))
# Vlad Shcherbina: found [0 r, Succ l, Succ l, Succ l, get l, K l, S l, get r, 0 r] -> ((get 3) (get 0))
class AppNTo0Strategy(SequenceStrategy):
    def __init__(self, slot, n_slot):
        self.slot = slot
        self.n_slot = n_slot
        self.strategies = [
                           ApplicationSequenceStrategy((RIGHT_APP, self.slot, card.zero)),
                           RepeatStrategy(n = self.n_slot, strategy = ApplicationSequenceStrategy((LEFT_APP, self.slot, card.succ))),
                           ApplicationSequenceStrategy((LEFT_APP, self.slot, card.get),
                                                       (LEFT_APP, self.slot, card.K),
                                                       (LEFT_APP, self.slot, card.S),
                                                       (RIGHT_APP, self.slot, card.get),
                                                       (RIGHT_APP, self.slot, card.zero)),
                          ]

