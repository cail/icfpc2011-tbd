__all__ = [
    'SLOTS',
    'INITIAL_VITALITY',
    'MAX_APPLICATIONS',
    'MAX_TURNS',
    'LEFT_APP',
    'RIGHT_APP',
    'Function',
    'IntValue',
    'card_by_name',
    'Error',
    'Context',
    'apply',
    'card',
#    'zero',
#    'Function',
#    'Identity',
#    'K',
#    'S',
#    'Succ',
#    'Double',
#    'Get',
#    'Put',
#    'Attack',
]

SLOTS = 256
INITIAL_VITALITY = 10000
MAX_APPLICATIONS = 1000
MAX_TURNS = 10000 # REDUCED FOR TESTING (originally 10**5)

LEFT_APP = 'l'
RIGHT_APP = 'r'

class Error(Exception):
    pass

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
    # i'm deliberately making context required parameter,
    # so it won't be forgotten somewhere in cards by accident
    if context is not None:
        context.count_apply()
    return f.apply(arg, context)


# This part is a bit of a mess, conceptually: we use the same set of classes
# both for functions as received from input etc, and for functions being 
# evaluated. The problem is most obvious in case of 'zero'.
# Hopefully it wouldn't lead to scary bugs.

class Function(object):
    def apply(self, arg, context):
        raise NotImplementedError()
    def __str__(self):
        return self.canonical_name
    def partial_str(self, *args):
        return self.canonical_name + ''.join('({0})'.format(arg) for arg in args)


class IntValue(int): # not a Function -- otherwise it would break a lot of code below
    def __init__(self, value):
        self.value = value
    def apply(self, arg, context):
        raise Error('Attempt to apply an integer')
    def __str__(self):
        return str(self.value)


class Identity(Function):
    def apply(self, arg, context):
        return arg


class K(Function):
    def apply(self, arg, context):
        return K1(arg)


class K1(K):
    'K with one argument applied'
    def __init__(self, value):
        self.value = value
    def apply(self, arg, context):
        return self.value
    def __str__(self):
        return self.partial_str(self.value)
    
    
class S(Function):
    def apply(self, arg, context):
        return S1(arg)


class S1(S):
    def __init__(self, f):
        self.f = f
    def apply(self, arg, context):
        return S2(self.f, arg)
    def __str__(self):
        return self.partial_str(self.f)
    
    
class S2(S):
    def __init__(self, f, g):
        self.f = f
        self.g = g
    def apply(self, arg, context):
        h = apply(self.f, arg, context)
        y = apply(self.g, arg, context)
        return apply(h, y, context)
    def __str__(self):
        return self.partial_str(self.f, self.g)
    
    
class Succ(Function):
    canonical_name = 'succ'
    def apply(self, arg, context):
        if isinstance(arg, Function):
            raise Error('Succ applied to function')
        return IntValue(min(arg+1, 65535))
    
    
class Double(Function):
    canonical_name = 'dbl'
    def apply(self, arg, context):
        if isinstance(arg, Function):
            raise Error('Dbl applied to function')
        return IntValue(min(arg*2, 65535))
    

class Get(Function):
    canonical_name = 'get'
    def apply(self, arg, context):
        ensure_slot_number(arg)
        if context.game.proponent.vitalities[arg] <= 0:
            raise Error('Get applied to a dead slot number')
        return context.game.proponent.values[arg]

    
class Put(Function):
    canonical_name = 'put'
    def apply(self, arg, context):
        return card.I

    
class Attack(Function):
    canonical_name = 'attack'
    def apply(self, arg, context):
        return Attack1(arg)    
    
    
class Attack1(Attack):
    def __init__(self, i):
        self.i = i
    def apply(self, arg, context):
        return Attack2(self.i, arg)
    def __str__(self):
        return self.partial_str(self.i)


def ensure_slot_number(value):
    if isinstance(value, Function):
        raise Error('Using function as slot number')
    if not 0 <= value < SLOTS:
        raise Error('Slot number not in range')
    
class Attack2(Attack):
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
                max(0, opp.vitalities[SLOTS-self.j]-arg*9//10)
        
        return card.I
    
    def __str__(self):
        return self.partial_str(self.i, self.j)

class Inc(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        prop = context.game.proponent 
        if prop.vitalities[arg] > 0 and prop.vitalities[arg] < 65535:
            prop.vitalities[arg] += 1
        return card.I        

class Dec(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        opp = context.game.opponent 
        if opp.vitalities[SLOTS-arg] > 0:
            opp.vitalities[SLOTS-arg] -= 1
        return card.I        

class Help(Function):
    def apply(self, arg, context):
        return Help1(arg)    

class Help1(Function):
    def __init__(self, i):
        self.i = i
    def apply(self, arg, context):
        return Help2(self.i, arg)

class Help2(Function):
    def __init__(self, i, j):
        self.i = i
        self.j = j
    def apply(self, arg, context):
        
        prop = context.game.proponent
        
        ensure_slot_number(self.i)
        if isinstance(arg, Function):
            raise Error('help strength is a function')
        if arg > prop.vitalities[self.i]:
            raise Error('too strong help')
        prop.vitalities[self.i] -= arg
        
        ensure_slot_number(self.j) # after decreasing the source slot
        
        if prop.vitalities[self.j] > 0:
            prop.vitalities[self.j] = \
                min(65535, prop.vitalities[self.j]+arg*11//10)
        
        return card.I    

    def __str__(self):
        return self.partial_str(self.i, self.j)

class card(object):
    I = Identity()
    zero = IntValue(0)
    succ = Succ()
    dbl = Double()
    get = Get()
    put = Put()
    S = S()
    K = K()
    inc = Inc()
    dec = Dec()
    attack = Attack()
    help = Help()
    # copy = Copy()
    # revive = Revive()
    # zombie = Zombie()

card_by_name = dict((k, v) for k, v in card.__dict__.iteritems() if not k.startswith('_'))

def _init_canonical_names():
    for name, card in card_by_name.iteritems():
        card.__class__.canonical_name = name
_init_canonical_names()

def parse_commands(s):
    import re
    s = re.sub(r'^\s*\[(.*)\]\s*', r'\1', s) # remove brackets (if any)
    lst = []
    order_map = {'l':LEFT_APP, 'r':RIGHT_APP} 
    for cmd_s in s.split(','):
        cmd, order = cmd_s.split()
        lst.append((order_map[order], card_by_name[cmd])) 
    return lst
