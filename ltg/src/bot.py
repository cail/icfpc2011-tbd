from game import Game, card_by_name, SLOTS

__all__ = [
    'Bot',
    'GameTrackingBot',
    'IdleBot',
    'InteractiveBot',
]

class Bot(object):
    def begin_game(self, your_number):
        assert your_number in range(2)
        self.number = your_number
        
    def end_game(self):
        pass
        
    def receive_move(self, dir, slot, card):
        pass
        #raise NotImplementedError()
    
    def make_move(self):
        'return tuple (dir, slot, card_name)'
        raise NotImplementedError()
    
    
class GameTrackingBot(Bot):
    def begin_game(self, your_number):
        Bot.begin_game(self, your_number)
        self.game = Game()
        
    def receive_move(self, *move):
        assert self.game.half_moves%2 == 1-self.number
        self.game.make_half_move(*move)
        
    def make_move(self):
        assert self.game.half_moves%2 == self.number
        move = self.choose_move()
        self.game.make_half_move(*move)
        return move
    
    def choose_move(self):
        raise NotImplementedError()
        
        
class IdleBot(Bot):
    def make_move(self):
        return (1, 0, 'I')


class InteractiveBot(GameTrackingBot):
    def begin_game(self, your_number):
        super(InteractiveBot, self).begin_game(your_number)
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