
import sys

from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP
from sequence_bot import SequenceBot
from simple_bot import Bot
from slot_killer import SequenceBotNone
from terms import number_term, number_term_with_min_seq_cost, term_to_sequence, binarize_term, parse_lambda


def loop_de_loop_bot():
    return LoopDeLoop()


class LambdaSequenceBot(Bot):
    def __init__(self, slot, lmb):
        self.slot = slot
        self.lmb = lmb

    def set_game(self, game):
        super(LambdaSequenceBot, self).set_game(game)
        self.sequence = self.mk_seq()

    def choose_move(self):
        return self.sequence.choose_move()

    def mk_seq(self):
        sequence = []
        for t in [
            self.lmb,
            ]:
            t = parse_lambda(t, locals())
            t = binarize_term(t)
            sequence += term_to_sequence(t)
        seq = SequenceBotNone(sequence, self.slot)
        seq.set_game(self.game)
        return seq


class MultipleLambdaSequencesBot(Bot):
    def __init__(self, bots):
        self.bots = []
        for bot_slot, bot_lmb in bots:
            self.bots.append(LambdaSequenceBot(bot_slot, bot_lmb))

    def set_game(self, game):
        super(MultipleLambdaSequencesBot, self).set_game(game)
        for bot in self.bots:
            bot.set_game(game)

    def choose_move(self):
        for bot in self.bots:
            move = bot.choose_move()
            if move != None:
                return move
        return None


class LoopDeLoop(Bot):
    def __init__(self):
        self.sequence = MultipleLambdaSequencesBot([
                                                   (2, r'(\icomb. (icomb K (icomb get (succ (succ zero))) icomb) ((icomb get zero) (icomb get (succ zero))))'),
                                                   (0, r'(dec)'),
                                                   (1, r'((put I) zero)'),
                                                   (3, r'((get (succ (succ zero))) I)'),
                                                   ])

    def set_game(self, game):
        super(LoopDeLoop, self).set_game(game)
        self.sequence.set_game(game)

    def choose_move(self):
        return self.sequence.choose_move()


