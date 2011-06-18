import html
import string
import sys

import rules
from game import Game

TABLE_WIDTH = 16
STEPS_PER_PAGE = 100

def is_init(player, slot):
    return player.vitalities[slot] == rules.INITIAL_VITALITY and \
           player.values[slot] == rules.cards.I

def cell(h, player, slot):
    with (h.td(klass='active') if not is_init(player, slot) else h.td):
        h.text(str(player.vitalities[slot]))
        h.br
        h.text(str(player.values[slot]))
        
def table(h, player):
    with h.table(border='1') as t:
        for row in xrange(rules.SLOTS / TABLE_WIDTH):
            with t.tr() as r:
                for col in xrange(TABLE_WIDTH):
                    if row * TABLE_WIDTH + col >= rules.SLOTS:
                        break
                    cell(r, player, row * TABLE_WIDTH + col)

class ParseError(Exception):
    pass

def read_move(line):
    try:
        direction, slot, card = string.split(line)
        direction = int(direction)
        slot = int(slot)
    except ValueError:
        raise ParseError("Incorrect input format")
    
    if direction not in [1, 2]:
        raise ParseError("Illegal direction")
    
    direction = {1:rules.LEFT_APP, 2:rules.RIGHT_APP}[direction]
    
    try:
        card = rules.card_by_name[card]
    except KeyError:
        raise ParseError("Unrecognized card")
    
    return (direction, slot, card)

def process_move(h, game, move):
    direction, slot, card = move
    if direction == rules.LEFT_APP:
        move_descr = 'card %s to slot %d' % (card.canonical_name, slot)
    else:
        move_descr = 'slot %d to card %s' % (slot, card.canonical_name)
        
    h.h2('Turn %d. Player %d applies %s' % (game.half_moves//2, game.half_moves%2, move_descr))
    game.make_half_move(*move)
    with h.table.tr:
            table(h.td, game.players[0])
            h.td(width='20')
            table(h.td, game.players[1])

def write_page(h, number, name):
    number = '' if number == 0 else str(number)
    filename = name + number + '.html'
    css = '<style type="text/css">table{font-size: smaller;} .active{background-color:#DDDDDD}</style>\n'
    with open(filename, 'w') as f:
        f.write("<head>\n"+css+"</head>\n<html>")
        f.write(str(h))
        f.write("</html>")

def main(name="vis_output"):
    game = Game()
    h = html.HTML()
    step_count = 0  # this will eventually include zombie moves
    
    for line in sys.stdin:
        try:
            move = read_move(line)
        except ParseError as e:
            print e
            exit()
        process_move(h, game, move)
        step_count += 1
        if step_count % STEPS_PER_PAGE == 0:
            write_page(h, (step_count - 1) // STEPS_PER_PAGE, name)
    if step_count % STEPS_PER_PAGE > 0:
        write_page(h, step_count // STEPS_PER_PAGE, name)
    
    
if __name__ == '__main__':
    main()