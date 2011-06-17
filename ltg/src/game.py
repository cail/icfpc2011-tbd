SLOTS = 256
INITIAL_VITALITY = 10000
MAX_APPLICATIONS = 1000


class IntValue(int):
    pass

zero = IntValue(0)        
        

class Error(Exception):
    pass


# functions module in turn imports SLOTS etc. from game module, so...
from functions import *


class Player(object):
    def __init__(self):
        self.vitalities = [INITIAL_VITALITY]*SLOTS
        self.values = [Identity.instance]*SLOTS
        
    
class Game(object):
    def __init__(self):
        self.players = [Player(), Player()]
        self.proponent, self.opponent = self.players
        self.half_moves = 0
        
    def apply(self, slot, card, direction):
        context = Context(self)
        s = self.proponent.values[slot]
        try:
            if direction == 'left':
                result = apply(card, s, context)
            elif direction == 'right':
                result = apply(s, card, context)
            else:
                assert False
            self.proponent.values[slot] = result
        except Error as e:
            print e
            self.proponent.values[slot] = Identity.instance
        
    def swap_players(self):
        self.proponent, self.opponent = self.opponent, self.proponent
        
    def __str__(self):
        result = []
        for i in range(2):
            result.append('player {0} slots:'.format(i))
            player = self.players[i]
            for slot in range(SLOTS):
                vit = player.vitalities[slot]
                value = player.values[slot]
                if vit != INITIAL_VITALITY or \
                   value != Identity.instance:
                    result.append('    {0:03}: ({1}, {2})'.format(slot, vit, value))
        return '\n'.join(result)
    
    
if __name__ == '__main__':
    game = Game()
    print game
    game.apply(0, zero, 'right')
    game.apply(1, Succ.instance, 'right')
    game.apply(1, zero, 'right')
    game.apply(2, K.instance, 'left')
    print game