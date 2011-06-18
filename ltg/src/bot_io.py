
from rules import card_by_name, SLOTS, LEFT_APP, RIGHT_APP


__all__ = [
          'BotIo',
          'ThunkIo',
          'QuietInteractiveIo',
          'DefaultInteractiveIo',
          'WriteReplayIo',
          'ReadReplayIo',
          'InvalidMoveInputException',
          ]


class BotIo(object):
    def notify_winner(self, player_no):
        raise NotImplementedError()

    def notify_tie(self):
        raise NotImplementedError()

    def notify_total_moves(self, moves):
        raise NotImplementedError()

    def notify_total_time(self, time):
        raise NotImplementedError()

    def dump_game(self, bot):
        raise NotImplementedError()

    def notify_begin_game(self, bot):
        raise NotImplementedError()

    def notify_prop_move(self, bot, prop_move):
        raise NotImplementedError()

    def notify_opp_move(self, bot, opp_move):
        raise NotImplementedError()

    def read_move(self):
        raise NotImplementedError()


class ThunkIo(BotIo):
    def notify_winner(self, player_no):
        pass

    def notify_tie(self):
        pass

    def notify_total_moves(self, moves):
        pass

    def notify_total_time(self, time):
        pass

    def dump_game(self, bot):
        pass

    def notify_begin_game(self, bot):
        pass

    def notify_prop_move(self, bot, prop_move):
        pass

    def notify_opp_move(self, bot, opp_move):
        pass


class InvalidMoveInputException(Exception):
    pass


class QuietInteractiveIo(ThunkIo):
    def read_move(self):
        self.prompt_direction()
        while True:
            direction = self.get_input_line()
            if direction == '1':
                direction = LEFT_APP
                slot, card = self.read_card_and_slot()
                break
            if direction == '2':
                direction = RIGHT_APP
                slot, card = self.read_slot_and_card()
                break
            self.warn_direction(direction)
        return (direction, slot, card)

    def read_card_and_slot(self):
        card = self.read_card()
        slot = self.read_slot()
        return (slot, card)

    def read_slot_and_card(self):
        slot = self.read_slot()
        card = self.read_card()
        return (slot, card)

    def read_slot(self): 
        self.prompt_slot_no()
        while True:
            slot = self.get_input_line()
            try:
                slot = int(slot)
            except ValueError as e:
                self.warn_value_error(e)
                continue
            if slot not in range(SLOTS):
                self.warn_slot_range(slot)
                continue
            return slot
        
    def read_card(self):
        self.prompt_card_name()
        while True:
            card = self.get_input_line()
            if card == '0':
                card = 'zero'
            if card in card_by_name:
                return card_by_name[card]
            self.warn_available_cards(card)
            
    def get_input_line(self):
        return raw_input()

    def warn_value_error(self, e):
        raise InvalidMoveInputException('ValueError', e)

    def warn_direction(self, direction):
        raise InvalidMoveInputException('direction', direction)

    def warn_slot_range(self, slot):
        raise InvalidMoveInputException('slot', slot)

    def warn_available_cards(self, card):
        raise InvalidMoveInputException('card', card)

    def prompt_direction(self):
        pass

    def prompt_slot_no(self):
        pass

    def prompt_card_name(self):
        pass


class DefaultInteractiveIo(QuietInteractiveIo):
    def notify_winner(self, player_no):
        print 'player ' + str(player_no) + ' wins'

    def notify_tie(self):
        print 'tie'

    def notify_total_moves(self, moves):
        print 'game finished after half move ' + str(moves)

    def notify_total_time(self, time):
        print 'it took ' + str(time)

    def dump_game(self, bot):
        print bot.game

    def notify_begin_game(self, bot):
        print 'You are player ', bot.number
        
    def notify_prop_move(self, bot, prop_move):
        print 'proponent\'s move was ' + str(prop_move)

    def notify_opp_move(self, bot, opp_move):
        print 'opponent\'s move was ' + str(opp_move)

    def warn_value_error(self, e):
        print e

    def warn_direction(self, direction):
        print 'enter 1 or 2 (got: ' + direction + ')'

    def warn_slot_range(self, slot):
        print 'between ' + str(0) + ' and ' + str(SLOTS - 1) + ' (got: ' + str(slot) + ')'

    def warn_available_cards(self, card):
        print 'available card names are ' + str(card_by_name.keys()) + ' (got: ' + card + ')'

    def prompt_direction(self):
        print '(1) apply card to slot, or (2) apply slot to card?'

    def prompt_slot_no(self):
        print 'slot no?'

    def prompt_card_name(self):
        print 'card name?'


class WriteReplayIo(ThunkIo):
    def __init__(self, fd):
        self.fd = fd

    def notify_prop_move(self, bot, prop_move):
        self.write_replay_move(bot, prop_move)

    def notify_opp_move(self, bot, opp_move):
        self.write_replay_move(bot, opp_move)

    def write_replay_move(self, bot, move):
        direction, slot, card = move
        if card == 0:
            card_name = 'zero'
        else:
            card_name = str(card)
        self.fd.write(dict(l = '1', r = '2')[direction] + ' ' + str(slot) + ' ' + card_name + "\n")


class ReadReplayIo(QuietInteractiveIo):
    def __init__(self, fd):
        self.fd = fd
        self.tokens = []

    def read_card_and_slot(self):
        return self.read_slot_and_card()

    def get_input_line(self):
        if len(self.tokens) == 0:
            self.tokens = self.fd.readline()[:-1].split(' ')
            self.tokens.reverse()
        return self.tokens.pop()


class CompositeIo(BotIo):
    def __init__(self, *args):
        self.io_impls = args

    def notify_winner(self, player_no):
        map(lambda x: x.notify_winner(player_no), self.io_impls)

    def notify_tie(self):
        map(lambda x: x.notify_tie(), self.io_impls)

    def notify_total_moves(self, moves):
        map(lambda x: x.notify_total_moves(moves), self.io_impls)

    def notify_total_time(self, time):
        map(lambda x: x.notify_total_time(time), self.io_impls)

    def dump_game(self, bot):
        map(lambda x: x.dump_game(bot), self.io_impls)

    def notify_begin_game(self, bot):
        map(lambda x: x.notify_begin_game(bot), self.io_impls)

    def notify_prop_move(self, bot, prop_move):
        map(lambda x: x.notify_prop_move(bot, prop_move), self.io_impls)

    def notify_opp_move(self, bot, opp_move):
        map(lambda x: x.notify_opp_move(bot, opp_move), self.io_impls)

    def read_move(self):
        for io_impl in self.io_impls:
            move = io_impl.read_move()
            if move != None:
                return move
        return None

