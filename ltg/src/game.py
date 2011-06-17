from rules import *

__all__ = [
    'Game',
]


class Player(object):
    def __init__(self):
        self.vitalities = [INITIAL_VITALITY]*SLOTS
        self.values = [card.I]*SLOTS
    def has_alive_slots(self):
        return any(v > 0 for v in self.vitalities)
    def num_alive_slots(self):
        return sum(1 for v in self.vitalities if v > 0)
    def has_zombies(self):
        return -1 in self.vitalities    

    
class Game(object):
    def __init__(self, silent=True):
        self.silent = silent
        self.players = [Player(), Player()]
        self.proponent, self.opponent = self.players
        self.half_moves = 0

        #self.proponent.vitalities[13] = -1
        #self.proponent.values[13] = zero
        
    def is_finished(self):
        return \
            self.half_moves >= MAX_TURNS*2 or \
            any(not p.has_alive_slots() for p in self.players)
            
    def zombie_phase(self):
        prop = self.proponent
        if not self.silent:
            print 'zombie phase'
        for i in range(SLOTS):
            if prop.vitalities[i] == -1:
                if not self.silent:
                    print 'zombie in slot', i, 'is applied to I'
                z = prop.values[i]
                context = Context(self, zombie=True)
                try:
                    _ = apply(z, card.I, context) # not interested in result
                except Error as e:
                    if not self.silent:
                        print e
                prop.values[i] = card.I
                prop.vitalities[i] = 0
                if not self.silent:
                    print 'zombie is rested'
            
    def make_half_move(self, direction, slot, card):
        import warnings
         
        if self.proponent.has_zombies():
            self.zombie_phase()
            
        self.apply(
            slot, 
            card, 
            direction)
        self.half_moves += 1
        self.proponent, self.opponent = self.opponent, self.proponent
        
    def apply(self, slot, card, direction):
        'return None or error'
        context = Context(self)
        try:
            if self.proponent.vitalities[slot] <= 0:
                raise Error('application involving dead slot')
            s = self.proponent.values[slot]
            if direction is LEFT_APP:
                result = apply(card, s, context)
            elif direction is RIGHT_APP:
                result = apply(s, card, context)
            else:
                assert False
            self.proponent.values[slot] = result
        except Error as e:
            if not self.silent:
                print 'Error:' + str(e)
            self.proponent.values[slot] = card.I
            
        
                
    def __str__(self):
        result = []
        for i in range(2):
            result.append('player {0} slots:'.format(i))
            player = self.players[i]
            for slot in range(SLOTS):
                vit = player.vitalities[slot]
                value = player.values[slot]
                if vit != INITIAL_VITALITY or \
                   value != card.I:
                    result.append('    {0:03}: ({1}, {2})'.format(slot, vit, value))
        return '\n'.join(result)

