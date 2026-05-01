import ply.yacc as yacc
from lexer import tokens
from ast_nodes import *
from error_utils import format_source_error

CURRENT_SOURCE_TEXT = ""


def set_source_text(text):
    global CURRENT_SOURCE_TEXT
    CURRENT_SOURCE_TEXT = text


def mark_node(node, p, token_index):
    node.lineno = p.lineno(token_index)
    node.lexpos = p.lexpos(token_index)
    return node


def mark_from_child(node, child):
    node.lineno = getattr(child, 'lineno', None)
    node.lexpos = getattr(child, 'lexpos', None)
    return node

precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("nonassoc", "LT", "LE", "GT", "GE", "EQ", "NE"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "UMINUS"),
)


def p_program(p):
    "program : statements"
    p[0] = Program(p[1])


def p_statements_many(p):
    "statements : statements statement"
    p[0] = p[1] + [p[2]]


def p_statements_one(p):
    "statements : statement"
    p[0] = [p[1]]


def p_statement_let(p):
    "statement : LET ID COLON type ASSIGN expr SEMI"
    p[0] = mark_node(LetDecl(p[2], p[4], p[6]), p, 1)


def p_statement_funsig(p):
    "statement : FUN ID COLON type ARROW type SEMI"
    p[0] = mark_node(FunSig(p[2], p[4], p[6]), p, 1)


def p_statement_fundef(p):
    "statement : LET ID ID ASSIGN expr SEMI"
    p[0] = mark_node(FunDef(p[2], p[3], p[5]), p, 1)


def p_statement_expr(p):
    "statement : expr SEMI"
    p[0] = mark_from_child(ExprStmt(p[1]), p[1])


def p_type_base(p):
    """type : INTTYPE
    | BOOLTYPE
    | STRINGTYPE"""
    p[0] = p[1]


def p_type_list(p):
    "type : LISTTYPE LBRACKET type RBRACKET"
    p[0] = f"List[{p[3]}]"


def p_expr_int(p):
    "expr : NUMBER"
    p[0] = mark_node(IntLit(p[1]), p, 1)


def p_expr_bool(p):
    """expr : TRUE
    | FALSE"""
    p[0] = mark_node(BoolLit(p[1] == "true"), p, 1)


def p_expr_string(p):
    "expr : STRING"
    p[0] = mark_node(StringLit(p[1]), p, 1)


def p_expr_list(p):
    "expr : LBRACKET list_items_opt RBRACKET"
    p[0] = mark_node(ListLit(p[2]), p, 1)


def p_list_items_opt_values(p):
    "list_items_opt : list_items"
    p[0] = p[1]


def p_list_items_opt_empty(p):
    "list_items_opt : empty"
    p[0] = p[1]


def p_list_items_many(p):
    "list_items : list_items COMMA expr"
    p[0] = p[1] + [p[3]]


def p_list_items_one(p):
    "list_items : expr"
    p[0] = [p[1]]


def p_empty(p):
    "empty :"
    p[0] = []


def p_expr_var(p):
    "expr : ID"
    p[0] = mark_node(Var(p[1]), p, 1)


def p_expr_group(p):
    "expr : LPAREN expr RPAREN"
    p[0] = p[2]


def p_expr_call(p):
    "expr : ID LPAREN expr RPAREN"
    p[0] = mark_node(Call(p[1], p[3]), p, 1)


def p_expr_binop(p):
    """
    expr : expr PLUS expr
    | expr MINUS expr
    | expr TIMES expr
    | expr DIVIDE expr
    | expr MOD expr
    | expr LT expr
    | expr LE expr
    | expr GT expr
    | expr GE expr
    | expr EQ expr
    | expr NE expr
    | expr AND expr
    | expr OR expr
    """
    p[0] = mark_node(BinOp(p[2], p[1], p[3]), p, 2)


def p_expr_unary_minus(p):
    "expr : MINUS expr %prec UMINUS"
    p[0] = mark_node(UnaryOp("-", p[2]), p, 1)


def p_expr_not(p):
    "expr : NOT expr"
    p[0] = mark_node(UnaryOp("not", p[2]), p, 1)


def p_expr_if(p):
    "expr : IF expr THEN expr ELSE expr"
    p[0] = mark_node(IfExpr(p[2], p[4], p[6]), p, 1)


def p_expr_when(p):
    "expr : WHEN LPAREN expr RPAREN IS cases END"
    p[0] = mark_node(WhenExpr(p[3], p[6]), p, 1)


def p_cases_many(p):
    "cases : cases case"
    p[0] = p[1] + [p[2]]


def p_cases_one(p):
    "cases : case"
    p[0] = [p[1]]


def p_case(p):
    "case : patterns ARROW expr SEMI"
    p[0] = mark_from_child(WhenCase(p[1], p[3]), p[3])


def p_patterns_many(p):
    "patterns : patterns COMMA pattern"
    p[0] = p[1] + [p[3]]


def p_patterns_one(p):
    "patterns : pattern"
    p[0] = [p[1]]


def p_pattern_negative_int(p):
    "pattern : MINUS NUMBER"
    p[0] = mark_node(IntLit(-p[2]), p, 1)


def p_pattern(p):
    """pattern : NUMBER
    | TRUE
    | FALSE
    | STRING
    | UNDERSCORE"""
    if p.slice[1].type == "NUMBER":
        p[0] = mark_node(IntLit(p[1]), p, 1)
    elif p.slice[1].type == "TRUE":
        p[0] = mark_node(BoolLit(True), p, 1)
    elif p.slice[1].type == "FALSE":
        p[0] = mark_node(BoolLit(False), p, 1)
    elif p.slice[1].type == "STRING":
        p[0] = mark_node(StringLit(p[1]), p, 1)
    else:
        p[0] = mark_node(Otherwise(), p, 1)


def p_error(p):
    if p:
        message = f"Token inesperado '{p.value}'"
        raise SyntaxError(format_source_error("Erro sintático", message, CURRENT_SOURCE_TEXT, p.lexpos))
    message = "Fim inesperado do ficheiro"
    eof_pos = len(CURRENT_SOURCE_TEXT) if CURRENT_SOURCE_TEXT else 0
    raise SyntaxError(format_source_error("Erro sintático", message, CURRENT_SOURCE_TEXT, eof_pos))


def build_parser(**kwargs):
    return yacc.yacc(**kwargs)
