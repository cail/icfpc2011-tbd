
import sys

from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP
from sequence_bot import SequenceBot
from simple_bot import Bot
from terms import number_term, number_term_with_min_seq_cost, term_to_sequence, binarize_term, parse_lambda


def slot_killer_bot():
    return SlotKiller()


class SequenceBotNone(SequenceBot):
    def choose_move(self):
        try:
            move = next(self.it)
        except StopIteration:
            return None
        card, dir = move
        return dir, self.slot, card


class BoostBattery(Bot):
    def __init__(self, battery_slot, execution_slot = None):
        self.battery_slot = battery_slot
        self.execution_slot = execution_slot
        if self.execution_slot == None:
            self.execution_slot = self.battery_slot

    def set_game(self, game):
        super(BoostBattery, self).set_game(game)
        self.boost = number_term_with_min_seq_cost(self.game.proponent.vitalities[self.battery_slot] * 90 / 100,
                                                   self.game.proponent.vitalities[self.battery_slot] * 75 / 100)
        self.sequence = self.mk_seq()
        #print>>sys.stderr, ('boosting ' + str(self.battery_slot) + ' for ' + str(self.boost))

    def choose_move(self):
        if self.game.proponent.vitalities[self.battery_slot] < max(10000, self.boost):
            return None
        return self.sequence.choose_move()

    def mk_seq(self):
        batslot = number_term(self.battery_slot)
        boost = number_term(self.boost)
        sequence = []
        for t in [
            r'(S help I batslot boost)',
            ]:
            t = parse_lambda(t, locals())
            t = binarize_term(t)
            sequence += term_to_sequence(t)
        seq = SequenceBotNone(sequence, self.execution_slot)
        seq.set_game(self.game)
        return seq


class AttackSlot(Bot):
    def __init__(self, battery_slot, target_slot, execution_slot = None, reserve = 30000):
        self.battery_slot = battery_slot
        self.target_slot = target_slot
        self.execution_slot = execution_slot
        if self.execution_slot == None:
            self.execution_slot = self.battery_slot
        self.reserve = reserve

    def set_game(self, game):
        super(AttackSlot, self).set_game(game)
        if self.game.opponent.vitalities[self.target_slot] * 10 / 9 < (self.game.proponent.vitalities[self.battery_slot] - 8 - self.reserve):
            self.dmg = number_term_with_min_seq_cost(self.game.opponent.vitalities[self.target_slot] * 10 / 9 + 8,
                                                     self.game.opponent.vitalities[self.target_slot] * 12 / 9 + 8)
        else:
        #    self.dmg = number_term_with_min_seq_cost((self.game.opponent.vitalities[self.battery_slot] - 10000) * 7 / 16 + 8,
        #                                             (self.game.opponent.vitalities[self.battery_slot] - 10000) * 9 / 16 + 8)
            self.dmg = number_term_with_min_seq_cost((self.game.opponent.vitalities[self.battery_slot] - 8 - self.reserve) * 4 / 5,
                                                     (self.game.opponent.vitalities[self.battery_slot] - 8 - self.reserve))
        self.sequence = self.mk_seq()
        #print>>sys.stderr, ('attacking ' + str(self.target_slot) + ' with ' + str(self.battery_slot) + ' for ' + str(self.dmg))

    def choose_move(self):
        if (self.game.proponent.vitalities[self.battery_slot] < self.dmg or
            self.game.opponent.vitalities[self.target_slot] <= 0):
            return None
        return self.sequence.choose_move()

    def mk_seq(self):
        batslot = number_term(self.battery_slot)
        atkslot = number_term(MAX_SLOT - self.target_slot)
        dmg = number_term(self.dmg)
        sequence = []
        for t in [
            r'(attack batslot atkslot dmg)',
            ]:
            t = parse_lambda(t, locals())
            t = binarize_term(t)
            sequence += term_to_sequence(t)
        seq = SequenceBotNone(sequence, self.execution_slot)
        seq.set_game(self.game)
        return seq


class SlotKiller(Bot):
    def __init__(self):
        self.sequence = None

    def set_game(self, game):
        super(SlotKiller, self).set_game(game)
        self.pick_battery()
        self.pick_target()
        self.change_of_plans()

    def choose_move(self):
        move = self.get_next_move()
        if move == None:
            self.change_of_plans()
            move = self.get_next_move()
        if move == None:
            move = (LEFT_APP, 0, cards.I)
        return move

    def get_next_move(self):
        return self.sequence.choose_move()

    def pick_battery(self):
        self.battery_slot = reduce(lambda x, y: x if x[1] >= y[1] else y, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]

    def pick_target(self):
        self.target_slot = reduce(lambda x, y: y if y[1] <= x[1] and y[1] != 0 else x, zip(range(SLOTS), self.game.opponent.vitalities), (0, 100500))[0]

    def change_of_plans(self):
        self.pick_battery()
        self.pick_target()
        if self.game.proponent.vitalities[self.battery_slot] < 60000:
            self.pick_battery()
            self.sequence = BoostBattery(self.battery_slot)
        elif self.game.opponent.vitalities[self.target_slot] > 0:
            self.pick_target()
            self.sequence = AttackSlot(self.battery_slot, self.target_slot)
        else:
            #print>>sys.stderr, 'blargh', self.battery_slot, self.target_slot
            self.sequence = SequenceBot([], 0)
        self.sequence.set_game(self.game)

