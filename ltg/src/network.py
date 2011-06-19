from pprint import pprint
import sys

from terms import number_term, optimal_subterm, replace_leaf_subterm,\
    sequential_cost, subterms
import rules
from rules import cards
from game import Game


FAIL = '0-FAIL'
WAIT = '1-WAIT'
OK = '2-OK'
# for comparisons like FAIL < OK


class Node(object):
    def __init__(self):
        self.in_ = []
        self.out = []
        
    def name(self):
        return '???'
    
    def check(self):
        raise NotImplementedError()
    
            
class Goal(Node):
    def __init__(self, term, slot=None):
        self.term = term
        self.slot = slot
        Node.__init__(self)
    
    def __str__(self):
        return 'Construct(term={0} at slot {1})'.format(self.term, self.slot)
    
    def name(self):
        return 'Goal@{0}'.format(self.slot)
    
    def status(self):
        assert self.slot is not None
        prop = self.game.prop
        if prop.vitalities[self.slot] <= 0:
            return FAIL
        if value_to_term(prop.values[self.slot]) == self.term:
            return OK
        return WAIT
    

class Arrow(object):
    'arrow x -> y means that y depends on x'
    def __init__(self, from_, to):
        self.from_ = None
        self.to = None
        self.set_from(from_)
        self.set_to(to)
        
    def set_from(self, from_):
        if self.from_ is not None:
            self.from_.out.remove(self)
        self.from_ = from_
        if from_ is not None:
            self.from_.out.append(self)
        
    def set_to(self, to):
        if self.to is not None:
            self.to.in_.remove(self)
        self.to = to
        if to is not None:
            self.to.in_.append(self)
            
    def delete(self):
        self.set_from(None)
        self.set_to(None)
        
    def __str__(self):
        return '{0} -> {1}'.format(self.from_.name(), self.to.name())


slot_numbers_by_reachability = range(rules.SLOTS)
slot_numbers_by_reachability.sort(key=lambda n: sequential_cost(number_term(n)))


class Network(object):
    def __init__(self, game):
        self.nodes = []
        self.game = game
        
    def add_node(self, node):
        node.game = self.game
        self.nodes.append(node)
        
    def get_arrows(self):
        result = set()
        for node in self.nodes:
            result |= set(node.in_)
            result |= set(node.out)    
        return result
    
    def __str__(self):
        result = 'Nodes:\n'
        for node in self.nodes:
            result += '   {0}\n'.format(node)
        result += 'Arrows:\n'
        for arrow in self.get_arrows():
            result += '   {0}\n'.format(arrow)
        result += '({0} steps to construct)'.format(self.steps_to_construct())
        return result
        
    def get_goals(self):
        return [node for node in self.nodes if isinstance(node, Goal)]
        
    def allocate_register(self, register_slot):
        prop = self.game.proponent
        if prop.vitalities[register_slot] < 0:
            return False
        
        register_clean = str(prop.values[register_slot]) == 'I'
        
        terms = []
        for goal in self.get_goals():
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
        for goal in self.get_goals():
            if not sub_term in subterms(goal.term):
                continue
            goal.term = replace_leaf_subterm(sub_term, register_access, goal.term)
            Arrow(sub_goal, goal) # TODO: only add dependency if needed
        self.add_node(sub_goal)
        
        return True
    
    def allocate_registers(self):
        numbers = slot_numbers_by_reachability[:50][::-1]
        print>>sys.stderr, numbers
        #numbers = [1]
        for slot in numbers:
            self.allocate_register(slot)
        
    def steps_to_construct(self):
        terms = [goal.term for goal in self.get_goals()]
        return sum(map(sequential_cost, terms))
    
    def get_instructions(self):
        pass
        
if __name__ == '__main__':
    game = Game()
    net = Network(game)
    t = ((cards.get, number_term(8)), (cards.get, number_term(65535)))
    node = Goal(t, 100)
    net.add_node(node)
    print net
    net.allocate_registers()
    print net
