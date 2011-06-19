
import sys

from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP
from sequence_bot import SequenceBot
from simple_bot import Bot
from terms import number_term, term_to_sequence, binarize_term, parse_lambda

def test_combo_bot(slot = 0):
    tgtslot = number_term(0)
    selfslot = number_term(slot)
    #m = number_term(INITIAL_VITALITY)
    sequence = []
    for t in [
        #r'((\c f x. (\i. (\g. i c f x) (i f x))) (\c f x. (\i. (\g. i c f x) (i f x))) (dec) (zero))',
        r'(((\atkslot icomb. K (icomb get selfslot) (icomb dec atkslot)) tgtslot) I)',
        ]:
        t = parse_lambda(t, locals())
        t = binarize_term(t)
        sequence += term_to_sequence(t)
    return SequenceBot(sequence, slot)

