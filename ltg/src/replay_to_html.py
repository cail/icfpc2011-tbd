import sys
import os

from game import Game
from simple_bot import PlaybackBot
from rules import SLOTS, INITIAL_VITALITY, cards, LEFT_APP

HEAD = 300 # how many head and tail moves we show
TAIL = 20

def main(replay_name):
    with open(replay_name) as fin:
        replay = list(fin)
        
    html_name = os.path.splitext(replay_name)[0]+'.html'
    html = open(html_name, 'w')
    
    
    #log = sys.stdout
    print>>html, '<html><body><div style="background-color:#FFFFFF">'
    print>>html, 'Lambda: The Gathering log emulator'
    
    game = Game(output_level=2)
    original_stdout = sys.stdout
    sys.stdout = html # because game outputs to stdout
    # it's dirty, but i don't care    
    bots = [PlaybackBot(replay[::2]).set_game(game), PlaybackBot(replay[1::2]).set_game(game)]

    skip_begin = -1
    skip_end = -1
    if len(replay) > 210:
        skip_begin = 100
        skip_end = len(replay)-100

    while not game.is_finished():
        if game.half_moves == len(replay):
            print>>html, '<hr/>replay prematurely ended'
            break
        
        show = game.half_moves < HEAD or game.half_moves >= len(replay)-TAIL
        
        game.output_level = 2 if show else 0
        
        if game.half_moves == HEAD and game.half_moves < len(replay)-TAIL:
            print>>html, '<h1>...</h1>'*3
        
        
        if show:
            player = game.half_moves%2
            if player == 0:
                print>>html, '<h4>###### turn {0}</h4>'.format(game.half_moves//2+1)
            print>>html, '<div style="background-color:{0}">'.format('#FFFFE0' if player else '#E0FFFF') 
            print>>html, "<h5>*** player {0}'s move</h5>".format(player)
            print>>html, '<table border="1"><tr>'
            for p in game.players:
                print>>html, '<td style="vertical-align:top">'
                print>>html, 'Slots: <table>'
                for i in range(SLOTS):
                    vit, value = p.vitalities[i], p.values[i]
                    try:
                        value = str(value)
                    except RuntimeError as e:
                        value = str(e)
                    color = '#B0FFB0'
                    if vit < INITIAL_VITALITY:
                        color = '#E0E090'
                    if vit == 0:
                        color = '#FFB0B0'
                    if vit == -1:
                        color = '#507040'
                    if (vit, value) != (INITIAL_VITALITY, 'I'):
                        print>>html, '<tr style="background-color:{3}"><td>{0}</td><td>{1}</td><td>{2}</td>'.format(i, vit, value, color)
                print>>html, '</table>'
                print>>html, '</td>'
            print>>html, '</tr></table>'

            print>>html, '<pre>'
            
        if game.has_zombie_phase():
            game.zombie_phase()
        move = bots[game.half_moves%2].choose_move()
        
        if show:
            if move[0] == LEFT_APP:
                print>>html, ('player {0} applied card {2} to slot {1}'.
                    format(player, move[1], move[2]))
            else:
                print>>html, ('player {0} applied slot {1} to card {2}'.
                    format(player, move[1], move[2]))

        game.make_half_move(*move)
        if show:
            print>>html, '</pre>'
            print>>html, '</div>'

    print>>html, '<h1>{0}:{1}</h1>'.format(game.players[0].num_alive_slots(), game.players[1].num_alive_slots())
    print>>html, '</div></body></html>'
    html.close()
    sys.stdout = original_stdout    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: replay_to_html hz.rpl'
        exit(1)
    main(sys.argv[1])     
