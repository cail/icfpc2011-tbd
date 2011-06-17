
from time import clock

from arena import Arena
from bot import IdleBot, InteractiveBot
from strategy_bot import StrategyBot
from bot_io import ThunkIo, DefaultInteractiveIo, QuietInteractiveIo, CompositeIo
from strategy import GenerateValueStrategy, AppNTo0Strategy, SequenceStrategy


if __name__ == '__main__':
    start = clock()

    with open('../../replays/test.rpl', 'w') as rpl_fd:
        thunk_io = ThunkIo()
        game_io = CompositeIo(DefaultInteractiveIo(), ThunkIo())
        #game_io = QuietInteractiveIo()
    
        # Interactive against idle
        arena1 = Arena(arena_io = game_io, bot1 = InteractiveBot(bot_io = game_io), bot2 = IdleBot(bot_io = thunk_io))
        #arena1.fight()
    
        # Non-interactive faux strat against idle
        strategy_bot_test = StrategyBot(bot_io = game_io)
        strategy_bot_test.add_strategy(
                SequenceStrategy(
                                 GenerateValueStrategy(slot = 0, target = 15),
                                 GenerateValueStrategy(slot = 1, target = 3),
                                 GenerateValueStrategy(slot = 3, target = 15),
                                 AppNTo0Strategy(slot = 2, n_slot = 4)))
        arena2 = Arena(arena_io = game_io, bot1 = IdleBot(bot_io = thunk_io), bot2 = strategy_bot_test)
        arena2.fight()

    game_io.notify_total_time(clock() - start)

