from functools import partial

from rules import cards
from simple_bot import Bot

from terms import number_term, term_to_sequence

class SequenceBot(Bot):
    def __init__(self, sequence, slot, game):
        self.game = game
        self.it = iter(sequence)
        self.slot = slot
        
    def choose_move(self):
        card, dir = next(self.it, (cards.I, 'l'))
        
        return dir, self.slot, card
    
    
def attack_term(i, j, n):
    i = number_term(i)
    j = number_term(j)
    n = number_term(n)
    return (((cards.attack, i), j), n)
    
def test_seq_bot():
    #sequence = [(cards.zero, 'r'), (cards.succ, 'l')]
    t = attack_term(0, 0, 8000)
    sequence = term_to_sequence(t)
    t = attack_term(1, 0, 8000)
    sequence += term_to_sequence(t)
    slot = 0
    return partial(SequenceBot, sequence, slot)