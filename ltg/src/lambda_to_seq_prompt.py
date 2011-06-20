from traceback import print_exc
import sys

from terms import lambda_to_sequence, sequence_to_str
from abselim import LambdaParserException



if __name__ == '__main__':
    while True:
        print '>>>',
        s = raw_input()
        try:
            seq = lambda_to_sequence(s)
        except LambdaParserException as e:
            print e
            continue
        except Exception as e:
            sys.stdout.flush()
            print_exc()
            sys.stderr.flush()
            continue
        print len(seq),
        seq = sequence_to_str(seq)
        if len(seq) > 70:
            seq = seq[:70]+' ...'
        print seq
        