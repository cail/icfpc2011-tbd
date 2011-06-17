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
MAX_SLOT = SLOTS - 1
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
    def apply(self, arg, context):
        if isinstance(arg, Function):
            raise Error('Succ applied to function')
        return IntValue(min(arg+1, 65535))
    
    
class Double(Function):
    def apply(self, arg, context):
        if isinstance(arg, Function):
            raise Error('Dbl applied to function')
        return IntValue(min(arg*2, 65535))
    

class Get(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        if context.game.proponent.vitalities[arg] <= 0:
            raise Error('Get applied to a dead slot number')
        return context.game.proponent.values[arg]

    
class Put(Function):
    def apply(self, arg, context):
        return card.I

def increase_vitality(player, slot, amount=1):
    vitality = player.vitalities[slot]
    if vitality > 0:
        player.vitalities[slot] = min(65535, vitality + amount)

def decrease_vitality(player, slot, amount=1):
    vitality = player.vitalities[slot]
    if vitality > 0:
        player.vitalities[slot] = max(0, vitality - amount)

    
class Attack(Function):
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
        prop = context.game.proponent
        opp = context.game.opponent
        
        ensure_slot_number(self.i)
        if isinstance(arg, Function):
            raise Error('attack strength is a function')
        if arg > prop.vitalities[self.i]:
            raise Error('too strong attack')
        prop.vitalities[self.i] -= arg
        
        ensure_slot_number(self.j) # after decreasing our own slot
        
        if context.zombie:
            increase_vitality(opp, MAX_SLOT-self.j, arg*9//10)
        else:
            decrease_vitality(opp, MAX_SLOT-self.j, arg*9//10)
            
        return card.I
    
    def __str__(self):
        return self.partial_str(self.i, self.j)

class Inc(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        prop = context.game.proponent
        if context.zombie:
            decrease_vitality(prop, arg)
        else:
            increase_vitality(prop, arg)
        return card.I        

class Dec(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        opp = context.game.opponent
        if context.zombie: 
            increase_vitality(opp, MAX_SLOT - arg)
        else:
            decrease_vitality(opp, MAX_SLOT - arg)
        return card.I        

class Help(Function):
    def apply(self, arg, context):
        return Help1(arg)    

class Help1(Function):
    def __init__(self, i):
        self.i = i
    def apply(self, arg, context):
        return Help2(self.i, arg)
    def __str__(self):
        return self.partial_str(self.i)

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
        
        if context.zombie:
            decrease_vitality(prop, self.j, arg*11//10)
        else:
            increase_vitality(prop, self.j, arg*11//10)
        
        return card.I    

    def __str__(self):
        return self.partial_str(self.i, self.j)

class Copy(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        return context.game.opponent.values[arg]

class Revive(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        if context.game.proponent.vitalities[arg] <= 0:
            context.game.proponent.vitalities = 1
        return card.I

class Zombie(Function):
    def apply(self, arg, context):
        return Zombie1(arg)    

class Zombie1(Function):
    def __init__(self, i):
        self.i = i
    def apply(self, arg, context):
        ensure_slot_number(self.i)
        opp = context.game.opponent
        if opp.vitalities[MAX_SLOT-self.i] > 0:
            raise Error('can\'t zombify a living slot')
        opp.values[MAX_SLOT-self.i] = arg
        opp.vitalities[MAX_SLOT-self.i] = -1
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
    copy = Copy()
    revive = Revive()
    zombie = Zombie()

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
        lst.append((card_by_name[cmd], order_map[order])) 
    return lst
