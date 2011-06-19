#from timeit import timeit
#from rules import cards
#from terms import term_to_sequence, eval_sequence
#from pprint import pprint
#
#term = (((cards.S, cards.K), (cards.K, cards.I)), cards.I)
#seq = term_to_sequence(term)
#pprint(seq) 
#res = eval_sequence(seq, debug = True)
#pprint(res)

#from terms import parse_lambda, binarize_term, term_to_sequence
#
#l = r'(\x.(attack x))'
#t = parse_lambda(l)
#print t
#t = binarize_term(t)
#print t
#s = term_to_sequence(t)
#print s

import play
import replay_to_html
import shlex
import webbrowser

play.main(*shlex.split('--replay tmp.rpl loop_de_loop_bot() IdleBot()'))
replay_to_html.main('tmp.rpl')
webbrowser.open('tmp.html')
