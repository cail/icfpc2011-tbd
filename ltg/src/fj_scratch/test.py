from rules import cards
from terms import term_to_sequence, eval_sequence, lambda_to_sequence
from pprint import pprint

r'(\icomb. icomb get 0 (icomb get 1 (icomb get 2)))'

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

#print lambda_to_sequence(r'(put I help 4 0 8192)')

# play.main(*shlex.split('--replay tmp.rpl SampleNetworkBot() IdleBot()'))
play.main(*shlex.split('--replay tmp.rpl loop_de_loop_bot() SampleNetworkBot()'))
replay_to_html.main('tmp.rpl')
webbrowser.open('tmp.html')
