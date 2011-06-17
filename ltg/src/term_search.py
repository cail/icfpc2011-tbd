from itertools import *
from random import random
from time import clock

from rules import *

class AbstractFunction(Function):
    def __init__(self, name, required_type=None):
        self.name = name
        self.required_type = required_type
    def apply(self, arg, context):
        t = self.required_type
        if t is not None and not isinstance(arg, t):
            raise Error('wrong type')
        return AbstractFunction('({0} {1})'.format(self.name, arg))
    def __str__(self):
        return self.name


if __name__ == '__main__':
    x, y, z, t = map(AbstractFunction, 'XYZT')
    get = AbstractFunction('get', required_type=IntValue)
    
    desired = set([
        '((get {0}) (get {1}))'.format(i, j) 
        for i in range(4) for j in range(4)
        ])
    print 'search for', desired
    
    allowed_functions = [
        #x, y, z, t, 
        get,
        card.zero, card.succ, card.dbl, 
        card.I, card.K, card.S]
    
    possible_steps = list(product(allowed_functions, 'lr'))
    
    def steps_to_str(steps):
        return '[{0}]'.format(', '.join(str(f)+' '+side for f, side in steps))

    steps = []
    
    cnt = 0
    
    context = Context(None)
    
    def rec(cur, depth):
        global cnt
        if str(cur) in desired:
            print 'found', steps_to_str(steps), '->', cur
            desired.remove(str(cur))
            if len(desired) == 0:
                exit()
        if depth == 0:
            return
        cnt += 1
        if cnt % 100000 == 0:
            print cnt
        for f, side in possible_steps:
            try:
                context.app_limit = 30
                if side == 'r':
                    next = apply(cur, f, context)
                else:
                    next = apply(f, cur, context)
            except Error as e:
                continue
            except Exception as e:
                print steps_to_str(steps+[(f, side)])
                print e
                exit()
            steps.append((f, side))
            rec(next, depth-1)
            steps.pop()
        
    start = clock()
    for i in range(1, 20):
        print i, clock()-start
        rec(card.I, i)
    
    