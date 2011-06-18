
import copy

from rules import cards, MAX_SLOT, SLOTS, LEFT_APP, RIGHT_APP


__all__ = [
          'Strategy',
          'IdleStrategy',
          'GenerateValueStrategy',
          'SequenceStrategy',
          'ApplicationSequenceStrategy',
          'RepeatStrategy',
          'AppNTo0Strategy',
          'AppFIJNStrategy',
          'BoostBattery',
          'AttackSlot',
          'DumbSlotKiller',
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
    
    def pop_move(self, game):
        '''return tuple (dir, slot, card_name)'''
        raise NotImplementedError()


class NoneStrategy(Strategy):
    def minimum_slots(self):
        return 0

    def available_moves(self):
        return 100500

    def current_priority(self):
        return 0
    
    def pop_move(self, game):
        return None


class IdleStrategy(Strategy):
    def minimum_slots(self):
        return 0

    def available_moves(self):
        return 100500

    def current_priority(self):
        return 0
    
    def pop_move(self, game):
        return LEFT_APP, 0, cards.I


class GenerateValueStrategy(Strategy):
    def __init__(self, slot = 0, target = 0):
        self.target = target
        self.intermediate_targets = [target]
        while target > 1:
            target = target / 2
            self.intermediate_targets.append(target)
        self.slot = slot
        self.slot_value = 0
        self.inited = False
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

    def pop_move(self, game):
        #self.turns = self.turns - 1
        if not self.inited:
            self.inited = True
            return (LEFT_APP, self.slot, cards.put)
        elif not self.zeroed:
            self.zeroed = True
            return (RIGHT_APP, self.slot, cards.zero)
        elif self.target == self.slot_value:
            return None
        elif self.slot_value == 0:
            self.slot_value = self.slot_value + 1
            return (LEFT_APP, self.slot, cards.succ)
        else:
            cur_target = self.intermediate_targets.pop()
            if cur_target == self.slot_value:
                self.slot_value = self.slot_value * 2
                return (LEFT_APP, self.slot, cards.dbl)
            else:
                self.intermediate_targets.append(cur_target)
                self.slot_value = self.slot_value + 1
                return (LEFT_APP, self.slot, cards.succ)


class SequenceStrategy(Strategy):
    def __init__(self, *args):
        self.strategies = args

    def minimum_slots(self):
        return reduce(lambda x, y: x + y.minimum_slots(), self.strategies, 0)

    def available_moves(self):
        return reduce(lambda x, y: x + y.available_moves(), self.strategies, 0)

    def current_priority(self):
        return 0
    
    def pop_move(self, game):
        for strategy in self.strategies:
            move = strategy.pop_move(game)
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
    
    def pop_move(self, game):
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
    
    def pop_move(self, game):
        move = self.cur_strategy.pop_move(game)
        if move == None:
            self.n = self.n - 1
            if self.n <= 0:
                self.n = 0
                return None
            else:
                self.cur_strategy = copy.deepcopy(self.strategy)
                move = self.cur_strategy.pop_move(game)
        return move


class GetIStrategy(SequenceStrategy):
    def __init__(self, slot, i_slot):
        self.slot = slot
        self.i_slot = i_slot
        self.strategies = [
                           ApplicationSequenceStrategy((LEFT_APP, self.slot, cards.put),
                                                       (RIGHT_APP, self.slot, cards.zero),
                                                      ),
                           RepeatStrategy(n = self.i_slot, strategy = ApplicationSequenceStrategy((LEFT_APP, self.slot, cards.succ))),
                           ApplicationSequenceStrategy((LEFT_APP, self.slot, cards.get),
                                                      ),
                          ]


# Vlad Shcherbina: found [0 r, Succ l, Succ l, get l, K l, S l, get r, 0 r] -> ((get 2) (get 0))
# Vlad Shcherbina: found [0 r, Succ l, Succ l, Succ l, get l, K l, S l, get r, 0 r] -> ((get 3) (get 0))
class AppNTo0Strategy(SequenceStrategy):
    def __init__(self, slot, n_slot):
        self.slot = slot
        self.n_slot = n_slot
        self.strategies = [
                           ApplicationSequenceStrategy((LEFT_APP, self.slot, cards.put),
                                                       (RIGHT_APP, self.slot, cards.zero),
                                                      ),
                           RepeatStrategy(n = self.n_slot, strategy = ApplicationSequenceStrategy((LEFT_APP, self.slot, cards.succ))),
                           ApplicationSequenceStrategy((LEFT_APP, self.slot, cards.get),
                                                       (LEFT_APP, self.slot, cards.K),
                                                       (LEFT_APP, self.slot, cards.S),
                                                       (RIGHT_APP, self.slot, cards.get),
                                                       (RIGHT_APP, self.slot, cards.zero),
                                                      ),
                          ]


class AppFIJNStrategy(SequenceStrategy):
    def __init__(self, slot, f_card, i_num, j_num, n_num):
        self.slot = slot
        self.interm_slot = 1
        self.f_card = f_card
        self.i_num = i_num
        self.j_num = j_num
        self.n_num = n_num
        self.strategies = [
                           ApplicationSequenceStrategy((LEFT_APP, self.interm_slot, cards.put),
                                                       (RIGHT_APP, self.interm_slot, self.f_card),
                                                      ),
                           GenerateValueStrategy(slot = 0, target = self.i_num),
                           AppNTo0Strategy(slot = self.slot, n_slot = self.interm_slot),
                           GetIStrategy(slot = self.interm_slot, i_slot = self.slot),
                           GenerateValueStrategy(slot = 0, target = self.j_num),
                           AppNTo0Strategy(slot = self.slot, n_slot = self.interm_slot),
                           GetIStrategy(slot = self.interm_slot, i_slot = self.slot),
                           GenerateValueStrategy(slot = 0, target = self.n_num),
                           AppNTo0Strategy(slot = self.slot, n_slot = self.interm_slot),
                          ]

class BoostBattery(AppFIJNStrategy):
    def __init__(self, battery_slot, boost):
        super(BoostBattery, self).__init__(battery_slot, cards.help, battery_slot, battery_slot, boost)

class AttackSlot(AppFIJNStrategy):
    def __init__(self, battery_slot, target_slot, dmg):
        super(AttackSlot, self).__init__(battery_slot, cards.attack, battery_slot, (MAX_SLOT - target_slot), dmg)

class DumbSlotKiller(Strategy):
    def __init__(self, battery_slot, target_slot):
        self.battery_slot = battery_slot
        self.target_slot = target_slot
        self.cur_strategy = None

    def available_moves(self):
        return 1

    def current_priority(self):
        return 0
    
    def pop_move(self, game):
        if self.cur_strategy == None:
            self.pick_strategy(game)
            return self.cur_strategy.pop_move(game)
        else:
            move = self.cur_strategy.pop_move(game)
            if move == None:
                self.cur_strategy = None
                return self.pop_move(game)
            else:
                return move

    def pick_strategy(self, game):
        if game.opponent.vitalities[self.target_slot] <= 0:
            self.cur_strategy = NoneStrategy()
        elif game.proponent.vitalities[self.battery_slot] < 60000:
            self.cur_strategy = BoostBattery(battery_slot = self.battery_slot,
                                             boost = game.proponent.vitalities[self.battery_slot] - 1
                                            )
        else:
            self.cur_strategy = AttackSlot(battery_slot = self.battery_slot,
                                           target_slot = self.target_slot,
                                           dmg = min(game.opponent.vitalities[self.target_slot] * 10 / 9 + 1, game.proponent.vitalities[self.battery_slot] / 2)
                                          )
            

