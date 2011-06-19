from itertools import *
from time import clock
import sys

from rules import cards, AbstractFunction, Error, IntValue, Context, apply
import terms

if __name__ == '__main__':
    part = '1/1'
    if len(sys.argv) > 1:
        part = sys.argv[1]
    our_part, num_parts = map(int, part.split('/'))
    our_part -= 1
    
    x, y, z, t, r = map(AbstractFunction.create, 'XYZTR')
    get = AbstractFunction.create('get', IntValue)
    
    #desired = set([
    #    'get({0})(get({1}))'.format(i, j) 
    #    for i in range(4) for j in range(4)
    #    ])
    desired = set(['numbers'])
    print 'search for', desired, 'part', part
    
    allowed_functions = [
        #x, y, z, #t,
        #get,
        cards.zero, cards.succ, cards.dbl,
        #cards.put, # useless combinator? 
        cards.I, cards.K, cards.S]
    
    possible_steps = [(f, dir) for dir in 'rl' for f in allowed_functions]
    
    def steps_to_str(steps):
        return '[{0}]'.format(', '.join(str(f)+' '+side for f, side in steps))

    steps = []
    
    cnt = 0
    
    context = Context(None)
    
    optimized_numbers = set()
    
    def rec(cur, depth):
        global cnt
        scur = str(cur)
        
        if scur.isdigit() and scur not in optimized_numbers:
            t = terms.number_term(int(scur))
            cost = terms.sequential_cost(t)
            if cost > len(steps):
                print len(steps), steps_to_str(steps), '->', scur
            optimized_numbers.add(scur)
            
        if scur in desired:
            print len(steps), steps_to_str(steps), '->', scur
            desired.remove(scur)
            if len(desired) == 0:
                print 'Done. Press enter to exit'
                raw_input()
                exit()
        if depth == 0:
            return
        cnt += 1
        if cnt % 500000 == 0:
            print cnt
        for i, (f, side) in enumerate(possible_steps):
            if len(steps) == 0 and i%num_parts != our_part:
                continue
            try:
                context.app_limit = 30
                if side == 'r':
                    next = apply(cur, f, context)
                else:
                    next = apply(f, cur, context)
            except Error as e:
                continue
            #except Exception as e:
            #    print steps_to_str(steps+[(f, side)])
            #    print e
            #    raise e
            #    exit()
            steps.append((f, side))
            rec(next, depth-1)
            steps.pop()
        
    start = clock()
    for i in range(1, 20):
        print i, clock()-start
        rec(cards.I, i)
        

    