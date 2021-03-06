from functools import partial
import sys
from random import randrange

from game import Game
from rules import cards, card_by_name, INITIAL_VITALITY, SLOTS
from simple_bot import Bot

from terms import number_term, term_to_sequence, binarize_term, parse_lambda,\
    unfold_numbers, sequential_cost

from network import Network, Goal, NetworkFail, global_optimize_network

NO_PLAN = 'NO PLAN'

class NetworkBot(Bot):
    def __init__(self, debug=False):
        self.net = None
        self.debug = debug
        self.prev_success = True
        
    def make_plan(self, prev_success):
        'return (plan, plan_checker)'
        raise NotImplementedError()
    
    def choose_move(self):
        # TODO: add application error detection
        i = 0
        while True:
            i += 1
            if i > 1000:
                if self.debug:
                    print>>sys.stderr, 'we are stuck in plan making'
                assert False, 'we are stuck in plan making'
                return ('l', 0, cards.I)
                
            if self.net is None:
                self.net, self.checker = self.make_plan(self.prev_success)
                self.prev_success = False # unless shown otherwise
                if self.net == NO_PLAN:
                    return ('l', 0, cards.I)                
                if self.debug:
                    print>>sys.stderr, 'NEW PLAN:', self.net
                #self.net.refine()
                self.net = global_optimize_network(self.net)
                self.net.begin()
                if self.debug:
                    print>>sys.stderr, 'DETAILED PLAN:', self.net
                if not self.checker():
                    if self.debug:
                        print>>sys.stderr, 'plan was impossible from the beginning'
                    self.net = None
                    continue
                
                if self.debug:
                    raw_input()
            
            if self.net == NO_PLAN:
                return ('l', 0, cards.I)
            
            if self.net.is_finished():
                if self.debug:
                    print>>sys.stderr, 'finished'
                self.net = None
                self.prev_success = True
                continue
            
            if not self.checker():
                if self.debug:
                    print>>sys.stderr, 'checker rejected plan'
                self.net = None
                continue
                        
            try:
                self.net.check()
                move = self.net.get_next_move()
                return move
            except NetworkFail as e:
                if self.debug:
                    print>>sys.stderr, 'plan failed because', e
                self.net = None
            
        
            
def lambdas_to_plan(game, d):
    result = Network(game)
    for slot, term in d.items():
        term = parse_lambda(term)
        term = binarize_term(term)
        term = unfold_numbers(term)
        result.add_goal(Goal(term, slot))
    return result
                   
            
class SampleNetworkBot(NetworkBot):
    def __init__(self, debug=False):
        self.plans_limit = 1000
        NetworkBot.__init__(self, debug)
        
    
    def kill_plan(self):
        damage = 8192
        
        if self.plans_limit == 999: # first call
            attacker1 = 0
            attacker2 = 1
        else:
            attacker1 = randrange(100)
            attacker2 = randrange(100)
            
        target = SLOTS-1
        
        plan = lambdas_to_plan(self.game, {
            42: r'(attack {0} {1} {2})'.format(attacker1, 255-target, damage),
            43: r'(attack {0} {1} {2})'.format(attacker2, 255-target, damage),
        })
        
        def plan_checker():
            prop = self.game.proponent
            opp = self.game.opponent

            if opp.vitalities[target] <= 0:
                return False # no need to kill

            d = 0
            if prop.vitalities[attacker1] >= damage:
                d += damage*9//10
            if prop.vitalities[attacker2] >= damage:
                d += damage*9//10
            if opp.vitalities[target] > d:
                return False # can't kill anyway

            return True

        return plan, plan_checker
    
    def zombie_plan(self):
        vits = self.game.opponent.vitalities
        alive = [slot for slot in range(SLOTS) if vits[slot] > 0]
        
        donor, acceptor = (alive+[0, 0])[:2]
        if vits[donor] <= vits[acceptor]:
            donor, acceptor = acceptor, donor

        target = SLOTS-1
        
        #def range_term(m, n):
        #    return min(range(m, n), key=lambda i: sequential_cost(number_term(i)))
        
        help_term = '(help {0} {1})'.format(donor, acceptor)
        if self.plans_limit == 998:
            strength = 8704
        else:
            strength = vits[donor]
        #strength = range_term((vits[acceptor]*10+10)//11, vits[donor]+1)
        #assert strength <= vits[donor], vits[donor]
        #assert strength*11//10 >= vits[acceptor] 
        lazy_help = '(S (K {0}) (K {1}))'.format(help_term, strength)
         
        slot = randrange(SLOTS)
        plan = lambdas_to_plan(self.game, {
            slot: '(zombie {0} {1})'.format(255-target, lazy_help),
        })
        
        def plan_checker():
            return True # TODO:
        
        return plan, plan_checker
    
    def make_plan(self, prev_success):
        self.plans_limit -= 1
        if self.plans_limit < 0:
            return NO_PLAN, None
        
        opp = self.game.opponent
        if opp.vitalities[255] > 0:
            return self.kill_plan()
        else:
            return self.zombie_plan()
        
        #assert plan_checker()
