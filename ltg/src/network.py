from pprint import pprint
import sys
from copy import copy

from terms import number_term, optimal_subterm, replace_leaf_subterm,\
    sequential_cost, subterms, term_to_sequence
import rules
from rules import cards
from game import Game


FAIL = '0-FAIL'
WAIT = '1-WAIT'
OK = '2-OK  '
# for comparisons like FAIL < OK


  
            
class Requirement(object):
    def check(self, game):
        raise NotImplementedError()
    
    
class TermInSlotRequirement(Requirement):
    def __init__(self, term, slot):
        self.term = term
        self.slot = slot
        
    def check(self, game):
        prop = game.proponent
        if prop.vitalities[self.slot] <= 0:
            return FAIL
        #if value_to_term(prop.vitalities[self.slot]) == self.term:
        #    return OK
        return WAIT
    
    def __str__(self):
        term = str(self.term)
        if len(term) > 10:
            term = '...'
        return 'REQUIRES {0}@{1}'.format(term, self.slot)
    
            
class Goal(object):
    def __init__(self, term, slot=None):
        self.term = term
        self.slot = slot
        self.requirements = []
    
    def __str__(self):
        return 'Goal(term={0}, slot={1}) [{2}] of cost {3}'.\
            format(self.term, self.slot,
                   '; '.join(map(str, self.requirements)),
                   self.cost())
    
    def name(self):
        return 'Goal@{0}'.format(self.slot)
    
    def status(self, game):
        result = OK
        for req in self.requirements:
            result = min(result, req.check(game)) 
        return result
            
    def achieved(self, game):
        prop = game.proponent
        if prop.vitalities[self.slot] <= 0:
            return False
        return False
        return value_to_term(prop.vitalities[self.slot]) == self.term
    
    def cost(self):
        return sequential_cost(self.term)
    
    def get_moves(self):
        result = []
        for card, side in term_to_sequence(self.term):
            result.append((side, self.slot, card))
        return result


slot_numbers_by_reachability = sorted(
    range(rules.SLOTS), 
    key=lambda n: sequential_cost(number_term(n)))


class Network(object):
    def __init__(self, game):
        self.goals = []
        self.game = game
        self.eternal_requirements = [] # for lazy
        
    def clone(self):
        result = Network(self.game)
        result.goals = map(copy, self.goals)
        return result
        
    def add_goal(self, goal):
        self.goals.append(goal)
        
    def __str__(self):
        result = 'Goals:\n'
        for goal in self.goals:
            result += '   {0}\n'.format(goal)
        result += '({0} steps to construct)'.format(self.cost())
        return result
                
    def allocate_register(self, register_slot):
        if not self.is_slot_available(register_slot):
            return False
        prop = self.game.proponent
        register_clean = str(prop.values[register_slot]) == 'I'
        
        terms = []
        for goal in self.goals:
            terms.append(goal.term)
        register_access = (cards.get, number_term(register_slot))
        register_cost = sequential_cost(register_access)
        sub_term, advantage = optimal_subterm(register_cost, *terms)
        
        if not register_clean:
            advantage -= 1
            # because we have to clean it up
        
        if advantage <= 0:
            return False
        print>>sys.stderr, 'advantage', advantage
        
        sub_goal = Goal(sub_term, register_slot)
        for goal in self.goals:
            if not sub_term in subterms(goal.term):
                continue
            goal.term = replace_leaf_subterm(sub_term, register_access, goal.term)
            goal.requirements.append(TermInSlotRequirement(sub_term, register_slot))
            #Arrow(sub_goal, goal) # TODO: only add dependency if needed
        self.add_goal(sub_goal)
        
        return True
    
    def allocate_registers(self, regs=None):
        if regs is None:
            regs = slot_numbers_by_reachability[:5][::-1]
        print>>sys.stderr, regs
        for slot in regs:
            self.allocate_register(slot)
        
    def cost(self):
        return sum(goal.cost() for goal in self.goals)
    
    def is_slot_available(self, slot_number):
        'alive and not used by other goal'
        prop = self.game.proponent
        if prop.vitalities[slot_number] < 0:
            return False
        for goal in self.goals:
            if goal.slot == slot_number:
                return False
        for req in self.eternal_requirements:
            assert type(req) == 
        return True

    def remove_achieved_goals(self):
        new_goals = []
        for goal in self.goals:
            if not goal.achieved(self.game):
                new_goals.append(goal)
        self.goals = new_goals
    
    def get_instructions(self):
        assert self.goals
        
        status = {}
        
        for goal in self.goals:
            status[goal] = goal.status(self.game)
            if status[goal] == FAIL:
                print>>sys.stderr, 'network failed because of ', goal
                return None
                    
        for goal in self.goals:
            assert not goal.achieved(self.game)
            if goal.status(self.game) == OK:
                return goal.get_moves()
            
        assert set(status.values()) == set([WAIT])
        
if __name__ == '__main__':
    game = Game()
    net = Network(game)
    t = ((cards.get, number_term(8)), (cards.get, number_term(15)))
    t = (t, ((cards.get, number_term(3)), (cards.get, number_term(255))))
    node = Goal(t, 100)
    net.add_goal(node)
    print net
    net.allocate_registers()
    print net
    
    #for goal in net.goals:
    #    print goal.status(net.game), goal
    #print net.get_instructions()
    
    def make_moves():
        for move in net.get_instructions():
            game.make_half_move(*move)
            game.make_half_move('l', 0, cards.I) #opponent is idle
            
    make_moves()
    print game  