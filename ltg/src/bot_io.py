
from rules import card_by_name, SLOTS, LEFT_APP, RIGHT_APP

class BotIo(object):
    def dump_game(self, bot):
        raise NotImplementedError()

    def notify_begin_game(self, bot):
        raise NotImplementedError()

    def notify_opp_move(self, bot, opp_move):
        raise NotImplementedError()

    def read_move(self):
        raise NotImplementedError()


class ThunkIo(BotIo):
    def dump_game(self, bot):
        pass

    def notify_begin_game(self, bot):
        pass

    def notify_opp_move(self, bot, opp_move):
        pass


class DefaultInteractiveIo(BotIo):
    def dump_game(self, bot):
        print bot.game

    def notify_begin_game(self, bot):
        print 'You are player ', bot.number
        
    def notify_opp_move(self, bot, opp_move):
        print 'opponent\'s move was', opp_move

    def read_move(self):
        self.prompt_direction()
        while True:
            direction = self.get_input_line()
            if direction == '1':
                direction = LEFT_APP
                card = self.read_card()
                slot = self.read_slot()
                break
            if direction == '2':
                direction = RIGHT_APP
                slot = self.read_slot()
                card = self.read_card()
                break
            self.warn_direction(direction)
        return (direction, slot, card)

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
            if card in card_by_name:
                return card_by_name[card]
            self.warn_available_cards(card)
            
    def get_input_line(self):
        return raw_input()

    def warn_value_error(self, e):
        print e

    def warn_direction(self, direction):
        print 'enter 1 or 2 (got: ' + direction + ')'

    def warn_slot_range(self, slot):
        print 'between ' + str(0) + ' and ' + str(SLOTS - 1) + ' (got: ' + str(slot) + ')'

    def warn_available_cards(self, card):
        print 'available card names are' + str(card_by_name.keys()) + ' (got: ' + card + ')'

    def prompt_direction(self):
        print '(1) apply card to slot, or (2) apply slot to card?'

    def prompt_slot_no(self):
        print 'slot no?'

    def prompt_card_name(self):
        print 'card name?'


class InvalidMoveInputException(Exception):
    pass


class QuietInteractiveIo(DefaultInteractiveIo):
    def dump_game(self, bot):
        pass

    def notify_begin_game(self, bot):
        pass
        
    def notify_opp_move(self, bot, opp_move):
        pass

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



