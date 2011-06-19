
from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP
from sequence_bot import SequenceBot
from simple_bot import Bot
from terms import number_term, term_to_sequence, binarize_term, parse_lambda

def test_idiot_bot(slot = 0):
    sequence = []
    return SequenceBot(sequence, slot)


