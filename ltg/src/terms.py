
import sys

from pprint import pprint

from rules import card_by_name, cards
from rules import LEFT_APP, RIGHT_APP, apply
from rules import IntValue, Context, AbstractFunction
from abselim import eliminate_abstraction


App = tuple


def sequence_to_str(commands):
    return ', '.join('{0} {1}'.format(*command) for command in commands)
    
    
def parse_sequence(s):
    import re
    s = re.sub(r'^\s*\[(.*)\]\s*', r'\1', s) # remove brackets (if any)
    lst = []
    order_map = {'l':LEFT_APP, 'r':RIGHT_APP} 
    for cmd_s in s.split(','):
        cmd, order = cmd_s.split()
        lst.append((card_by_name[cmd], order_map[order])) 
    return lst


def eval_sequence(commands, start=cards.I, debug=False):
    get = AbstractFunction.create('get', IntValue)
    context = Context(None)
    state = start
    for cmd, side in commands:
        if cmd == cards.get: 
            cmd = get
        if side == 'r':
            state = apply(state, cmd, context)
        else:
            state = apply(cmd, state, context)
        if debug:
            print cmd, side, ':', state
    return state


def binarize_term(term):
    '(f, x, y) -> ((f, x), y), etc.'
    if isinstance(term, App):
        result = term[0]
        for t in term[1:]:
            result = (result, binarize_term(t))
        return result
    return term


def subterms(*terms):
    'in postorder'
    result = []
    visited = set()
    def rec(term):
        if term in visited:
            return
        if isinstance(term, App):
            left, right = term
            rec(left)
            rec(right)
        assert term not in visited
        visited.add(term)
        result.append(term)
    map(rec, terms)
    return result
 

def replace_leaf_subterm(template, pattern, term):
    if term == template:
        return pattern
    if isinstance(term, App):
        left, right = term
        return (replace_leaf_subterm(template, pattern, left), 
                replace_leaf_subterm(template, pattern, right))
    return term
 
assert replace_leaf_subterm((1,2), (3, 4), ((1, 2), (3, 4))) == ((3, 4), (3, 4))
     

def calc_costs_and_weights(*terms):
    st = subterms(*terms)
    cost = {}
    for t in st:
        if isinstance(t, App):
            left, right = t
            if cost[left] == 1:
                cost[t] = cost[right]+1
            else:
                cost[t] = cost[left]+3*(cost[right]-1)+1
        else:
            cost[t] = 1
    weight = dict.fromkeys(st, 0)
    for t in terms:
        weight[t] += 1
    for t in reversed(st):
        if isinstance(t, App):
            left, right = t
            weight[left] += weight[t]
            if cost[left] == 1:
                weight[right] += weight[t]
            else:
                weight[right] += weight[t]*3
    return cost, weight


def sequential_cost(term):
    cost, _ = calc_costs_and_weights(term)
    return cost[term]

def optimal_subterm(register_cost, *terms):
    '''(subterm, advantage)
    
    Find best subterm to put to temporary slot.
    Don't use result if advantage <= 0
    '''
    
    # it's can underestimate advantage because
    # we don't take into account that term may become sequential
    
    # or maybe it's fine...
    
    cost, weight = calc_costs_and_weights(*terms)
    def key(t):
        return (cost[t]-register_cost)*weight[t]-cost[t]
    result = max(cost.keys(), key=key)
    return result, key(result)


def check_term(term):
    if isinstance(term, App):
        left, right = term
        check_term(left)
        check_term(right)
    else:
        assert term in card_by_name.values()
    
    
def term_to_str(term):
    if isinstance(term, App):
        return '({0} {1})'.format(*map(term_to_str, term))
    else:
        return str(term) 
    

def number_term(n):
    assert 0 <= n < 65536
    
    if n == 65535:
        # use saturation
        result = (cards.succ, cards.zero)
        for _ in range(16):
            result = (cards.dbl, result)
        return result
        
    if n == 0:
        return cards.zero
    if n%2 == 1:
        return (cards.succ, number_term(n-1))
    return (cards.dbl, number_term(n//2))


scnt_memoized = dict()


def scnt(i):
    if not i in scnt_memoized:
        scnt_memoized[i] = sequential_cost(number_term(i))
    return scnt_memoized[i]


def number_term_with_min_seq_cost(n, m):
    n = min(max(0, n), 65535)
    m = min(max(0, m), 65535)
    r, rc = n, scnt(n)
    for i in range(n, m):
        ic = scnt(i)
        if ic <= rc:
            r, rc = i, ic
    return r


def canonical_sequence(seq):
    if len(seq) == 0 or seq[0][1] == 'l':
        seq = [(cards.I, 'r')]+seq
    assert seq[0][1] == 'r'
    return seq
 
 
def apply_sequences(left, right):
    'return sequence equivalent to result of application left to right'
    
    right = canonical_sequence(right)
    t = [(right[0][0], 'r')]
    for atom, side in right[1:]:
        if side == 'l': # fj's method
            t = [(cards.K, 'l'), (cards.S, 'l'), (atom, 'r')] + t
        else: # fj's method, modified
            t = [(cards.K, 'l'), (cards.S, 'l')] + t + [(atom, 'r')]
    return left+t


def term_to_sequence(term):
    #print>>sys.stderr, sequential_cost(term)
    if isinstance(term, App):
        left, right = term
        if not isinstance(left, App):
            result = term_to_sequence(right)+[(left, 'l')]
        else:
            result = apply_sequences(term_to_sequence(left), term_to_sequence(right))
    else:
        result = [(term, 'r')]
    #TODO: comment for performance
    assert sequential_cost(term) == len(result)
    return result


def parse_term(s, locals={}):
    s = s.replace(' ', ', ')
    for card_name in card_by_name:
        s = s.replace(card_name, 'cards.'+card_name)
    return binarize_term(eval(s, globals(), locals))


def parse_lambda(s, locals={}):
    return parse_term(eliminate_abstraction(s), locals)


def value_to_term(value):
    if isinstance(value, IntValue):
        return int(value)
    # we depend on the fact that all functions with no arguments are cards themselves
    if value.arg0 is None:
        return value
    card = card_by_name[value.canonical_name] # get corresponding card
    r = (card, value_to_term(value.arg0))
    if value.arg1 is not None:
        r = (r, value_to_term(value.arg1))
    return r


def fold_numbers(term):
    if isinstance(term, App):
        left, right = term
        left = fold_numbers(left)
        right = fold_numbers(right)
        if isinstance(right, int):
            right = int(right)
            if left == cards.succ:
                return min(right+1, 65535)
            elif left == cards.dbl:
                return min(right*2, 65535)
        return (left, right)
    if isinstance(term, int):
        return int(term)
    return term
    

def unfold_numbers(term):
    if isinstance(term, App):
        left, right = term
        return (unfold_numbers(left), unfold_numbers(right))
    if type(term) == int: # not isinstance, because IntValue derives from int
        return number_term(term)
    return term


def is_subterm_eager(subterm, term):
    '''return whether all ocurences of subterm will be evaluated during term 
    construction using term_to_sequence
    '''
    return False


if __name__ == '__main__':
    t = ((cards.get, 65535), (cards.get, 5))
    assert fold_numbers(unfold_numbers(t)) == t

    #print term_to_str(t)
    pprint(t)
    
    t = unfold_numbers(t)
    
    t = binarize_term(t)
    print 'optimal subterm', optimal_subterm(3, t)
    s = term_to_sequence(t)
    
    print 'sequence of length', len(s)
    print sequence_to_str(s)
    
    try:
        print eval_sequence(s)
    except Exception as e:
        print '----'
        print 'Error', e
        print "don't worry, evaluation is not fully supported BECAUSE."


    
