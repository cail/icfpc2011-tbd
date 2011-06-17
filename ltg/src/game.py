
SLOTS = 256
INITIAL_VITALITY = 10000
MAX_APPLICATIONS = 1000

class IntValue(int):
    pass

zero = IntValue(0)


def apply(f, arg, context):
    if isinstance(f, IntValue):
        raise Error('Attempt to apply integer')
    context.count_apply()
    return f.apply(arg, context)


class Function(object):
    def apply(self, arg, context):
        raise NotImplementedError()
    def __str__(self):
        type_name = type(self).__name__
        if self.__dict__ == {}:
            return type_name
        return '{0}{1}'.format(type_name, self.__dict__)
        #return ''
    

class Identity(Function):
    def apply(self, arg, context):
        return arg
    def __str__(self):
        return 'Id'
Identity.instance = Identity()


class K(Function):
    def apply(self, arg, context):
        return K1(arg)
K.instance = K()

    
class K1(Function):
    'K with one argument applied'
    def __init__(self, value):
        self.value = value
    def apply(self, arg, context):
        return self.value
    def __str__(self):
        return '{0}[{1}]'.format(type(self).__name__, self.value)
    
    
class Succ(Function):
    def apply(self, arg, context):
        if isinstance(arg, Function):
            raise Error('Succ applied to function')
        return IntValue(arg+1)
Succ.instance = Succ()
    
    
class Context(object):
    def __init__(self, game):
        self.app_limit = MAX_APPLICATIONS
        self.game = game
    def count_apply(self):
        self.app_limit -= 1
        if self.app_limit < 0:
            raise Error('application limit exceeded')


class Error(Exception):
    pass



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