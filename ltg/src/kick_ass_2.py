
import sys

from rules import cards, SLOTS, MAX_SLOT, LEFT_APP, RIGHT_APP, IntValue
from sequence_bot import SequenceBot
from simple_bot import Bot
from slot_killer import SequenceBotNone
from kick_ass import SetToValue, BatteryPrepped
from terms import number_term, number_term_with_min_seq_cost, term_to_sequence, binarize_term, parse_lambda


def kick_ass_2_bot():
    return KickAss2()


class PrepBattery2(Bot):
    def __init__(self, battery_slot, pain_slot, observer_slot, gauge_slot):
        self.battery_slot = battery_slot
        self.pain_slot = pain_slot
        self.observer_slot = observer_slot
        self.gauge_slot = gauge_slot

    def set_game(self, game):
        super(PrepBattery2, self).set_game(game)
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
        pppslot = number_term(self.pain_slot)
        obsslot = number_term(self.observer_slot)
        ggeslot = number_term(self.gauge_slot)
        sequence = []
        for t in [
            r'(\icomb. (K (icomb get batslot)) ((K (((S help I) batslot) (icomb get pppslot))) (attack batslot (icomb get obsslot) (icomb get ggeslot))))',
            ]:
            t = parse_lambda(t, locals())
            t = binarize_term(t)
            sequence += term_to_sequence(t)
        seq = SequenceBotNone(sequence, self.battery_slot)
        seq.set_game(self.game)
        return seq


class KickAss2(Bot):
    def __init__(self):
        self.sequence = None
        self.battery_slot = -1
        self.pain_slot = -1
        self.observer_slot = -1
        self.gauge_slot = -1
        self.target_slot = -1
        self.gauge = -1
        self.pain = -1
        self.battery_prepped = False

    def set_game(self, game):
        super(KickAss2, self).set_game(game)
        self.pick_battery()
        self.pick_target()
        self.pick_pain()
        self.pick_observer()
        self.pick_gauge()
        self.change_of_plans()

    def choose_move(self):
        if self.is_battery_prepped() and self.is_pain_bearable() and self.is_target_painted() and self.is_gauge_set():
            print>>sys.stderr, ('everything prepped up -- firing mah lazor!')
            print>>sys.stderr, (str(self.game.proponent.values[self.gauge_slot]))
            print>>sys.stderr, (self.gauge)
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
        #self.battery_slot = reduce(lambda x, y: y if (y[1] > x[1] and
        #                                              y[0] != self.pain_slot and
        #                                              y[0] != self.observer_slot and
        #                                              y[0] != self.gauge_slot) else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]
        cands = zip(range(SLOTS), self.game.proponent.vitalities)
        bat_cand, cand_vit = reduce(lambda x, y: y if (y[1] > x[1] and
                                                      y[0] != self.pain_slot and
                                                      y[0] != self.observer_slot and
                                                      y[0] != self.gauge_slot) else x, cands, (0, 0))
        #cands_f = filter(lambda x: x[1] >= cand_vit * 4 / 5 and (x[0] in [128, 64, 32, 16, 8, 4, 2, 1]), cands)
        cands_f = filter(lambda x: x[1] >= cand_vit * 4 / 5 and (x[0] in [32, 16, 8, 4, 2, 1]), cands)
        if len(cands_f) > 0:
            self.battery_slot = reduce(lambda x, y: y[0] if y[0] > x else x, cands_f, 0)
        else:
            self.battery_slot = bat_cand
        if old_battery_slot != self.battery_slot:
            self.battery_prepped = False
        print>>sys.stderr, ('battery ' + str(self.battery_slot))

    def pick_pain(self):
        old_pain_slot = self.pain_slot
        self.pain_slot = reduce(lambda x, y: y if (y[1] > x[1] and
                                                   y[0] != self.battery_slot and
                                                   y[0] != self.observer_slot and
                                                   y[0] != self.gauge_slot) else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]
        if old_pain_slot != self.pain_slot:
            self.battery_prepped = False
        self.pain = self.recommend_pain()
        print>>sys.stderr, ('pain slot ' + str(self.pain_slot))
        print>>sys.stderr, ('pain ' + str(self.pain))

    def pick_observer(self):
        old_observer_slot = self.observer_slot
        self.observer_slot = reduce(lambda x, y: y if (y[1] > x[1] and
                                                       y[0] != self.battery_slot and
                                                       y[0] != self.pain_slot and
                                                       y[0] != self.gauge_slot) else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]
        if old_observer_slot != self.observer_slot:
            self.battery_prepped = False
        print>>sys.stderr, ('observer ' + str(self.observer_slot))

    def pick_gauge(self):
        old_gauge_slot = self.gauge_slot
        self.gauge_slot = reduce(lambda x, y: y if (y[1] > x[1] and
                                                    y[0] != self.battery_slot and
                                                    y[0] != self.pain_slot and
                                                    y[0] != self.observer_slot) else x, zip(range(SLOTS), self.game.proponent.vitalities), (0, 0))[0]
        if old_gauge_slot != self.gauge_slot:
            self.battery_prepped = False
        self.gauge = self.recommend_gauge()
        print>>sys.stderr, ('gauge slot ' + str(self.gauge_slot))
        print>>sys.stderr, ('gauge ' + str(self.gauge))

    def pick_target(self):
        self.target_slot = reduce(lambda x, y: y if y[1] < x[1] and y[1] != 0 else x, zip(range(SLOTS), self.game.opponent.vitalities), (0, 100500))[0]
        #self.target_slot = reduce(lambda x, y: y if len(str(y[1])) > len(str(x[1])) and y[2] != 0 else x, zip(range(SLOTS), self.game.opponent.values, self.game.opponent.vitalities), (0, '', 0))[0]
        print>>sys.stderr, ('attacking ' + str(self.target_slot))
        self.pick_gauge()

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

    def recommend_pain(self):
        return number_term_with_min_seq_cost(self.game.proponent.vitalities[self.battery_slot] * 99 / 100,
                                             self.game.proponent.vitalities[self.battery_slot] * 90 / 100)

    def change_of_plans(self):
        if not self.is_battery_prepped():
            self.pick_battery()
            self.sequence = PrepBattery2(self.battery_slot, self.pain_slot, self.observer_slot, self.gauge_slot)
        elif not self.is_pain_bearable():
            self.pick_pain()
            self.sequence = SetToValue(self.pain_slot, self.pain)
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

    def is_pain_bearable(self):
        return (self.game.proponent.vitalities[self.pain_slot] > 100 and
                self.game.proponent.values[self.pain_slot] == self.pain and
                self.game.proponent.vitalities[self.battery_slot] > self.pain and
                self.pain >= self.recommend_pain() * 1 / 2)

    def is_target_painted(self):
        return (self.game.proponent.vitalities[self.observer_slot] > 100 and
                self.game.proponent.values[self.observer_slot] == MAX_SLOT - self.target_slot and
                self.game.opponent.vitalities[self.target_slot] > 0)

    def is_gauge_set(self):
        return (self.game.proponent.vitalities[self.gauge_slot] > 100 and
                isinstance(self.game.proponent.values[self.gauge_slot], IntValue) and
                self.game.proponent.values[self.gauge_slot] == self.gauge and
                (self.gauge >= self.recommend_gauge() * 1 / 2 and self.gauge <= self.recommend_gauge() * 2))

