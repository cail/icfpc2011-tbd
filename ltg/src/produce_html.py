import sys

from game import Game
from simple_bot import PlaybackBot

if __name__ == '__main__':
    with open('hz.rpl') as fin:
        replay = list(fin)
        
    html = open('nice.html', 'w')
    
    game = Game()
    
    bots = [PlaybackBot(replay[::2], game), PlaybackBot(replay[1::2], game)]

    skip_begin = -1
    skip_end = -1
    if len(replay) > 210:
        skip_begin = 100
        skip_end = len(replay)-100

    while not game.is_finished():
        show = skip_begin <= game.half_moves < skip_end:
        
        if show:        
            print>>html, '<h5>Turn {0}, player{1} move</h5>'.\
                format(game.half_moves//2, game.half_moves%2)
        if game.has_zombie_phase():
            game.zombie_phase()
        move = bots[game.half_moves%2].choose_move()
        if show:
        print>>html, 'Player made move {0} {1} {2}'.format(*move)
        game.make_half_move(*move)


    html.close()
    print 'game ended at half turn', game.half_moves