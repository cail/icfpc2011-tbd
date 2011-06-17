from itertools import *
from random import random

import game
from functions import *

if __name__ == '__main__':
    x, y, z, t = map(AbstractFunction, 'XYZT')
    
    desired = apply(apply(x, y, None), apply(z, t, None), None)
    desired = str(desired)
    print 'search for', desired
    
    allowed_functions = [x, y, z, t, Identity.instance, K.instance, S.instance]
    
    possible_steps = list(product(allowed_functions, 'lr'))
    
    def steps_to_str(steps):
        return '[{0}]'.format(', '.join(str(f)+' '+side for f, side in steps))

    steps = []
    
    cnt = 0
    
    def rec(cur, depth):
        global cnt
        if str(cur) == desired:
            print 'found'
            print steps_to_str(steps), cur
            exit()
        if depth == 0:
            return
        cnt += 1
        if cnt % 10000 == 0:
            print cnt
        for f, side in possible_steps:
            if side == 'r':
                next = apply(cur, f, None)
            else:
                next = apply(f, cur, None)
            steps.append((f, side))
            rec(next, depth-1)
            steps.pop()
        
    for i in range(1, 10):
        print i
        rec(Identity.instance, i)
    
    