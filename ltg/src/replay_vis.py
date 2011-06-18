import html
import string
import sys

import rules
from game import Game
from bot_io import QuietInteractiveIo

TABLE_WIDTH = 16
STEPS_PER_PAGE = 100

def is_init(player, slot):
    return player.vitalities[slot] == rules.INITIAL_VITALITY and \
           player.values[slot] == rules.cards.I

def cell(h, player, slot):
    with h.td as c:
        if is_init(player, slot):
            pass
        else:
            c.text(str(player.vitalities[slot]))
            c.br
            c.text(str(player.values[slot]))
        
def table(h, player):
    with h.table(klass='slots') as t:
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
    doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"\n"http://www.w3.org/TR/html4/strict.dtd">'
    #css = '<style type="text/css">table{font-size: smaller;} .active{background-color:#DDDDDD}</style>\n'
    css = '<style type="text/css">table.slots{border-collapse: collapse; } table.slots td{min-width:30px; height:30px; border: 1px solid black; font-size: 10px;}</style>\n'
    with open(filename, 'w') as f:
        f.write(doctype + "<head>\n" + css + "</head>\n<html>")
        f.write(str(h))
        f.write("</html>")

def main(name="vis_output"):
    game = Game(game_io = QuietInteractiveIo())
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
        h = html.HTML()
    
    
if __name__ == '__main__':
    main()
