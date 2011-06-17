from game import Game
from rules import parse_commands, apply, card, Context, Function, Error
from rules import IntValue
from pprint import pprint
 
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

#game = Game(silent=False)

def generate_get_i_get_j_command(i, j):
    return ', '.join(['zero r'] + 
                     ['succ l'] * i +
                     ['get l'] +
                     ['K l', 'S l', 'get r'] +
                     ['K l', 'S l', 'succ r'] *j + 
                     ['zero r'])
s = generate_get_i_get_j_command(3, 7)
commands = parse_commands(s)
pprint(commands)

context = Context(None)

state = cards.I

for cmd, side in commands:
    if cmd == cards.get: 
        cmd = AbstractFunction('get', IntValue) 
    if side == 'r':
        state = apply(state, cmd, context)
    else:
        state = apply(cmd, state, context)
    print cmd, side, ':', state
