
import re
import sys

from game import *

class LambdaParserException(Exception):
    pass

def is_whitespace(char):
    return re.match(r'\s', char)

def is_special(char):
    return re.match(r'[\(\)\\\.]', char)

def tokenize(string):
    tokens = []
    curtoken = ''
    for char in string:
        if is_whitespace(char):
            if curtoken != '':
                tokens.append(curtoken)
                curtoken = ''
        elif is_special(char):
            if curtoken != '':
                tokens.append(curtoken)
                curtoken = ''
            tokens.append(char)
        else:
            curtoken = curtoken + char
    if curtoken != '':
        tokens.append(curtoken)
    return tokens

def m(tokens):
    toklen = len(tokens)
    if toklen == 0:
        return ('', [])
    elif toklen == 1:
        return (tokens[0], [])
    else:
        return (tokens[0], tokens[1:])

def join_expr(left, right):
    if left == None:
        return right
    else:
        return Expr(left, right)

def parse(string):
    return parse_expr(None, tokenize(string))

def parse_expr(expr, tokens):
    s = m(tokens)
    if s[0] == ')' or len(s[1]) == 0:
        if expr == None:
            raise LambdaParserException('null expression')
        return (expr, s[1])
    elif s[0] == '(':
        interm = parse_expr(None, s[1])
        return parse_expr(join_expr(expr, interm[0]), interm[1])
    elif expr == None and s[0] == '\\':
        return parse_lambda(s[1])
    elif not is_special(s[0]):
        return parse_expr(join_expr(expr, Atom(s[0])), s[1])
    else:
        raise LambdaParserException('unrecognized symbol')

def parse_lambda(tokens):
    s = m(tokens)
    if is_special(s[0]):
        raise LambdaParserException('bad lambda')
    return parse_lambda2(Atom(s[0]), s[1])

def parse_lambda2(variable, tokens):
    s = m(tokens)
    if s[0] != '.':
        interm = parse_lambda(tokens)
    else:
        interm = parse_expr(None, s[1])
    return (Lambda(variable, interm[0]), interm[1])

class Atom:
    def __init__(self, symbol):
        self.symbol = symbol
    def dump(self):
        return self.symbol
    def transform(self):
        return self
    def free(self, atom):
        return self.symbol == atom.symbol
    def equals(self, atom):
        return self.free(atom)

class Expr:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def dump(self):
        return '(' + self.left.dump() + ' ' + self.right.dump() + ')'
    def transform(self):
        return Expr(self.left.transform(), self.right.transform())
    def free(self, atom):
        return self.left.free(atom) or self.right.free(atom)
    def equals(self, atom):
        return False

class Lambda:
    def __init__(self, variable, expr):
        self.variable = variable
        self.expr = expr
    def dump(self):
        return '(\\' + self.variable.dump() + '. ' + self.expr.dump() + ')'
    def transform(self):
        xexpr = self.expr.transform()
        if not xexpr.free(self.variable):
            return Expr(Atom('K'), xexpr)
        elif xexpr.equals(self.variable):
            return Atom('I')
        elif ((not xexpr.left.free(self.variable)) and
              xexpr.right.equals(self.variable)):
            return xexpr.left
        else:
            return Expr(Expr(Atom('S'), Lambda(self.variable, xexpr.left).transform()),
                        Lambda(self.variable, xexpr.right).transform())
    def free(self, atom):
        return (not self.variable.equals(atom)) and self.expr.free(atom)
    def equals(self, atom):
        return False

if __name__ == '__main__':
    while True:
        sys.stdout.write('>>> ');
        try:
            print parse('(' + sys.stdin.readline() + ')')[0].transform().dump()
        except LambdaParserException as e:
            print '\nError: ' + e.args[0]

