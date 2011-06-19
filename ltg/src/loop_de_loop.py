
import sys

from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP, IntValue
from sequence_bot import SequenceBot
from simple_bot import Bot
from slot_killer import SequenceBotNone
from terms import scnt, number_term, number_term_with_min_seq_cost, lambda_to_sequence
 

def loop_de_loop_bot():
    return LoopDeLoop()


class LambdaSequenceBot(Bot):
    def __init__(self, slot, lmb, lcl, add = None):
        self.slot = slot
        self.lmb = lmb
        self.lcl = lcl
        self.add = None

    def set_game(self, game):
        super(LambdaSequenceBot, self).set_game(game)
        self.sequence = self.mk_seq()

    def choose_move(self):
        move = self.sequence.choose_move()
        if move == None:
            move = self.add
            self.add = None
        return move

    def mk_seq(self):
        sequence = []
        for t in [
            self.lmb,
            ]:
            sequence += lambda_to_sequence(t, self.lcl)
        seq = SequenceBotNone(sequence, self.slot)
        seq.set_game(self.game)
        return seq


class MultipleLambdaSequencesBot(Bot):
    def __init__(self, bots, lcl):
        self.boost_term = number_term(8192)
        self.boostable = True
        self.lcl = lcl
        self.bots = []
        for bot_slot, bot_lmb in bots:
            self.bots.append(LambdaSequenceBot(bot_slot, bot_lmb, self.lcl))

    def set_game(self, game):
        super(MultipleLambdaSequencesBot, self).set_game(game)
        for bot in self.bots:
            bot.set_game(game)

    def boost_muthafucka(self, critical_slot):
        boost_slot = reduce(lambda x, y: y if scnt(y[0]) < scnt(x[0]) and y[0] > 31 and y[1] >= 10000 and str(y[2]) == 'I' else x, zip(range(SLOTS), self.game.proponent.vitalities, self.game.proponent.values), (255, 0, ''))[0]
        if boost_slot != 255:
            self.boostable = False
            boost = self.boost_term
            crtslot = number_term(critical_slot)
            bstslot = number_term(boost_slot)
            boost_bot = LambdaSequenceBot(boost_slot, r'(help bstslot crtslot boost)', locals())
            boost_bot.set_game(self.game)
            self.bots.insert(0, boost_bot)

    def revive_muthafucka(self, critical_slot):
        boost_slot = reduce(lambda x, y: y if scnt(y[0]) < scnt(x[0]) and y[0] > 31 and y[1] >= 10000 and str(y[2]) == 'I' else x, zip(range(SLOTS), self.game.proponent.vitalities, self.game.proponent.values), (255, 0, ''))[0]
        if boost_slot != 255:
            self.boostable = False
            crtslot = number_term(critical_slot)
            boost_bot = LambdaSequenceBot(boost_slot, r'(crtslot)', locals(), (LEFT_APP, boost_slot, cards.revive))
            boost_bot.set_game(self.game)
            self.bots.insert(0, boost_bot)

    def choose_move(self):
        if self.boostable:
            for critical_slot in range(4):
                if self.game.proponent.vitalities[critical_slot] <= 0:
                    self.revive_muthafucka(critical_slot)
                    break
                if self.game.proponent.vitalities[critical_slot] < 10000:
                    self.boost_muthafucka(critical_slot)
                    break
        if len(self.bots) == 0:
            return None
        cur_bot = self.bots[0]
        move = cur_bot.choose_move()
        if move == None:
            self.boostable = True
            self.bots = self.bots[1:]
            return self.choose_move()
        return move
        #for bot in self.bots:
        #    move = bot.choose_move()
        #    if move != None:
        #        return move
        #self.boostable = True


class LoopDeLoop(Bot):
    def __init__(self):
        self.terminate = False
        self.voltage = number_term(8192)
        self.otake = number_term(768)
        self.tgt = number_term(255)
        voltage = self.voltage
        otake = self.otake
        tgt = self.tgt
        self.sequence = MultipleLambdaSequencesBot([
                                                   ####(2, r'(\icomb. (icomb K (icomb get (succ (succ zero))) icomb) ((icomb get zero) (icomb get (succ zero))))'),
                                                   ####(2, r'(\zeroarg icomb. (K (icomb (get (succ (succ zero))) (succ zeroarg) icomb)) ((icomb get zero) zeroarg))'),
                                                   ###(2, r'(\zeroarg icomb. ((icomb get) (succ (succ zero)) (succ zeroarg)) ((icomb get) zero zeroarg))'),
                                                   ###(0, r'(\x. help x x voltage)'),
                                                   ####(1, r'(voltage)'),
                                                   ###(3, r'((get (succ (succ zero))) zero I)'),
                                                   #(2, r'(\icomb. (icomb K (icomb get (succ (succ zero))) icomb) ((icomb get zero) (icomb get (succ zero))))'),
                                                   #(2, r'(\zeroarg icomb. (K (icomb (get (succ (succ zero))) (succ zeroarg) icomb)) ((icomb get zero) zeroarg))'),
                                                   (0, r'(\icomb. icomb get 0 (icomb get 1 (icomb get 2)))'),
                                                   (1, r'(\x. (\ic. ic attack 0 x otake) (K I x help 0 0 voltage))'),
                                                   (2, r'(tgt)'),
                                                   (3, r'(put I get zero I)'),
                                                   ], locals())

    def set_game(self, game):
        super(LoopDeLoop, self).set_game(game)
        self.sequence.set_game(game)

    def spider_sense(self):
        return reduce(lambda x, y: y if len(str(y[1])) > len(str(x[1])) and len(str(y[1])) > 32 and y[2] > 0 else x, zip(range(SLOTS), self.game.opponent.values, self.game.opponent.vitalities), (-1, '', 0))[0]

    def we_re_done_for(self):
        return (self.game.proponent.vitalities[0] <= 0 or
                self.game.proponent.vitalities[1] <= 0 or
                self.game.proponent.vitalities[2] <= 0 or
                self.game.proponent.vitalities[3] <= 0)

    def choose_move(self):
        if self.terminate:
            danger = self.spider_sense()

#            if self.we_re_done_for():
#                return (LEFT_APP, 0, cards.I)
            if self.game.proponent.vitalities[0] > 0 and str(self.game.proponent.values[0]) == 'I':
                self.sequence = MultipleLambdaSequencesBot([
                                                           (0, r'(\icomb. icomb get 0 (icomb get 1 (icomb get 2)))'),
                                                           ], locals())
                self.sequence.set_game(self.game)
                self.terminate = False
                return self.choose_move()
            elif self.game.proponent.vitalities[1] > 0 and str(self.game.proponent.values[1]) == 'I':
                voltage = self.voltage
                otake = self.otake
                self.sequence = MultipleLambdaSequencesBot([
                                                           (1, r'(\x. (\ic. ic attack 0 x otake) (K I x help 0 0 voltage))'),
                                                           ], locals())
                self.sequence.set_game(self.game)
                self.terminate = False
                return self.choose_move()
            elif self.game.proponent.vitalities[2] > 0 and str(self.game.proponent.values[2]) == 'I':
                self.sequence = MultipleLambdaSequencesBot([
                                                           (2, r'(zero)'),
                                                           ], locals())
                self.sequence.set_game(self.game)
                self.terminate = False
                return self.choose_move()
            elif danger != -1:
                dng = number_term(MAX_SLOT - danger)
                self.sequence = MultipleLambdaSequencesBot([
                                                           (2, r'(put I dng)'),
                                                           (3, r'(put I get zero I)'),
                                                           ], locals())
                self.sequence.set_game(self.game)
                self.terminate = False
                return self.choose_move()
            elif isinstance(self.game.proponent.values[2], IntValue) and self.game.opponent.vitalities[MAX_SLOT - self.game.proponent.values[2]] > 0:
                self.sequence = MultipleLambdaSequencesBot([
                                                           (3, r'(put I get zero I)'),
                                                           ], locals())
                self.sequence.set_game(self.game)
                self.terminate = False
                return self.choose_move()
            elif self.game.proponent.values[2] == 255:
                self.sequence = MultipleLambdaSequencesBot([
                                                           (2, r'(put I zero)'),
                                                           ], locals())
                self.sequence.set_game(self.game)
                self.terminate = False
                return self.choose_move()
            elif isinstance(self.game.proponent.values[2], IntValue) and self.game.opponent.vitalities[MAX_SLOT - self.game.proponent.values[2]] <= 0:
                self.terminate = False
                return (LEFT_APP, 2, cards.succ)
            else:
                self.terminate = False
                return (LEFT_APP, 2, cards.succ)
        move = self.sequence.choose_move()
        if move != None:
            return move
        self.terminate = True
        return self.choose_move()


