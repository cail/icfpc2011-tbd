from itertools import *
import random

from rules import cards
from simple_bot import Bot
from terms import lambda_to_sequence, parse_sequence, apply_sequences


class Fail(Exception):
    pass


class IterBot(Bot):
    def __init__(self):
        self.it = None
        
    def get_strategy(self):
        'return iterable'
        raise NotImplementedError()
        
    def choose_move(self):
        if self.it is None:
            self.it = iter(self.get_strategy())
        return next(self.it, ('l', 42, cards.zero))
    
    
    @staticmethod
    def fail_safe(self, strat):
        try:
            for move in strat:
                yield move
        except:
            pass
            
    
    @staticmethod
    def run_seq(slot, sequence):
        if isinstance(sequence, str):
            sequence = parse_sequence(sequence)
        for card, dir in sequence:
            yield (dir, slot, card)
        
    @staticmethod
    def run_term(slot, term, dirty=False):
        if dirty:
            yield ('l', slot, cards.put)
        for card, dir in lambda_to_sequence(term):
            yield (dir, slot, card)
            
            
    def assign_term(self, slot, term):
        prop = self.game.proponent
        for move in\
            self.run_term(slot, term, dirty=(prop.values[slot] != cards.I)):
            yield move
            
    @staticmethod
    def apply_to(f, arg):
        'slot[f] = slot[f](arg)'
        return IterBot.run_seq(f, apply_sequences([], lambda_to_sequence(arg)))

    def fresh_slot(self, rng=range(256)):
        prop = self.game.proponent
        rng = list(rng)
        random.shuffle(rng)
        for slot in rng:
            if prop.vitalities[slot] > 0 and prop.values[slot] == cards.I:
                return slot
        raise Fail()

    def revive_reflex(self, strat, slots):
        prop = self.game.proponent
        for move in strat:
            yield move
            
            for slot in slots:
                if prop.vitalities[slot] <= 0:
                    t = self.fresh_slot(range(10, 250))
                    for m in self.run_term(t, '(revive {0})'.format(slot)):
                        yield m
                        
    def coup_de_gras_reflex(self, strat, slots):
        opp = self.game.opponent
        for move in strat:
            yield move
            
            for slot in slots:
                if opp.vitalities[slot] == 1:
                    t = self.fresh_slot(range(10, 250))
                    for m in self.run_term(t, '(dec {0})'.format(255-slot)):
                        yield m        
        
        
class ZombieRush(IterBot):

    def rush(self):
        strat = chain(
            self.assign_term(0, r'9216'), # because this number will also be used for Z
            self.assign_term(1, r'(\source. attack source 0 (get 0))'),
            self.assign_term(2, r'(get 1)'),
            self.apply_to(1,'0'), # attack 0 -> 0
            #self.run_seq(2,'K l, S l, succ r, zero r'), 
            self.apply_to(2, '1'), # attack 1 -> 0
             
            self.assign_term(1, '(K (help 1 0))'),
            self.run_seq(0, 'K l'),
            self.assign_term(2, '(S (get 1) (get 0)'),
            self.assign_term(3, '(zombie 0 (get 2))'),
        )
        return strat
    
    def generic_zombie(self):
        vits = self.game.opponent.vitalities
        alive = [i for i in range(256) if vits[i] > 0]
        alive += [0, 0]
        donor, acceptor = alive[:2]
        if vits[donor] < vits[acceptor]:
            donor, acceptor = acceptor, donor
        
        strength = vits[donor]
        
        strat = chain(
            self.assign_term(0, str(acceptor)),
            self.assign_term(1, '(help {0})'.format(donor)),
            self.apply_to(1, '(get 0)'),
            self.run_seq(1, 'K l, S l'),
            self.assign_term(0, '(K {0})'.format(strength)),
            self.apply_to(1, '(get 0)'),
            self.assign_term(3, '(zombie 0 (get 1))'),
        )
        
        for move in strat:
            yield move
                                
    def get_strategy(self):
        strat = chain(
            self.rush(),
            chain(*(self.generic_zombie() for _ in xrange(1000))),
            repeat(('r', 66, cards.zero)),
            )
        strat = self.coup_de_gras_reflex(strat, range(253, 256))
        strat = self.revive_reflex(strat, range(5))
        return strat
    