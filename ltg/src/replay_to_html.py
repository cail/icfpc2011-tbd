import sys
import os

from game import Game
from simple_bot import PlaybackBot
from rules import SLOTS, INITIAL_VITALITY, cards, LEFT_APP

HEAD = 200 # how many head and tail moves we show
TAIL = 20

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: replay_to_log hz.rpl'
        exit(1)
        
    replay_name = sys.argv[1]     
    with open(replay_name) as fin:
        replay = list(fin)
        
    html_name = os.path.splitext(replay_name)[0]+'.html'
    html = open(html_name, 'w')
    
    
    #log = sys.stdout
    print>>html, '<html><body><div style="background-color:#FFFFFF">'
    print>>html, 'Lambda: The Gathering log emulator'
    
    game = Game()
    
    bots = [PlaybackBot(replay[::2], game), PlaybackBot(replay[1::2], game)]

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
                    color = '#B0FFB0'
                    if vit == 0:
                        color = '#FFB0B0'
                    if vit == -1:
                        color = '#00A060'
                    if (vit, value) != (INITIAL_VITALITY, cards.I):
                        print>>html, '<tr style="background-color:{3}"><td>{0}</td><td>{1}</td><td>{2}</td>'.format(i, vit, value, color)
                print>>html, '</table>'
                print>>html, '</td>'
            print>>html, '</tr></table>'
        
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
            print>>html, '</div>'
        game.make_half_move(*move)

    print>>html, '<h1>{0}:{1}</h1>'.format(game.players[0].num_alive_slots(), game.players[1].num_alive_slots())
    print>>html, '</div></body></html>'
    html.close()
    