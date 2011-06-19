
import sys

from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP
from sequence_bot import SequenceBot
from simple_bot import Bot
from slot_killer import SequenceBotNone, BoostBattery, AttackSlot
from kick_ass import BatteryPrepped
from terms import number_term, number_term_with_min_seq_cost, term_to_sequence, binarize_term, parse_lambda


# Slot 0 is reserved for the battery

def the_battery_bot():
    return TheBattery()


class PrepTheBattery(Bot):
    def __init__(self, battery_slot):
        self.battery_slot = battery_slot

    def set_game(self, game):
        super(PrepTheBattery, self).set_game(game)
        self.sequence = self.mk_seq()
        #print>>sys.stderr, ('boosting ' + str(self.battery_slot) + ' for ' + str(self.boost))

    def choose_move(self):
        if self.game.proponent.vitalities[self.battery_slot] < 40961:
            return None
        move = self.sequence.choose_move()
        if move == None:
            raise BatteryPrepped()
        return move

    def mk_seq(self):
        batslot = number_term(self.battery_slot)
        boost = number_term(40960)
        sequence = []
        for t in [
            r'(\icomb. (K (icomb get batslot)) (icomb S help I batslot boost))',
            ]:
            t = parse_lambda(t, locals())
            t = binarize_term(t)
            sequence += term_to_sequence(t)
        seq = SequenceBotNone(sequence, self.battery_slot)
        seq.set_game(self.game)
        return seq


class TheBattery(Bot):
    def __init__(self):
        self.sequence = None
        self.battery_prepped = False

    def set_game(self, game):
        super(TheBattery, self).set_game(game)
        self.pick_battery()
        self.pick_execution()
        self.pick_target()
        self.change_of_plans()

    def choose_move(self):
        try:
            move = self.get_next_move()
        except BatteryPrepped:
            self.battery_prepped = True
            move = None
        if move == None:
            self.change_of_plans()
            move = self.get_next_move()
        if move == None:
            move = (RIGHT_APP, self.battery_slot, cards.I)
        return move

    def get_next_move(self):
        return self.sequence.choose_move()

    def pick_battery(self):
        self.battery_slot = 0

    def pick_execution(self):
        self.execution_slot = reduce(lambda x, y: y if (y[1] > x[1] and y[0] != self.battery_slot) else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]

    def pick_target(self):
        #self.target_slot = reduce(lambda x, y: y if y[1] <= x[1] and y[1] != 0 else x, zip(range(SLOTS), self.game.opponent.vitalities), (0, 100500))[0]
        self.target_slot = reduce(lambda x, y: y if len(str(y[1])) > len(str(x[1])) and y[2] != 0 else x, zip(range(SLOTS), self.game.opponent.values, self.game.opponent.vitalities), (0, '', 0))[0]

    def recommend_gauge(self):
        gauge = self.game.opponent.vitalities[self.target_slot]
        if gauge > (self.game.proponent.vitalities[self.battery_slot] - 10000) / 2:
            gauge = number_term_with_min_seq_cost((self.game.proponent.vitalities[self.battery_slot] - 10000) * 3 / 8,
                                                  (self.game.proponent.vitalities[self.battery_slot] - 10000) * 4 / 8)
        if self.game.proponent.vitalities[self.battery_slot] < 60000:
            gauge = 8
        if gauge < 10:
            gauge = 8
        return gauge

    def change_of_plans(self):
        if self.game.proponent.vitalities[self.battery_slot] < 40961 or (
           self.game.proponent.vitalities[self.battery_slot] < 60000 and not self.battery_prepped):
            self.pick_battery()
            self.pick_execution()
            self.battery_prepped = False
            self.sequence = BoostBattery(self.battery_slot, self.execution_slot)
        elif self.battery_prepped and self.game.proponent.vitalities[self.battery_slot] < 60000:
            self.sequence = SequenceBotNone([], 0)
        elif self.battery_prepped:
            self.pick_execution()
            self.pick_target()
            self.sequence = AttackSlot(self.battery_slot, self.target_slot, self.execution_slot, reserve = 45000)
        else:
            self.sequence = PrepTheBattery(self.battery_slot)
        self.sequence.set_game(self.game)

