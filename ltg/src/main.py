from time import clock

from game import Game
from bot import *
from strategy import *
from strategy_bot import *

def match(bot1, bot2):
    game = Game(silent=False)
    
    bots = bot1, bot2
    bot1.begin_game(0)
    bot2.begin_game(1)
    
    while not game.is_finished():
        move = bots[game.half_moves%2].make_move()
        bots[1-game.half_moves%2].receive_move(*move)
        game.make_half_move(*move)
             
    print 'game finished after half move', game.half_moves-1
    n1, n2 = [p.num_alive_slots() for p in game.players]
    if n1 > n2:
        print 'player 0 wins'
    elif n2 > n1:
        print 'player 1 wins'
    else:
        print 'tie'


if __name__ == '__main__':
    start = clock()
    match(InteractiveBot(), IdleBot())
    strategy_bot_test = StrategyBot()
    strategy_bot_test.add_strategy(
            SequenceStrategy(
                             GenerateValueStrategy(slot = 0, target = 15),
                             GenerateValueStrategy(slot = 1, target = 3),
                             GenerateValueStrategy(slot = 3, target = 15),
                             AppNTo0Strategy(slot = 2)))
    match(IdleBot(), strategy_bot_test)
    print 'it took', clock()-start
