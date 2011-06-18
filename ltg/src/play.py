import sys

from game import Game
from bot import IdleBot, RandomBot, InteractiveBot

if __name__ == '__main__':
    game = Game(silent=False)
    
    replay = open('replay.txt', 'w')
    
    bots = [RandomBot(game), IdleBot(game)]

    while not game.is_finished():
        print>>sys.stderr, 'half turn', game.half_moves
        if game.has_zombie_phase():
            game.zombie_phase()
        move = bots[game.half_moves%2].choose_move()
        print>>sys.stderr, move[0], move[1], move[2]
        game.make_half_move(*move)
        print>>replay, move[0], move[1], move[2]

    
    print 'game ended at half turn', game.half_moves