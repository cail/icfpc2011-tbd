
from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP
from sequence_bot import SequenceBot
from simple_bot import Bot
from terms import number_term, term_to_sequence, binarize_term, parse_lambda

def test_combo_bot(slot = 0):
    #n = number_term(8192)
    #m = number_term(INITIAL_VITALITY)
    sequence = []
    for t in [
        r'((\c f x i. (\g. c f x) (f x)) (\c f x i. (\g. c f x) (f x)) (dec) (zero))',
        ]:
        t = parse_lambda(t, locals())
        t = binarize_term(t)
        sequence += term_to_sequence(t)
    return SequenceBot(sequence, slot)

