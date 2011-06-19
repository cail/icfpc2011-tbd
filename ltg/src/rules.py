from collections import defaultdict, namedtuple
import sys

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
    'cards',
]

sys.setrecursionlimit(8000)

SLOTS = 256
MAX_SLOT = SLOTS - 1
INITIAL_VITALITY = 10000
MAX_APPLICATIONS = 1000
MAX_TURNS = 100000

LEFT_APP = 'l'
RIGHT_APP = 'r'

MEMOIZE_FUNCTIONS = True

class Error(Exception):
    pass

class Context(object):
    def __init__(self, game, zombie=False):
        self.app_limit = MAX_APPLICATIONS
        self.side_effects = 0
        self.game = game
        self.zombie = zombie
    def count_apply(self, n=1):
        self.app_limit -= n
        if self.app_limit < 0:
            raise Error('application limit exceeded')
    def count_side_effect(self):
        # including read side effects
        self.side_effects += 1


apply_cache = {}

def apply(f, arg, context):
    pair = f, arg
    if pair in apply_cache:
        #print 'application recalled'
        result, application_count = apply_cache[pair]
        context.count_apply(application_count)
        return result
    
    app_limit_before = context.app_limit
    side_effects_before = context.side_effects
    
    context.count_apply()
    result = f.apply(arg, context)
    
    if context.side_effects == side_effects_before:
        # we only memoize functions without side effects
        assert context.app_limit >= 0
        application_count = app_limit_before-context.app_limit
        apply_cache[pair] = result, application_count
        #print 'application remembered'
    return result


# This part is a bit of a mess, conceptually: we use the same set of classes
# both for functions as received from input etc, and for functions being 
# evaluated. The problem is most obvious in case of 'zero'.
# Hopefully it wouldn't lead to scary bugs.

function_cache = defaultdict(dict)

class Function(object):
    # Note! Functions lack structural hash and comparisons,
    # because it's convenient for memoization.
    # Reference inequality does not guarantee structural inequality.
    # So far we do not need structural comparison at all.
    # As a quick hack one can compare str()'s.
    
    __slots__ = ['arg0', 'arg1']
    # canonical_name = 'BaseFunction' # all canonical names are set in _init_canonical_names
    
    def __new__(cls, arg0, arg1):
        obj = object.__new__(cls)
        obj.arg0 = arg0
        obj.arg1 = arg1
        return obj
        
    if MEMOIZE_FUNCTIONS:
        @classmethod
        def create(cls, arg0 = None, arg1 = None):
            # TODO: put memoization shit into separate module
            cache = function_cache[cls]
            args = (arg0, arg1)
            if args not in cache:
                cache[args] = cls(arg0, arg1)
            return cache[args]
    else:
        @classmethod
        def create(cls, arg0 = None, arg1 = None):
            return cls(arg0, arg1)
        
    def apply(self, arg, context):
        raise NotImplementedError()
    
    def __str__(self):
        def generate():
            yield self.canonical_name
            a0, a1 = self.arg0, self.arg1
            if a0 is None: return # fast path, no outer parentheses
            close_paren = ')'
            if a1 is not None:
                stack = [close_paren, a1, close_paren, a0]
            else:
                stack = [close_paren, a0]
            # pseudorecursion
            while stack:
                it = stack.pop()
                if it is close_paren:
                    yield it
                    continue
                yield '(' + it.canonical_name
                a0, a1 = it.arg0, it.arg1
                if a0 is not None:
                    if a1 is not None:
                        stack.append(close_paren)
                        stack.append(a1)
                    stack.append(close_paren)
                    stack.append(a0)
        return ''.join(generate())
    
    def __repr__(self):
        return str(self)


class AbstractFunction(Function):
    # crazy hacks follow!
    __slots__ = ['canonical_name', 'required_type']
    def __new__(cls, name, required_type=None):
        obj = Function.__new__(cls, None, None)
        obj.canonical_name = name
        obj.required_type = required_type
        return obj
        
    def apply(self, arg, context):
        t = self.required_type
        if t is not None and not isinstance(arg, t):
            raise Error('wrong type')
        return AbstractFunction('{0}({1})'.format(self.canonical_name, arg))
    

class IntValue(int): # not a Function -- because it's not!
    # we are not memoizing ints, so no need for create function
    arg0 = None
    arg1 = None
    @property
    def canonical_name(self):
        if self == 0:
            return 'zero'
        return int.__str__(self)
    def apply(self, arg, context):
        raise Error('Attempt to apply an integer')
    def __str__(self):
        return self.canonical_name
    def __repr__(self):
        return self.canonical_name


class Identity(Function):
    def apply(self, arg0, context):
        return arg0


class K(Function):
    def apply(self, arg, context):
        return K1.create(arg)


class K1(K):
    # K with one argument applied
    def apply(self, arg, context):
        return self.arg0
    
    
class S(Function):
    def apply(self, arg, context):
        return S1.create(arg)


class S1(S):
    def apply(self, arg, context):
        return S2.create(self.arg0, arg)
    
    
class S2(S):
    def apply(self, arg, context):
        h = apply(self.arg0, arg, context)
        y = apply(self.arg1, arg, context)
        return apply(h, y, context)
    
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
    

def ensure_slot_number(value):
    if isinstance(value, Function):
        raise Error('Using function as slot number')
    if not 0 <= value < SLOTS:
        raise Error('Slot number not in range')
    
    
class Get(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        context.count_side_effect()
        if context.game.proponent.vitalities[arg] <= 0:
            raise Error('Get applied to a dead slot number')
        return context.game.proponent.values[arg]

    
class Put(Function):
    def apply(self, arg, context):
        return cards.I


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
        return Attack1.create(arg)    
    
    
class Attack1(Attack):
    def apply(self, arg, context):
        return Attack2.create(self.arg0, arg)

    
class Attack2(Attack):
    def apply(self, arg, context):
        prop = context.game.proponent
        opp = context.game.opponent
        
        if isinstance(arg, Function):
            raise Error('attack strength is a function')
        
        ensure_slot_number(self.arg0)
        context.count_side_effect()
        if arg > prop.vitalities[self.arg0]:
            raise Error('too strong attack')
        prop.vitalities[self.arg0] -= arg
        
        ensure_slot_number(self.arg1) # after decreasing our own slot
        
        if context.zombie:
            increase_vitality(opp, MAX_SLOT-self.arg1, arg*9//10)
        else:
            decrease_vitality(opp, MAX_SLOT-self.arg1, arg*9//10)
            
        return cards.I


class Inc(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        context.count_side_effect()
        prop = context.game.proponent
        if context.zombie:
            decrease_vitality(prop, arg)
        else:
            increase_vitality(prop, arg)
        return cards.I        


class Dec(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        context.count_side_effect()
        opp = context.game.opponent
        if context.zombie: 
            increase_vitality(opp, MAX_SLOT - arg)
        else:
            decrease_vitality(opp, MAX_SLOT - arg)
        return cards.I        


class Help(Function):
    def apply(self, arg, context):
        return Help1.create(arg)    


class Help1(Help):
    def apply(self, arg, context):
        return Help2.create(self.arg0, arg)


class Help2(Help):
    def apply(self, arg, context):
        prop = context.game.proponent
        
        if isinstance(arg, Function):
            raise Error('help strength is a function')
        
        ensure_slot_number(self.arg0)
        context.count_side_effect()
        if arg > prop.vitalities[self.arg0]:
            raise Error('too strong help')
        prop.vitalities[self.arg0] -= arg
        
        ensure_slot_number(self.arg1) # after decreasing the source slot
        
        if context.zombie:
            decrease_vitality(prop, self.arg1, arg*11//10)
        else:
            increase_vitality(prop, self.arg1, arg*11//10)
        
        return cards.I


class Copy(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        context.count_side_effect()
        return context.game.opponent.values[arg]


class Revive(Function):
    def apply(self, arg, context):
        ensure_slot_number(arg)
        context.count_side_effect()
        if context.game.proponent.vitalities[arg] <= 0:
            context.game.proponent.vitalities[arg] = 1
        return cards.I
    

class Zombie(Function):
    def apply(self, arg, context):
        return Zombie1.create(arg)    


class Zombie1(Zombie):
    def apply(self, arg, context):
        ensure_slot_number(self.arg0)
        context.count_side_effect()
        opp = context.game.opponent
        if opp.vitalities[MAX_SLOT-self.arg0] > 0:
            raise Error('can\'t zombify a living slot')
        opp.values[MAX_SLOT-self.arg0] = arg
        opp.vitalities[MAX_SLOT-self.arg0] = -1
        return cards.I


class cards(object):
    I = Identity.create()
    zero = IntValue(0)
    succ = Succ.create()
    dbl = Double.create()
    get = Get.create()
    put = Put.create()
    S = S.create()
    K = K.create()
    inc = Inc.create()
    dec = Dec.create()
    attack = Attack.create()
    help = Help.create()
    copy = Copy.create()
    revive = Revive.create()
    zombie = Zombie.create()


card_by_name = dict((k, v) for k, v in cards.__dict__.iteritems() if not k.startswith('_'))

def _init_canonical_names():
    for name, card in card_by_name.iteritems():
        cls = card.__class__ 
        if not hasattr(cls, 'canonical_name'): # bc IntValue provides its own for example
            cls.canonical_name = name
    Function.canonical_name = 'BaseFunction'
_init_canonical_names()
