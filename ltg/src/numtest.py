
from terms import *

for i in range(31000, 45000):
    if sequential_cost(number_term(i)) < 19:
        print i, sequential_cost(number_term(i)) #, sequential_cost(number_term(255 - i))

