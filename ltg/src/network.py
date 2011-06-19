from pprint import pprint
import sys
from copy import copy
from collections import defaultdict
import random

from terms import number_term, optimal_subterm, replace_leaf_subterm,\
    sequential_cost, subterms, term_to_sequence, is_subterm_eager,\
    fold_numbers, calc_costs_and_weights, value_to_term, unfold_numbers
import rules
from rules import cards
from game import Game


FAIL = '0-FAIL'
WAIT = '1-WAIT'
OK = '2-OK  '
RUNNING = '*-RUN '
# for comparisons like FAIL < OK


    
            
class Goal(object):
    def __init__(self, term, slot=None):
        self.term = term
        self.slot = slot
        self.gets = set()
        self.lazy_gets = set()
        
    def clone(self):
        result = Goal(self.term, self.slot)
        result.gets = copy(self.gets)
        result.lazy_gets = copy(self.lazy_gets)
        return result
    
    def __str__(self):
        result = 'Goal(term={0}, slot={1}) of cost {2}'.\
            format(fold_numbers(self.term), self.slot,
                   self.cost())
        if self.gets:
            result += ', depends on {0}'.format(list(self.gets))
        if self.lazy_gets:
            result += ', lazily depends on {0}'.format(self.lazy_gets)
        return result
    
    def name(self):
        return 'Goal@{0}'.format(self.slot)
    
    def cost(self):
        return sequential_cost(self.term)
    
    def get_moves(self, game):
        result = []
        
        if game.proponent.values[self.slot] != cards.I: # clear slot
            result.append(('l', self.slot, cards.put))
            
        for card, side in term_to_sequence(self.term):
            result.append((side, self.slot, card))
        return result
    
    def introduce_get(self, sub_term, register_access):
        g, register_slot = fold_numbers(register_access)
        assert isinstance(register_slot, int)
        assert g == cards.get
        
        self.gets.add(register_slot)
        
        if not is_subterm_eager(sub_term, self.term):
            self.lazy_gets.add(register_slot)
        self.term = replace_leaf_subterm(sub_term, register_access, self.term)


slot_numbers_by_reachability = sorted(
    range(rules.SLOTS), 
    key=lambda n: sequential_cost(number_term(n)))


class NetworkFail(Exception):
    pass


def global_optimize_network(network):
    best = None
    best_cost = 1e100
    orig = str(network)
    for reg_count in [1]+[3]*5:
        assert str(network) == orig
        t = network.clone()
        t.reg_count = reg_count
        t.refine()
        cost = t.cost()
        if cost < best_cost:
            best = t
            best_cost = cost
        if network.game.total_time_left < 1000 or network.game.turn_time_left < 10:
            break
        
    return best


class Network(object):
    def __init__(self, game):
        self.goals = []
        self.game = game
        self.petrified_slots = set() # for lazy terms
        
        self.slot_goals = defaultdict(set)
        
        self.instructions = []
        self.current_goal = None
        self.next_move = None
        self.reg_count = 10
        
    def clone(self):
        result = Network(self.game)
        goal_map = dict((g, g.clone()) for g in self.goals)
        for g in self.goals:
            result.add_goal(goal_map[g])
            
        result.petrified_slots = copy(self.petrified_slots)

        result.instructions = self.instructions[:]
        if self.current_goal is not None:
            result.current_goal = goal_map[self.current_goal]
        result.next_move = self.next_move    
        return result

    def dont_touch(self, *slots):
        self.petrified_slots |= set(slots)

    def is_finished(self):
        return self.next_move is None

    def get_next_move(self):
        assert not self.is_finished()
        move = self.next_move
        self.next_move = self.pop_instruction()
        return move

    def begin(self):
        self.next_move = self.pop_instruction()
        
    
    def check(self):
        'raise NetworkError if something is wrong'
        need_alive = set()
        need_alive |= self.petrified_slots
        for goal in self.goals:
            need_alive.add(goal.slot)
            need_alive |= goal.gets
        prop = self.game.proponent
        for slot in need_alive:
            if prop.vitalities[slot] <= 0:
                raise NetworkFail('slot {0} is dead'.format(slot))
        
    def refine(self):
        self.reuse_shit()
        self.allocate_registers()
        
    def add_goal(self, goal):
        self.slot_goals[goal.slot].add(goal)
        self.goals.append(goal)
        
    def remove_goal(self, goal):
        assert goal in self.slot_goals[goal.slot]
        self.slot_goals[goal.slot].remove(goal)
        self.goals.remove(goal)
        
    def __str__(self):
        result = 'Goals:\n'
        for goal in self.goals:
            result += '   {0} {1}\n'.format(self.goal_status(goal), goal)
        result += 'petrified slots: {0}\n'.format(self.petrified_slots)
        result += '({0} steps to construct)'.format(self.cost())
        return result
    
    
    def introduce_get(self, sub_term, register_access):
        for goal in self.goals:
            if not sub_term in subterms(goal.term):
                continue
            goal.introduce_get(sub_term, register_access)
            
                
    def reuse_shit(self):
        assert self.current_goal is None
        
        prop = self.game.proponent
        terms = [goal.term for goal in self.goals]
        costs, _ = calc_costs_and_weights(*terms)
        for slot in slot_numbers_by_reachability:
            if prop.vitalities[slot] <= 0:
                continue
            value = prop.values[slot]
            if value == cards.I:
                continue # for speed
            shit = value_to_term(value)
            shit = unfold_numbers(shit)
            if shit in costs:
                access = (cards.get, number_term(slot))
                if sequential_cost(access) < costs[shit]:
                    if self.is_slot_available(slot):
                        self.introduce_get(shit, access)
                del costs[shit]
        
                
    def allocate_register(self, register_slot):
        if not self.is_slot_available(register_slot):
            return False
        prop = self.game.proponent
        register_clean = str(prop.values[register_slot]) == 'I'
        
        terms = [goal.term for goal in self.goals]
        
        register_access = (cards.get, number_term(register_slot))
        register_cost = sequential_cost(register_access)
        sub_term, advantage = optimal_subterm(register_cost, *terms)
        
        if not register_clean:
            advantage -= 1
            # because we have to clean it up
        
        if advantage <= 0:
            return False
        
        sub_goal = Goal(sub_term, register_slot)
        
        self.introduce_get(sub_term, register_access)

        self.add_goal(sub_goal)
        
        return True
    
    def allocate_registers(self, regs=None):

        regs = []
        for reg in slot_numbers_by_reachability:
            if self.is_slot_available(reg):
                regs.append(reg)
                if len(regs) >= self.reg_count:
                    break
        regs.reverse()
        random.shuffle(regs)
        for slot in regs:
            self.allocate_register(slot)
        
    def cost(self):
        return sum(goal.cost() for goal in self.goals)
        
    def is_slot_available(self, slot_number):
        'alive and not used by other goal'
        prop = self.game.proponent
        if prop.vitalities[slot_number] <= 0:
            return False
        if slot_number in self.petrified_slots:
            return False
        if len(self.slot_goals[slot_number]) > 0:
            return False
        if any(slot_number in goal.gets for goal in self.goals):
            return False
        return True
    
    def goal_status(self, goal):
        if goal == self.current_goal:
            return RUNNING
        prop = self.game.proponent
        
        for slot in goal.gets:
            if len(self.slot_goals[slot]) > 0:
                return WAIT
        
        return OK

    def select_goal(self):
        assert self.goals
        
        status = {}
        
        for goal in self.goals:
            if self.goal_status(goal) == FAIL:
                raise NetworkFail('network failed because of {0}'.format(goal))
        #print status
        
        for goal in self.goals:
            if self.goal_status(goal) == OK:
                #print>>sys.stderr, 'selected', goal
                return goal
            
        assert set(status.values()) == set([WAIT])
        raise NetworkFail('network failed because all goals are waiting')
        
    def pop_instruction(self):
        while len(self.instructions) == 0:
            # previous goal achieved
            if self.current_goal is not None:
                self.remove_goal(self.current_goal)
            if len(self.goals) == 0:
                return None
            self.current_goal = self.select_goal()
            
            self.petrified_slots |= self.current_goal.lazy_gets
             
            self.instructions = self.current_goal.get_moves(self.game)
        return self.instructions.pop(0)
        
        
if __name__ == '__main__':
    game = Game(output_level=2)
    net = Network(game)
    t = ((cards.get, number_term(8)), (cards.get, number_term(15)))
    t = (t, ((cards.get, number_term(3)), (cards.get, number_term(255))))
    node = Goal(t, 100)
    net.add_goal(node)
    print net
    net.refine()
    print net
        
    def make_move():
        net.check()
        move = net.pop_instruction()
        print 'making move', move
        game.make_half_move(*move)
        game.make_half_move('l', 0, cards.I) #opponent is idle
        print game
        print net
            
    make_move()
    make_move()
    make_move()
    make_move()
      