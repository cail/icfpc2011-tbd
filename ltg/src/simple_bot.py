# not because bots are simple
# but because their interface is FUCKING SIMPLE

import random
import sys

from rules import cards, LEFT_APP, RIGHT_APP, SLOTS, card_by_name


__all__ = [
    'IdleBot',
    'RandomBot'
    'InteractiveBot',
    'PlaybackBot',
]

class Bot(object):
    def set_game(self, game):
        '''Should be called by all interpreters after construction
        so that bot creation routines shouldn't have to specify the game'''
        self.game = game
        return self # to allow call chaining
    def choose_move(self):
        # choose move happens after zombie phase, you you see most current state
        raise NotImplementedError()

class IdleBot(Bot):
    def choose_move(self):
        return (LEFT_APP, 0, cards.I)


class RandomBot(Bot):
    def __init__(self, rand_seed = None):
        self.rnd = random.Random(rand_seed)
        self.slots_range = range(10) + range(100, 105) + range(SLOTS - 10, SLOTS)        
    def choose_move(self):
        return (
            self.rnd.choice([LEFT_APP, RIGHT_APP]),
            self.rnd.choice(self.slots_range),
            self.rnd.choice(card_by_name.values()))


class InteractiveBot(Bot):
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
    

class PlaybackBot(Bot):
    def __init__(self, moves):
        self.moves = iter(moves)
    def choose_move(self):
        dir, slot, card = next(self.moves).split()
        if dir == '1':
            dir = 'l'
        elif dir == '2':
            dir = 'r'
        else:
            assert False
        slot = int(slot)
        card = card_by_name[card]
        return dir, slot, card

