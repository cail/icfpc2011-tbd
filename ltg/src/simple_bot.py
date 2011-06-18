# not because bots are simple
# but because their interface is FUCKING SIMPLE

import random
import sys

from rules import cards, LEFT_APP, RIGHT_APP, SLOTS, card_by_name


__all__ = [
    'IdleBot',
    'RandomBot'
    'InteractiveBot',
]


class IdleBot(object):
    def __init__(self, game):
        self.game = game
    def choose_move(self):
        return (LEFT_APP, 0, cards.I)


class RandomBot(object):
    def __init__(self, game):
        self.game = game
    def choose_move(self):
        return (
            random.choice([LEFT_APP, RIGHT_APP]), 
            random.randrange(SLOTS),
            random.choice(card_by_name.values()))


class InteractiveBot(object):
    def __init__(self, game):
        self.game = game
       
    def read_slot(self):
        print 'slot no?'
        while True:
            slot = raw_input()
            try:
                slot = int(slot)
            except ValueError as e:
                print e
                continue
            if slot not in range(SLOTS):
                print 'between 0 and', SLOTS-1
                continue
            return slot
        
    def read_card(self):
        print 'card name?'
        while True:
            card = raw_input()
            if card in card_by_name:
                return card
            print 'available card names are', card_by_name.keys()
            
    def choose_move(self):
        if len(self.game.move_history) > 0:
            print self.game.move_history
            print 'opponent made move {0} {1} {2}'.\
                format(*self.game.move_history[-1])
        print self.game
        print 'Make you move as player {0}'.format(self.game.half_moves)
        print '(1) apply card to slot, or (2) apply slot to card?'
        while True:
            direction = raw_input()
            if direction == '1':
                direction = LEFT_APP
                card = self.read_card()
                slot = self.read_slot()
                break
            if direction == '2':
                direction = RIGHT_APP
                slot = self.read_slot()
                card = self.read_card()
                break
            print 'enter 1 or 2'
            
        return (direction, slot, card)
    
    
class OfficialConnectorBot111():
    # it's not used because it's shit
    def __init__(self, game):
        self.game = game
        
    def send_last_turn(self):
        direction, slot, card = self.game.move_history[-1]
        #print>>sys.stderr, 'echoing opps move', direction, slot, card
        if direction == LEFT_APP:
            print 1
            print card
            print slot
        else:
            print 2
            print slot
            print card
        sys.stdout.flush()
        #print>>sys.stderr, 'echoed opps move', direction, slot, card
        
    def choose_move(self):
        # output opponent's previous move
        if len(self.game.move_history) > 0:
            self.send_last_turn()
        #print>>sys.stderr, 'reading official move'
        direction = int(raw_input())
        if direction == 1:
            direction = LEFT_APP
            card = raw_input()
            slot = int(raw_input())
        elif direction == 2:
            direction = RIGHT_APP
            slot = int(raw_input())
            card = raw_input()
        else:
            assert False
        card = card_by_name[card]
        #print>>sys.stderr, 'reading official move - ok', direction, slot, card
        return direction, slot, card

