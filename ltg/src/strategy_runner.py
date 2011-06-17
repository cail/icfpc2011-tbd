from time import clock

from bot import IdleBot
from strategy import *
from strategy_bot import StrategyBot
from main import match


if __name__ == '__main__':
    start = clock()
    sb = StrategyBot()
    sb.add_strategy(GenerateValueStrategy(10))
    match(sb, IdleBot())
    print 'it took', clock()-start