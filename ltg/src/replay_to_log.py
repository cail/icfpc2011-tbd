import sys
import os

from game import Game
from simple_bot import PlaybackBot
from rules import SLOTS, INITIAL_VITALITY, cards, LEFT_APP

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: replay_to_log hz.rpl'
        exit(1)
        
    replay_name = sys.argv[1]     
    with open(replay_name) as fin:
        replay = list(fin)
        
    log_name = os.path.splitext(replay_name)[0]+'.log'
    log = open(log_name, 'w')
    
    
    #log = sys.stdout
    
    print>>log, 'Lambda: The Gathering log emulator'
    
    game = Game(output_level=1)
    original_stdout = sys.stdout
    sys.stdout = log # because game outputs to stdout
    # it's dirty, but i don't care
    
    bots = [PlaybackBot(replay[::2], game), PlaybackBot(replay[1::2], game)]

    skip_begin = -1
    skip_end = -1
    if len(replay) > 210:
        skip_begin = 100
        skip_end = len(replay)-100

    while not game.is_finished():
        if game.half_moves == len(replay):
            print>>log, 'replay prematurely ended'
            break
        player = game.half_moves%2
        if player == 0:
            print>>log, '###### turn {0}'.format(game.half_moves//2+1)
        print>>log, "*** player {0}'s turn, with slots:".format(player)
        prop = game.proponent
        for i in range(SLOTS):
            vit, value = prop.vitalities[i], prop.values[i]
            if (vit, value) != (INITIAL_VITALITY, cards.I):
                print>>log, '{0}={{{1},{2}}}'.format(i, vit, value)
        print>>log, '(slots {10000,I} are omitted)'
        
        if game.has_zombie_phase():
            game.zombie_phase()
        move = bots[game.half_moves%2].choose_move()
        
        print>>log, '(1) apply card to slot, or (2) apply slot to card?'
        if move[0] == LEFT_APP:
            print>>log, 'card name?'
            print>>log, 'slot no?'
            print>>log, 'player {0} applied card {2} to slot {1}'.\
                format(player, move[1], move[2])
        else:
            print>>log, 'slot no?'
            print>>log, 'card name?'
            print>>log, 'player {0} applied slot {1} to card {2}'.\
                format(player, move[1], move[2])
        game.make_half_move(*move)


    log.close()
    sys.stdout = original_stdout