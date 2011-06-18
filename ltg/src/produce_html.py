from game import Game
from bot import IdleBot, RandomBot, InteractiveBot

if __name__ == '__main__':
    html = open('nice.html', 'w')
    
    game = Game()
    
    bots = [RandomBot(game), IdleBot(game)]

    while not game.is_finished():
        print>>html, '<h5>half turn {0}</h5>'.format(game.half_moves)
        if game.has_zombie_phase():
            game.zombie_phase()
        move = bots[game.half_moves%2].choose_move()
        print>>html, 'Player made move {0} {1} {2}'.format(*move)
        game.make_half_move(*move)


    html.close()
    print 'game ended at half turn', game.half_moves