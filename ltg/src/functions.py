from game import IntValue, Error, SLOTS, MAX_APPLICATIONS


__all__ = [
    'Context',
    'apply',
    'Function',
    'Identity',
    'K',
    'S',
    'Succ',
    'Double',
    'Attack',
]


class Context(object):
    def __init__(self, game, zombie=False):
        self.app_limit = MAX_APPLICATIONS
        self.game = game
        self.zombie = zombie
    def count_apply(self):
        self.app_limit -= 1
        if self.app_limit < 0:
            raise Error('application limit exceeded')


def apply(f, arg, context):
    if isinstance(f, IntValue):
        raise Error('Attempt to apply integer')
    # i'm deliberately making context required parameter,
    # so it won't be forgotten somewhere in cards by accident
    if context is not None:
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
    
    
class S(Function):
    def apply(self, arg, context):
        return S1(arg)
S.instance = S()        


class S1(Function):
    def __init__(self, f):
        self.f = f
    def apply(self, arg, context):
        return S2(self.f, arg)
    
    
class S2(Function):
    def __init__(self, f, g):
        self.f = f
        self.g = g
    def apply(self, arg, context):
        h = apply(self.f, arg, context)
        y = apply(self.g, arg, context)
        return apply(h, y, context)
    
    
class Succ(Function):
    def apply(self, arg, context):
        if isinstance(arg, Function):
            raise Error('Succ applied to function')
        return IntValue(min(arg+1, 65535))
Succ.instance = Succ()
    
    
class Double(Function):
    def apply(self, arg, context):
        if isinstance(arg, Function):
            raise Error('Succ applied to function')
        return IntValue(min(arg*2, 65535))
Double.instance = Double()
    
    
class Attack(Function):
    def apply(self, arg, context):
        return Attack1(arg)    
Attack.instance = Attack()
    
    
class Attack1(Function):
    def __init__(self, i):
        self.i = i
    def apply(self, arg, context):
        return Attack2(self.i, arg)
        

def ensure_slot_number(value):
    if isinstance(value, Function):
        raise Error('Using function as slot number')
    if not 0 <= value < SLOTS:
        raise Error('Slot number not in range')

    
class Attack2(Function):
    def __init__(self, i, j):
        self.i = i
        self.j = j
        
    def apply(self, arg, context):
        assert not context.zombie, 'TODO'
        
        prop = context.game.proponent
        opp = context.game.opponent
        
        ensure_slot_number(self.i)
        if isinstance(arg, Function):
            raise Error('attack strength is a function')
        if arg > prop.vitalities[self.i]:
            raise Error('too strong attack')
        prop.vitalities[self.i] -= arg
        
        ensure_slot_number(self.j) # after decreasing our own slot
        
        if opp.vitalities[SLOTS-self.j] > 0:
            opp.vitalities[SLOTS-self.j] = \
                IntValue(max(0, opp.vitalities[SLOTS-self.j]-arg*9//10))
