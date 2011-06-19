
import sys

from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP
from sequence_bot import SequenceBot
from simple_bot import Bot
from slot_killer import SequenceBotNone
from terms import number_term, term_to_sequence, binarize_term, parse_lambda


def kick_ass_bot():
    return KickAss()


class BatteryPrepped(Exception): # duh
    pass


class PrepBattery(Bot):
    def __init__(self, battery_slot, observer_slot, gauge_slot):
        self.battery_slot = battery_slot
        self.observer_slot = observer_slot
        self.gauge_slot = gauge_slot

    def set_game(self, game):
        super(PrepBattery, self).set_game(game)
        self.boost = 8192
        self.sequence = self.mk_seq()
        #print>>sys.stderr, ('boosting ' + str(self.battery_slot) + ' for ' + str(self.boost))

    def choose_move(self):
        if self.game.proponent.vitalities[self.battery_slot] < 10000:
            return None
        move = self.sequence.choose_move()
        if move == None:
            raise BatteryPrepped()
        return move

    def mk_seq(self):
        batslot = number_term(self.battery_slot)
        obsslot = number_term(self.observer_slot)
        ggeslot = number_term(self.gauge_slot)
        boost = number_term(self.boost)
        sequence = []
        for t in [
            r'(\icomb. (K (icomb get batslot)) ((K (icomb help batslot batslot boost)) (attack batslot (icomb get obsslot) (icomb get ggeslot))))',
            ]:
            t = parse_lambda(t, locals())
            t = binarize_term(t)
            sequence += term_to_sequence(t)
        seq = SequenceBotNone(sequence, self.battery_slot)
        seq.set_game(self.game)
        return seq


class SetToValue(Bot):
    def __init__(self, slot, value):
        self.slot = slot
        self.value = value
        self.sequence = None

    def set_game(self, game):
        super(SetToValue, self).set_game(game)
        self.sequence = self.mk_seq()

    def choose_move(self):
        if self.game.proponent.vitalities[self.slot] < 1000:
            return None
        if self.game.proponent.values[self.slot] == self.value:
            return None
        move = self.sequence.choose_move()
        return move

    def mk_seq(self):
        value = number_term(self.value)
        sequence = []
        for t in [
            r'((put I) value)',
            ]:
            t = parse_lambda(t, locals())
            t = binarize_term(t)
            sequence += term_to_sequence(t)
        seq = SequenceBotNone(sequence, self.slot)
        seq.set_game(self.game)
        return seq


class KickAss(Bot):
    def __init__(self):
        self.sequence = None
        self.battery_slot = -1
        self.observer_slot = -1
        self.gauge_slot = -1
        self.target_slot = -1
        self.gauge = -1
        self.boost = 9999
        self.battery_prepped = False

    def set_game(self, game):
        super(KickAss, self).set_game(game)
        self.pick_battery()
        self.pick_target()
        self.pick_observer()
        self.pick_gauge()
        self.change_of_plans()

    def choose_move(self):
        if self.is_battery_prepped() and self.is_target_painted() and self.is_gauge_set():
            move = (RIGHT_APP, self.battery_slot, cards.I)
        else:
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
        old_battery_slot = self.battery_slot
        self.battery_slot = reduce(lambda x, y: y if y[1] > x[1] and y[0] != self.observer_slot and y[0] != self.gauge_slot else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]
        if old_battery_slot != self.battery_slot:
            self.battery_prepped = False

    def pick_observer(self):
        old_observer_slot = self.observer_slot
        self.observer_slot = reduce(lambda x, y: y if y[1] > x[1] and y[0] != self.battery_slot and y[0] != self.gauge_slot else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]
        if old_observer_slot != self.observer_slot:
            self.battery_prepped = False

    def pick_gauge(self):
        old_gauge_slot = self.gauge_slot
        self.gauge_slot = reduce(lambda x, y: y if y[1] > x[1] and y[0] != self.battery_slot and y[0] != self.battery_slot else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]
        if old_gauge_slot != self.gauge_slot:
            self.battery_prepped = False
        self.gauge = self.recommend_gauge()

    def pick_target(self):
        self.target_slot = reduce(lambda x, y: y if y[1] < x[1] and y[1] != 0 else x, zip(range(SLOTS), self.game.opponent.vitalities), (0, 100500))[0]
        #self.target_slot = reduce(lambda x, y: y if len(str(y[1])) > len(str(x[1])) and y[2] != 0 else x, zip(range(SLOTS), self.game.opponent.values, self.game.opponent.vitalities), (0, '', 0))[0]
        #print>>stderr, ('attacking ' + str(self.target_slot))
        self.pick_gauge()

    def recommend_gauge(self):
        gauge = self.game.opponent.vitalities[self.target_slot]
        if gauge > (self.game.proponent.vitalities[self.battery_slot] - 10000) / 2:
            gauge = (self.game.proponent.vitalities[self.battery_slot] - 10000) / 2
        if self.game.proponent.vitalities[self.battery_slot] < 60000:
            gauge = 10
        if gauge < 10:
            gauge = 10
        return gauge

    def change_of_plans(self):
        if not self.is_battery_prepped():
            self.pick_battery()
            self.sequence = PrepBattery(self.battery_slot, self.observer_slot, self.gauge_slot)
        elif not self.is_target_painted():
            self.pick_target()
            self.pick_observer()
            self.sequence = SetToValue(self.observer_slot, MAX_SLOT - self.target_slot)
        elif not self.is_gauge_set():
            self.pick_target()
            self.pick_gauge()
            self.sequence = SetToValue(self.gauge_slot, self.gauge)
        self.sequence.set_game(self.game)

    def is_battery_prepped(self):
        return self.battery_prepped

    def is_target_painted(self):
        return (self.game.proponent.vitalities[self.observer_slot] > 1000 and self.game.proponent.values[self.observer_slot] == MAX_SLOT - self.target_slot and
                self.game.opponent.vitalities[self.target_slot] > 0)

    def is_gauge_set(self):
        return (self.game.proponent.vitalities[self.gauge_slot] > 1000 and self.game.proponent.values[self.gauge_slot] == self.gauge and
                (self.gauge >= self.recommend_gauge() * 2 / 3 and self.gauge <= self.recommend_gauge() * 2))

