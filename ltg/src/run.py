
import sys

import bot as B

from arena import Arena
from bot_io import QuietInteractiveIo, CompetitionIo

if __name__ == '__main__':
    botname = sys.argv[1]
    player = int(sys.argv[2])
        
    competition_io = CompetitionIo()
    quiet_interactive_io = QuietInteractiveIo()
    
    prop_bot = getattr(B, botname)(bot_io = competition_io)
    opp_bot = B.InteractiveBot(bot_io = quiet_interactive_io)

    if player == 0:
        bot1, bot2 = prop_bot, opp_bot
    else:
        bot2, bot1 = prop_bot, opp_bot

    try:
        arena_competition = Arena(arena_io = quiet_interactive_io, bot1 = bot1, bot2 = bot2)
        arena_competition.fight()
    except EOFError:
        pass
        
