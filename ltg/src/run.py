import sys

import bot as B

def read_move(bot):
    direction = int(raw_input())
    if direction == 1:
        card = raw_input()
        slot = int(raw_input())
    else:
        slot = int(raw_input())
        card = raw_input()
    bot.receive_move(direction, slot, card)

def write_move(bot):
    direction, slot, card = bot.make_move()
    if direction == 1:
        print card
        print slot
    else:
        print slot
        print card
    
if __name__ == '__main__':
    botname = sys.argv[1]
    player = int(sys.argv[2])
        
    bot = B.__dict__[botname]()
    bot.begin_game(player)
    
    if player == 0:
        write_move(bot)
    
    try:
        while True:
            read_move(bot)
            write_move(bot)
    except EOFError:
        pass
        
