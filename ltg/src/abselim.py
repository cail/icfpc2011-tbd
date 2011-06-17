
import re

class LambdaParserException(Exception):
    pass

def m(string):
    strlen = len(string)
    if strlen == 0:
        return ('', '')
    elif strlen == 1:
        return (string, '')
    else:
        return (string[0], string[1:])

def elim_ws(string):
    s = m(string)
    if re.match(r'\s', s[0]) != None:
        return elim_ws(s[1])
    else:
        return string

def join_expr(left, right):
    if left == None:
        return right
    else:
        return Expr(left, right)

def parse(string):
    return parse_expr(None, string)

def parse_expr(expr, string):
    s = m(elim_ws(string))
    if s[0] == ')' or s[1] == '':
        if expr == None:
            raise LambdaParserException('null expression')
        return (expr, s[1])
    elif s[0] == '(':
        interm = parse(s[1])
        return parse_expr(join_expr(expr, interm[0]), interm[1])
    elif expr == None and re.match(r'\\', s[0]):
        return parse_lambda(s[1])
    elif re.match(r'[A-Za-z]', s[0]):
        return parse_expr(join_expr(expr, Atom(s[0])), s[1])
    else:
        raise LambdaParserException('unrecognized symbol')

def parse_lambda(string):
    s = m(elim_ws(string))
    if not re.match(r'[a-z]', s[0]):
        raise LambdaParserException('bad lambda')
    return parse_lambda2(Atom(s[0]), s[1])

def parse_lambda2(variable, string):
    s = m(elim_ws(string))
    if not re.match(r'\.', s[0]):
        raise LambdaParserException('malformed lambda')
    interm = parse(s[1])
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
        return self.left.dump() + '(' + self.right.dump() + ')'
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
    print parse(r'(\x. (\y. y x))')[0].transform().dump()

