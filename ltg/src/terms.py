from rules import card_by_name, cards
from rules import LEFT_APP, RIGHT_APP, card_by_name, apply, cards
from rules import IntValue, Context, AbstractFunction, Error

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
    if n == 0:
        return cards.zero
    if n%2 == 1:
        return (cards.succ, number_term(n-1))
    return (cards.dbl, number_term(n//2))


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
    if isinstance(term, App):
        left, right = term
        return apply_sequences(term_to_sequence(left), term_to_sequence(right))
    return [(term, 'r')]


if __name__ == '__main__':
    t = ((cards.get, number_term(4)), (cards.get, number_term(5))) 
    print term_to_str(t)
    s = term_to_sequence(t)
    print 'sequence of length', len(s)
    print sequence_to_str(s)
    print eval_sequence(s)
    
    