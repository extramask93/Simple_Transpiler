from enum import Enum
import re

class DefNode:
    def __init__(self, name, arg_names, body):
        self.name = name
        self.arg_names = arg_names
        self.body = body
    def __repr__(self):
        return "DefNode: <name : %s> <arg_names: %s> <body: %s>"%(self.name, self.arg_names, self.body)
class IntegerNode:
    def __init__(self,value):
        self.value = value
    def __repr__(self):
        return "IntegerNode: %s"%self.value
class CallNode:
    def __init__(self,fname,arg_expr):
        self.fname = fname
        self.agr_expr = arg_expr
    def __repr__(self):
        return "CallNode: %s, args = %s"%(self.fname,self.agr_expr)
class VarRefNode:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return "VarRefNode: %s"%self.value
class Tk(Enum):
    define = 0
    end = 1
    identifier = 2
    integer = 3
    oparen = 4
    cparen = 5
    comma =6
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __str__(self):
        return "<Token : type = %s, value = \"%s\">"%(self.type,self.value)
    def __repr__(self):
        return "<Token : type = %s, value = \"%s\">" % (self.type, self.value)

class Tokenizer:
    TOKEN_TYPES = [
        [Tk.define,r"\bdef\b"],
        [Tk.end,r"\bend\b"],
        [Tk.identifier,r"\b[a-zA-Z]+\b"],
        [Tk.integer,r"\b[0-9]+\b"],
        [Tk.oparen,r"\("],
        [Tk.cparen,r"\)"],
        [Tk.comma, r"\,"]
    ]
    def __init__(self, source):
        self.source = source
    def tokenize_one_token(self):
        for type in Tk:
            rn = r"\A" + r"(%s)" % Tokenizer.TOKEN_TYPES[type.value][1]
            res = re.search(rn, self.source)
            if res is not None:
                value = res.group(1)
                self.source = self.source[len(value):]
                return Token(type, value)
        print("%s" % (self.source))
    def tokenize(self):
        tokens = []
        while(len(self.source)):
            tokens.append(self.tokenize_one_token())
            self.source = self.source.strip()
        return tokens
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
    def parse(self):
        return self.parse_def()
    def parse_def(self):
        self.consume(Tk.define)
        name = self.consume(Tk.identifier).value
        arg_names = self.parse_arg_names()
        body = self.parse_expr()
        self.consume(Tk.end)
        return DefNode(name, arg_names, body)
    def parse_arg_names(self):
        arg_names = []
        self.consume(Tk.oparen)
        if(self.peek(Tk.identifier)):
            arg_names.append(self.consume(Tk.identifier).value)
            while(self.peek(Tk.comma)):
                self.consume(Tk.comma)
                arg_names.append(self.consume(Tk.identifier).value)
        self.consume(Tk.cparen)
        return arg_names
    def peek(self, type, nr = 0):
        return self.tokens[nr].type == type
    def parse_expr(self):
        if(self.peek(Tk.integer)):
            return self.parse_integer()
        elif(self.peek(Tk.identifier) and self.peek(Tk.oparen,1)):
            return self.parse_call()
        else:
            return self.parse_var_ref()
    def parse_var_ref(self):
        return VarRefNode(self.consume(Tk.identifier).value)
    def parse_call(self):
        name = self.consume(Tk.identifier).value
        arg_exprs = self.parse_arg_expr()
        return CallNode(name,arg_exprs)
    def parse_arg_expr(self):
        arg_expr = []
        self.consume(Tk.oparen)
        if(not self.peek(Tk.cparen)):
            arg_expr.append(self.parse_expr())
            while(self.peek(Tk.comma)):
                self.consume(Tk.comma)
                arg_expr.append(self.parse_expr())
        self.consume(Tk.cparen)
        return arg_expr
    def parse_integer(self):
        return IntegerNode(int(self.consume(Tk.integer).value))
    def consume(self, expected_type):
        token = self.tokens.pop(0)
        if token.type is expected_type:
            return token
        else:
            raise Exception("Expected %s but got %s"%(expected_type,token))
class Generator:
    def __init__(self):
        pass
    def generate(self, node):
        if(isinstance(node,DefNode)):
            return "function %s(%s) { return %s};" % (node.name, ','.join(node.arg_names), self.generate(node.body))
        elif(isinstance(node, CallNode)):
            return "%s(%s)" % (node.fname, ','.join(list(map(self.generate,node.agr_expr))))
        elif(isinstance(node,VarRefNode)):
            return node.value
        elif(isinstance(node, IntegerNode)):
            return str(node.value)
        else:
            raise Exception("Unexpected node type %s"%node)
if __name__ == "__main__":
    source = open("test.src",'r')
    text = source.read()
    ##########################
    tokens = Tokenizer(text).tokenize()
    tree = Parser(tokens).parse()
    code = Generator().generate(tree)
    print(code)