import sys
import argparse

import rules
from rules import LEFT_APP, RIGHT_APP, card_by_name
from game import Game
from simple_bot import IdleBot, RandomBot, InteractiveBot
from idiot_bot import test_idiot_bot
from sequence_bot import test_seq_bot
from slot_killer import slot_killer_bot
from combo_bot import test_combo_bot


def send_move(direction, slot, card):
    if direction == LEFT_APP:
        print 1
        print card
        print slot
    else:
        print 2
        print slot
        print card
    sys.stdout.flush()
    
    
def receive_move():
    direction = int(raw_input())
    if direction == 1:
        direction = LEFT_APP
        card = raw_input()
        slot = int(raw_input())
    elif direction == 2:
        direction = RIGHT_APP
        slot = int(raw_input())
        card = raw_input()
    else:
        assert False
    card = card_by_name[card]
    return direction, slot, card    
    
def main(*argv):
    if not argv: 
        argv = None
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--replay', type=argparse.FileType('w'),
                        default=None)
    parser.add_argument('--maxturns', type=int, default=rules.MAX_TURNS)
    parser.add_argument('bot1')
    parser.add_argument('bot2')
    parser.add_argument('number', nargs='?', type=int, default=None, 
                        help='if number is provided, script interacts '
                        'in official way, and another bot is ignored')
    
    args = parser.parse_args(argv)
    replay = args.replay
    bot_number = args.number
    
    game = Game()
    
    bots = [eval(args.bot1), eval(args.bot2)]
    if bot_number in (0, None):
        bots[0].set_game(game)
    if bot_number in (1, None):
        bots[1].set_game(game)

    while not game.is_finished():
        #if game.half_moves % 10 == 0:
        #    print>>sys.stderr, 'half turn', game.half_moves
        if game.half_moves >= args.maxturns*2:
            break
        if game.has_zombie_phase():
            game.zombie_phase()
        bot = bots[game.half_moves%2]
        
        if bot_number == 1-game.half_moves%2:
            move = receive_move()
        else:
            move = bot.choose_move()
        if bot_number == game.half_moves%2:
            send_move(*move)
        game.make_half_move(*move)
        if replay is not None:
            if move[0] == 'l':
                d = 1
            else:
                d = 2
            print>>replay, d, move[1], move[2]
            replay.flush()
        
    if replay is not None:
        replay.close()
    print>>sys.stderr, 'game ended at half turn', game.half_moves    
    
if __name__ == '__main__':
    main()
