from rules import card_by_name, SLOTS
from game import Game


__all__ = [
    'Bot',
    'IdleBot',
    'InteractiveBot',
]

class Bot(object):
    def begin_game(self, game, your_number):
        assert your_number in range(2)
        self.number = your_number
        self.game = game
        
    def end_game(self):
        pass
        
    def receive_move(self, dir, slot, card):
        pass
        #raise NotImplementedError()
    
    def make_move(self):
        'return tuple (dir, slot, card_name)'
        raise NotImplementedError()
    
class IdleBot(Bot):
    def make_move(self):
        return (1, 0, 'I')
    def receive_move(self, *move):
        pass

class InteractiveBot(GameTrackingBot):
    def begin_game(self, game, your_number):
        super(InteractiveBot, self).begin_game(game, your_number)
        print 'You are player 0'
        
    def receive_move(self, *move):
        print "opponent's move was", move
        super(InteractiveBot, self).receive_move(*move)  
       
    def read_slot(self): 
        print 'slot no?'
        while True:
            slot = raw_input()
            try:
                slot = int(slot)
            except ValueError as e:
                print e
                continue
            if slot not in range(SLOTS):
                print 'between 0 and', SLOTS-1
                continue
            return slot
        
    def read_card(self):
        print 'card name?'
        while True:
            card = raw_input()
            if card in card_by_name:
                return card
            print 'available card names are', card_by_name.keys()
            
    def choose_move(self):
        print self.game
        print 'your (player{0}) move'.format(self.number)
        print '(1) apply card to slot, or (2) apply slot to card?'
        while True:
            direction = raw_input()
            if direction == '1':
                direction = 1
                card = self.read_card()
                slot = self.read_slot()
                break
            if direction == '2':
                direction = 2
                slot = self.read_slot()
                card = self.read_card()
                break
            print 'enter 1 or 2'
            
        return (direction, slot, card)