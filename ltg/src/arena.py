
from game import Game


__all__ = [
          'Arena',
          ]

class Arena(object):
    def __init__(self, arena_io, bot1, bot2):
        self.io = arena_io
        self.game = Game(silent = False)
        self.bots = bot1, bot2

    def fight(self):
        self.prep_up()
        self.duke_it_out()
        self.report_outcome()

    def prep_up(self):
        for (bot_num, bot) in zip(range(2), self.bots):
            bot.begin_game(self.game, bot_num)

    def duke_it_out(self):
        while not self.game.is_finished():
            move = self.bots[self.game.half_moves % 2].make_move()
            self.bots[1 - (self.game.half_moves % 2)].receive_move(*move)
            self.game.make_half_move(*move)

    def report_outcome(self):
        self.io.notify_total_moves(self.game.half_moves - 1)
        n1, n2 = [p.num_alive_slots() for p in self.game.players]
        if n1 > n2:
            self.io.notify_winner(0)
        elif n2 > n1:
            self.io.notify_winner(1)
        else:
            self.io.notify_tie()

