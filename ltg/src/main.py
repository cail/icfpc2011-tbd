
from time import clock

from arena import Arena
from bot import IdleBot, RandomBot, InteractiveBot
from bot_io import ThunkIo, DefaultInteractiveIo, QuietInteractiveIo, WriteReplayIo, ReadReplayIo, CompetitionIo, CompositeIo
from rules import cards
from strategy import GenerateValueStrategy, GetIStrategy, AppNTo0Strategy, SequenceStrategy, IdleStrategy, AppFIJNStrategy, DumbSlotKiller
from strategy_bot import StrategyBot


if __name__ == '__main__':
    start = clock()

    thunk_io = ThunkIo()
    game_io = DefaultInteractiveIo()
    competition_io = CompetitionIo()
    quiet_interactive_io = QuietInteractiveIo()
    
    # Competition mode
    arena_competition = Arena(arena_io = game_io,
                   bot1 = InteractiveBot(bot_io = quiet_interactive_io),
                   bot2 = RandomBot(bot_io = competition_io))
    #arena_competition.fight()

    with open('../../replays/test.rpl', 'r') as rpl_fd:
        # Replay playback
        arena_replay = Arena(arena_io = game_io,
                       bot1 = InteractiveBot(bot_io = CompositeIo(ReadReplayIo(fd = rpl_fd), game_io)),
                       bot2 = InteractiveBot(bot_io = CompositeIo(ReadReplayIo(fd = rpl_fd), thunk_io)))
        #arena_replay.fight()

    with open('../../replays/test.rpl', 'w') as rpl_fd:
        # Interactive against idle
        arena_interactive = Arena(arena_io = game_io,
                       bot1 = InteractiveBot(bot_io = game_io),
                       bot2 = IdleBot(bot_io = thunk_io))
        #arena_interactive.fight()
    
        # Two randoms duking it out
        arena_random = Arena(arena_io = game_io,
                       bot1 = RandomBot(bot_io = CompositeIo(game_io, WriteReplayIo(fd = rpl_fd))),
                       bot2 = RandomBot(bot_io = thunk_io))
        #arena_random.fight()
    
        # Non-interactive faux strat against idle with replay
        strategy_bot_test = StrategyBot(bot_io = CompositeIo(game_io, WriteReplayIo(fd = rpl_fd)))
        strategy_bot_test.add_strategy(
                SequenceStrategy(
                                 #GenerateValueStrategy(slot = 0, target = 15),
                                 #GenerateValueStrategy(slot = 1, target = 3),
                                 #GenerateValueStrategy(slot = 3, target = 15),
                                 #AppNTo0Strategy(slot = 2, n_slot = 4),
                                 #GetIStrategy(slot = 100, i_slot = 1),
                                 #AppFIJNStrategy(slot = 2, f_card = cards.help, i_num = 3, j_num = 3, n_num = 8192),
                                 #AppFIJNStrategy(slot = 2, f_card = cards.attack, i_num = 3, j_num = 3, n_num = 1024),
                                 DumbSlotKiller(battery_slot = 3, target_slot = 252),
                                 #IdleStrategy(),
                                ))
        arena_strategy = Arena(arena_io = game_io,
                       bot1 = IdleBot(bot_io = thunk_io),
                       bot2 = strategy_bot_test)
        arena_strategy.fight()

    game_io.notify_total_time(clock() - start)

