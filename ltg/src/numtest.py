
from terms import *

for i in range(255):
    print i, sequential_cost(number_term(i)), sequential_cost(number_term(255 - i))

