from itertools import *
import random
import sys
import logging

from rules import cards
from simple_bot import Bot
from terms import lambda_to_sequence, parse_sequence, apply_sequences



class Fail(Exception):
    pass


class IterBot(Bot):
    def __init__(self):
        self.it = None
        self.log = logging.getLogger('IdleBot')
        
    def get_strategy(self):
        'return iterable'
        raise NotImplementedError()
        
    def choose_move(self):
        if self.it is None:
            self.it = iter(self.get_strategy())
        return next(self.it, ('l', 42, cards.zero))
    
    
    def fail_safe(self, strat, retries=1):
        for i in range(retries):
            try:
                for move in strat:
                    yield move
                return
            except Fail as e:
                if i == retries-1:
                    self.log.warning('fail {0} - abort'.format(e))
                else:
                    self.log.warning('fail {0} - retry'.format(e))
                    
            
    
    def run_seq(self, slot, sequence):
        if isinstance(sequence, str):
            sequence = parse_sequence(sequence)
        prop = self.game.proponent
        for card, dir in sequence:
            if prop.vitalities[slot] <= 0:
                raise Fail('run_seq on dead slot {0}'.format(slot))
            yield (dir, slot, card)
        

    def run_term(self, slot, term, dirty=False):
        prop = self.game.proponent
        if dirty:
            if prop.vitalities[slot] <= 0:
                raise Fail('run_seq on dead slot {0}'.format(slot))
            yield ('l', slot, cards.put)
        for card, dir in lambda_to_sequence(term):
            if prop.vitalities[slot] <= 0:
                raise Fail('run_seq on dead slot {0}'.format(slot))
            yield (dir, slot, card)
            
            
    def assign_term(self, slot, term):
        prop = self.game.proponent
        return self.run_term(slot, term, dirty=(prop.values[slot] != cards.I))
    
            
    def apply_to(self, f, arg):
        'slot[f] = slot[f](arg)'
        return self.run_seq(f, apply_sequences([], lambda_to_sequence(arg)))

    def fresh_slot(self, rng=range(256)):
        prop = self.game.proponent
        r = list(rng)
        random.shuffle(r)
        for slot in r:
            if prop.vitalities[slot] > 0 and prop.values[slot] == cards.I:
                return slot
        raise Fail("Can't find fresh slot among {0}".format(rng))

    def revive_reflex(self, strat, slots):
        prop = self.game.proponent
        for move in strat:
            yield move
            
            for slot in slots:
                if prop.vitalities[slot] <= 0:
                    t = self.fresh_slot(range(10, 250))
                    self.log.info('revive reflex {0} at {1}'.format(slot, t))
                    for m in self.run_term(t, '(revive {0})'.format(slot)):
                        yield m
                        
    def coup_de_gras_reflex(self, strat, slots):
        opp = self.game.opponent
        for move in strat:
            yield move
            
            for slot in slots:
                if opp.vitalities[slot] == 1:
                    t = self.fresh_slot(range(10, 250))
                    self.log.info('coup de gras reflex {0} at {1}'.format(slot, t))
                    for m in self.run_term(t, '(dec {0})'.format(255-slot)):
                        yield m        
        
        
class ZombieRush(IterBot):
    def __init__(self, handicap=0):
        self.handicap = handicap
        super(type(self), self).__init__()

    def ensure_zombie_heal_possible(self, donor, acceptor, strength):
        vits = self.game.opponent.vitalities
        if vits[donor] < strength:
            raise Fail('acceptor is too weak')
        if donor == acceptor:
            if vits[acceptor] > strength+strength*11//10:
                raise Fail('not enough help to kill donor by himself')
        else:
            if vits[acceptor] > strength*11//10:
                raise Fail('not enough help to kill donor')

    def rush(self):
        self.log.info('rush')
        strength = 9216 # because this number will also be used for Z
        kill = chain(
            self.assign_term(0, str(strength)),
            self.assign_term(1, r'(\source. attack source 0 (get 0))'),
            self.assign_term(2, r'(get 1)'),
            self.apply_to(1,'0'), # attack 0 -> 0
            self.apply_to(2, '1'), # attack 1 -> 0
        )
        for move in kill:
            yield move
        
        donor = acceptor = 0
        zombie = chain(     
            self.assign_term(1, '(K (help {0} {1}))'.format(donor, acceptor)),
            self.run_seq(0, 'K l'),
            self.assign_term(2, '(S (get 1) (get 0)'),
            self.assign_term(3, '(zombie 0 (get 2))'),
        )
        for move in zombie:
            self.ensure_zombie_heal_possible(donor, acceptor, strength)
            yield move
    
    def generic_zombie(self):
        vits = self.game.opponent.vitalities
        alive = [i for i in range(256) if vits[i] > 0]
        alive += [0, 0]
        donor, acceptor = alive[:2]
        if vits[donor] < vits[acceptor]:
            donor, acceptor = acceptor, donor
        
        strength = vits[donor]
        
        self.log.info('generic zombie (heal {0} {1} {2})'.
                      format(donor, acceptor, strength))
        
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
            self.ensure_zombie_heal_possible(donor, acceptor, strength)
            yield move
                                
    def get_strategy(self):
        self.log = logging.getLogger('IterBot.Player{0}'.format(self.game.half_moves%2))
        self.log.info('creating strategy')
        
        strat = chain(
            [('l', 0, cards.I)]*self.handicap,
            self.fail_safe(self.rush()),
            chain(*(self.fail_safe(self.generic_zombie()) for _ in xrange(1000))),
            )
        strat = self.coup_de_gras_reflex(strat, [255])
        strat = self.revive_reflex(strat, range(4))
        return strat
    