from functools import partial
import sys

from rules import cards, card_by_name, INITIAL_VITALITY
from simple_bot import Bot

from terms import number_term, term_to_sequence, binarize_term, parse_lambda

class SequenceBot(Bot):
    def __init__(self, sequence, slot):
        print>>sys.stderr, 'sequence length', len(sequence)
        self.it = iter(sequence)
        self.slot = slot
        
    def choose_move(self):
        card, dir = next(self.it, (cards.I, 'l'))
        
        return dir, self.slot, card
    
    
def attack_term(i, j, n):
    i = number_term(i)
    j = number_term(j)
    n = number_term(n)
    return (cards.attack, i, j, n)
                   
       
def test_seq_bot():
    n = number_term(8192)
    m = number_term(INITIAL_VITALITY)

    #Y = r'(\f. (\q. q q) (\x. f (x x)))'
    #Y = parse_lambda(Y)

    sequence = []
    
    for t in [
        r'(attack zero zero n)',
        r'(attack (succ zero) zero n)',
        r'(zombie zero (\id. (help ((id succ) zero) zero m))'
        ]:
        t = parse_lambda(t, locals())
        t = binarize_term(t)
        sequence += term_to_sequence(t)
    slot = 0
    return SequenceBot(sequence, slot)

