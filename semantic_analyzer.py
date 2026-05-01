from dataclasses import dataclass
from typing import Dict, Any

from ast_nodes import *


class SemanticError(Exception):
    def __init__(self, message, node=None):
        super().__init__(message)
        self.node = node


@dataclass
class FunctionInfo:
    arg_name: str
    arg_type: str
    ret_type: str
    body: Any


class SemanticAnalyzer:
    """Fase 1: validação semântica e anotação de tipos (sem executar)."""

    def __init__(self):
        self.value_types: Dict[str, str] = {}
        self.fun_sigs: Dict[str, tuple[str, str]] = {}
        self.functions: Dict[str, FunctionInfo] = {}
        self.builtins: Dict[str, tuple[str, str]] = {
            'critico': ('Int', 'Int'),
            'bonus': ('Int', 'Int'),
            'vivo': ('Int', 'Bool'),
            'tamanho': ('List[Any]', 'Int'),
            'vazio': ('List[Any]', 'Bool'),
            'cabeca': ('List[Any]', 'Any'),
            'cauda': ('List[Any]', 'List[Any]'),
        }

    def analyze(self, program: Program):
        for st in program.statements:
            self.check_statement(st)

    def check_statement(self, st):
        if isinstance(st, LetDecl):
            if st.name in self.value_types or st.name in self.functions:
                raise SemanticError(f"Identificador '{st.name}' já foi declarado", st)
            expr_t = self.infer_expr_type(st.expr, {})
            self.require_type(st.type_name, expr_t, f"declaração de {st.name}", st)
            self.value_types[st.name] = st.type_name
            return

        if isinstance(st, FunSig):
            if st.name in self.fun_sigs:
                raise SemanticError(f"Assinatura da função '{st.name}' já existe", st)
            self.fun_sigs[st.name] = (st.arg_type, st.ret_type)
            return

        if isinstance(st, FunDef):
            if st.name not in self.fun_sigs:
                raise SemanticError(f"Função '{st.name}' definida sem assinatura fun", st)
            if st.name in self.functions:
                raise SemanticError(f"Função '{st.name}' já foi definida", st)
            arg_t, ret_t = self.fun_sigs[st.name]
            self.functions[st.name] = FunctionInfo(st.arg_name, arg_t, ret_t, st.expr)
            body_t = self.infer_expr_type(st.expr, {st.arg_name: arg_t})
            self.require_type(ret_t, body_t, f"corpo da função {st.name}", st.expr)
            return

        if isinstance(st, ExprStmt):
            self.infer_expr_type(st.expr, {})
            return

        raise SemanticError(f"Instrução não suportada: {st}", st)

    def infer_expr_type(self, e, local_types):
        if isinstance(e, IntLit): return 'Int'
        if isinstance(e, BoolLit): return 'Bool'
        if isinstance(e, StringLit): return 'String'
        if isinstance(e, ListLit):
            if not e.items:
                return 'List[Unknown]'
            item_t = self.infer_expr_type(e.items[0], local_types)
            for item in e.items[1:]:
                it = self.infer_expr_type(item, local_types)
                self.require_type(item_t, it, 'elemento da lista', item)
            return f'List[{item_t}]'

        if isinstance(e, Var):
            if e.name in local_types: return local_types[e.name]
            if e.name in self.value_types: return self.value_types[e.name]
            raise SemanticError(f"Identificador '{e.name}' não declarado", e)

        if isinstance(e, UnaryOp):
            t = self.infer_expr_type(e.expr, local_types)
            if e.op == '-':
                self.require_type('Int', t, 'operador unário -', e)
                return 'Int'
            if e.op == 'not':
                self.require_type('Bool', t, 'operador not', e)
                return 'Bool'

        if isinstance(e, BinOp):
            lt = self.infer_expr_type(e.left, local_types)
            rt = self.infer_expr_type(e.right, local_types)
            op = e.op
            if op in ['+', '-', '*', '/', '%']:
                if op == '+' and lt == 'String' and rt == 'String':
                    return 'String'
                self.require_type('Int', lt, f'lado esquerdo de {op}', e.left)
                self.require_type('Int', rt, f'lado direito de {op}', e.right)
                return 'Int'
            if op in ['<', '<=', '>', '>=']:
                self.require_type('Int', lt, f'comparação {op}', e.left)
                self.require_type('Int', rt, f'comparação {op}', e.right)
                return 'Bool'
            if op in ['==', '!=']:
                if lt != rt:
                    raise SemanticError(f"Comparação {op} entre tipos incompatíveis: {lt} e {rt}", e)
                return 'Bool'
            if op in ['and', 'or']:
                self.require_type('Bool', lt, f'lado esquerdo de {op}', e.left)
                self.require_type('Bool', rt, f'lado direito de {op}', e.right)
                return 'Bool'

        if isinstance(e, IfExpr):
            ct = self.infer_expr_type(e.cond, local_types)
            self.require_type('Bool', ct, 'condição do if', e.cond)
            tt = self.infer_expr_type(e.then_expr, local_types)
            et = self.infer_expr_type(e.else_expr, local_types)
            if tt != et:
                raise SemanticError(f"Ramos do if com tipos diferentes: {tt} e {et}", e)
            return tt

        if isinstance(e, WhenExpr):
            target_t = self.infer_expr_type(e.target, local_types)
            result_t = None
            for case in e.cases:
                ct = self.infer_expr_type(case.expr, local_types)
                if result_t is None:
                    result_t = ct
                elif ct != result_t:
                    raise SemanticError('Todos os casos do when devem devolver o mesmo tipo', case.expr)
                for pat in case.patterns:
                    if isinstance(pat, Otherwise):
                        continue
                    pt = self.infer_expr_type(pat, local_types)
                    if pt != target_t:
                        raise SemanticError(f"Padrão do when tem tipo {pt}, mas o alvo tem tipo {target_t}", pat)
            if result_t is None:
                raise SemanticError('Expressão when sem casos', e)
            return result_t

        if isinstance(e, Call):
            at = self.infer_expr_type(e.arg, local_types)
            if e.name in self.builtins:
                expected, ret = self.builtins[e.name]
                if expected.startswith('List['):
                    if not self.is_list_type(at):
                        raise SemanticError(f"Argumento de {e.name} deve ser uma lista", e.arg)
                    if e.name == 'cabeca':
                        return self.list_item_type(at)
                    if e.name == 'cauda':
                        return at
                    return ret
                self.require_type(expected, at, f"argumento de {e.name}", e.arg)
                return ret
            if e.name in self.functions:
                f = self.functions[e.name]
                self.require_type(f.arg_type, at, f"argumento de {e.name}", e.arg)
                return f.ret_type
            if e.name in self.fun_sigs:
                arg_t, ret_t = self.fun_sigs[e.name]
                self.require_type(arg_t, at, f"argumento de {e.name}", e.arg)
                return ret_t
            raise SemanticError(f"Função '{e.name}' não definida", e)

        raise SemanticError(f"Expressão não suportada: {e}", e)

    def is_list_type(self, t):
        return isinstance(t, str) and t.startswith('List[') and t.endswith(']')

    def list_item_type(self, t):
        return t[5:-1] if self.is_list_type(t) else None

    def types_compatible(self, expected, actual):
        if expected == actual:
            return True
        if self.is_list_type(expected) and self.is_list_type(actual):
            return self.list_item_type(expected) == 'Unknown' or self.list_item_type(actual) == 'Unknown'
        return False

    def require_type(self, expected, actual, ctx, node=None):
        if not self.types_compatible(expected, actual):
            raise SemanticError(f"Erro de tipos em {ctx}: esperado {expected}, obtido {actual}", node)
