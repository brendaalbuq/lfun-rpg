import ply.lex as lex
from error_utils import format_source_error

reserved = {
    'let': 'LET',
    'fun': 'FUN',
    'Int': 'INTTYPE',
    'Bool': 'BOOLTYPE',
    'String': 'STRINGTYPE',
    'List': 'LISTTYPE',
    'true': 'TRUE',
    'false': 'FALSE',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'when': 'WHEN',
    'is': 'IS',
    'end': 'END',
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
}

tokens = [
    'ID', 'NUMBER', 'STRING',
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE',
    'ASSIGN', 'COLON', 'SEMI', 'LPAREN', 'RPAREN', 'ARROW',
    'LBRACKET', 'RBRACKET', 'COMMA', 'UNDERSCORE'
] + list(reserved.values())

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_ASSIGN = r'='
t_COLON = r':'
t_SEMI = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_ARROW = r'->'
t_COMMA = r','
t_UNDERSCORE = r'_'

t_ignore = ' \t\r'

states = (('COMMENT', 'exclusive'),)

def t_comment_single(t):
    r'--.*'
    pass

def t_comment_multi_start(t):
    r'\{-'
    t.lexer.begin('COMMENT')

def t_COMMENT_end(t):
    r'-\}'
    t.lexer.begin('INITIAL')

def t_COMMENT_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_COMMENT_any(t):
    r'.'
    pass

t_COMMENT_ignore = ''

def t_STRING(t):
    r'"([^\\\n]|(\\.))*?"'
    t.value = bytes(t.value[1:-1], 'utf-8').decode('unicode_escape')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    message = f"Símbolo léxico inválido '{t.value[0]}'"
    raise SyntaxError(format_source_error("Erro léxico", message, t.lexer.lexdata, t.lexpos))

def t_COMMENT_error(t):
    t.lexer.skip(1)

def build_lexer(**kwargs):
    return lex.lex(**kwargs)
