from dataclasses import dataclass
from typing import Any, Dict, Callable
from ast_nodes import *


@dataclass
class FunctionValue:
    arg_name: str
    arg_type: str
    ret_type: str
    body: Any


class SemanticError(Exception):
    def __init__(self, message, node=None):
        super().__init__(message)
        self.node = node


class RuntimeErrorLFun(Exception):
    pass


class Interpreter:
    def __init__(self):
        self.values: Dict[str, Any] = {}
        self.types: Dict[str, str] = {}
        self.fun_sigs: Dict[str, tuple[str, str]] = {}
        self.functions: Dict[str, FunctionValue] = {}

        # Built-ins úteis para o tema RPG. Mantêm a linguagem simples, mas dão sabor ao projeto.
        self.builtins: Dict[str, tuple[str, str, Callable[[Any], Any]]] = {
            'critico': ('Int', 'Int', lambda n: n * 2),
            'bonus': ('Int', 'Int', lambda n: n + 2),
            'vivo': ('Int', 'Bool', lambda hp: hp > 0),
        }

    def run(self, program: Program):
        outputs = []
        for st in program.statements:
            result = self.exec_statement(st)
            if isinstance(st, ExprStmt):
                outputs.append((result[0], result[1]))
        return outputs

    def exec_statement(self, st):
        if isinstance(st, LetDecl):
            if st.name in self.types or st.name in self.functions:
                raise SemanticError(f"Identificador '{st.name}' já foi declarado", st)
            value, typ = self.eval_expr(st.expr, {})
            self.require_type(st.type_name, typ, f"declaração de {st.name}", st)
            self.values[st.name] = value
            self.types[st.name] = typ
            return value, typ

        if isinstance(st, FunSig):
            if st.name in self.fun_sigs:
                raise SemanticError(f"Assinatura da função '{st.name}' já existe", st)
            self.fun_sigs[st.name] = (st.arg_type, st.ret_type)
            return None, 'Unit'

        if isinstance(st, FunDef):
            if st.name not in self.fun_sigs:
                raise SemanticError(f"Função '{st.name}' definida sem assinatura fun", st)
            if st.name in self.functions:
                raise SemanticError(f"Função '{st.name}' já foi definida", st)
            arg_type, ret_type = self.fun_sigs[st.name]
            fun_value = FunctionValue(st.arg_name, arg_type, ret_type, st.expr)
            self.functions[st.name] = fun_value
            try:
                _, body_type = self.eval_expr(st.expr, {st.arg_name: (None, arg_type)}, type_check_only=True)
                self.require_type(ret_type, body_type, f"corpo da função {st.name}", st.expr)
            except SemanticError:
                del self.functions[st.name]
                raise
            return None, 'Unit'

        if isinstance(st, ExprStmt):
            return self.eval_expr(st.expr, {})

        raise RuntimeErrorLFun(f"Instrução não suportada: {st}")

    def eval_expr(self, e, local_env, type_check_only=False):
        if isinstance(e, IntLit):
            return e.value, 'Int'
        if isinstance(e, BoolLit):
            return e.value, 'Bool'
        if isinstance(e, StringLit):
            return e.value, 'String'
        if isinstance(e, ListLit):
            if len(e.items) == 0:
                return ([] if not type_check_only else None), 'List[Unknown]'

            evaluated_values = []
            elem_type = None
            for item in e.items:
                iv, it = self.eval_expr(item, local_env, type_check_only)
                if elem_type is None:
                    elem_type = it
                else:
                    self.require_type(elem_type, it, "elemento da lista", item)
                evaluated_values.append(iv)

            list_type = f"List[{elem_type}]"
            if type_check_only or any(value is None for value in evaluated_values):
                return None, list_type
            return evaluated_values, list_type

        if isinstance(e, Var):
            if e.name in local_env:
                val, typ = local_env[e.name]
                return val, typ
            if e.name in self.values:
                return self.values[e.name], self.types[e.name]
            raise SemanticError(f"Identificador '{e.name}' não declarado", e)

        if isinstance(e, UnaryOp):
            v, t = self.eval_expr(e.expr, local_env, type_check_only)
            if e.op == '-':
                self.require_type('Int', t, 'operador unário -', e)
                if type_check_only or v is None:
                    return None, 'Int'
                return -v, 'Int'
            if e.op == 'not':
                self.require_type('Bool', t, 'operador not', e)
                if type_check_only or v is None:
                    return None, 'Bool'
                return not v, 'Bool'

        if isinstance(e, BinOp):
            lv, lt = self.eval_expr(e.left, local_env, type_check_only)
            rv, rt = self.eval_expr(e.right, local_env, type_check_only)
            op = e.op
            if op in ['+', '-', '*', '/', '%']:
                # Extensão String: concatenação apenas com + entre strings.
                if op == '+' and lt == 'String' and rt == 'String':
                    if type_check_only or lv is None or rv is None:
                        return None, 'String'
                    return lv + rv, 'String'
                self.require_type('Int', lt, f"lado esquerdo de {op}", e.left)
                self.require_type('Int', rt, f"lado direito de {op}", e.right)
                if type_check_only or lv is None or rv is None:
                    return None, 'Int'
                if op == '+': return lv + rv, 'Int'
                if op == '-': return lv - rv, 'Int'
                if op == '*': return lv * rv, 'Int'
                if op == '/':
                    if rv == 0: raise RuntimeErrorLFun('Divisão por zero')
                    return lv // rv, 'Int'
                if op == '%':
                    if rv == 0: raise RuntimeErrorLFun('Resto por zero')
                    return lv % rv, 'Int'
            if op in ['<', '<=', '>', '>=']:
                self.require_type('Int', lt, f"comparação {op}", e.left)
                self.require_type('Int', rt, f"comparação {op}", e.right)
                if type_check_only or lv is None or rv is None: return None, 'Bool'
                return eval(f"lv {op} rv"), 'Bool'
            if op in ['==', '!=']:
                if lt != rt:
                    raise SemanticError(f"Comparação {op} entre tipos incompatíveis: {lt} e {rt}", e)
                if type_check_only or lv is None or rv is None: return None, 'Bool'
                return (lv == rv if op == '==' else lv != rv), 'Bool'
            if op in ['and', 'or']:
                self.require_type('Bool', lt, f"lado esquerdo de {op}", e.left)
                self.require_type('Bool', rt, f"lado direito de {op}", e.right)
                if type_check_only or lv is None or rv is None: return None, 'Bool'
                return (lv and rv if op == 'and' else lv or rv), 'Bool'

        if isinstance(e, IfExpr):
            cv, ct = self.eval_expr(e.cond, local_env, type_check_only)
            self.require_type('Bool', ct, 'condição do if', e.cond)
            _, tt = self.eval_expr(e.then_expr, local_env, type_check_only=True)
            _, et = self.eval_expr(e.else_expr, local_env, type_check_only=True)
            if tt != et:
                raise SemanticError(f"Ramos do if com tipos diferentes: {tt} e {et}", e)
            if type_check_only or cv is None:
                return None, tt
            if cv:
                return self.eval_expr(e.then_expr, local_env, type_check_only=False)
            return self.eval_expr(e.else_expr, local_env, type_check_only=False)

        if isinstance(e, WhenExpr):
            target_v, target_t = self.eval_expr(e.target, local_env, type_check_only)
            result_type = None
            fallback_case = None
            for case in e.cases:
                _, ct = self.eval_expr(case.expr, local_env, type_check_only=True)
                result_type = ct if result_type is None else result_type
                if ct != result_type:
                    raise SemanticError('Todos os casos do when devem devolver o mesmo tipo', case.expr)
                for pat in case.patterns:
                    if isinstance(pat, Otherwise):
                        if fallback_case is None:
                            fallback_case = case
                    else:
                        _, pt = self.eval_expr(pat, local_env, type_check_only=True)
                        if pt != target_t:
                            raise SemanticError(f"Padrão do when tem tipo {pt}, mas o alvo tem tipo {target_t}", pat)
            if result_type is None:
                raise SemanticError('Expressão when sem casos', e)
            if type_check_only or target_v is None:
                return None, result_type
            for case in e.cases:
                for pat in case.patterns:
                    if isinstance(pat, Otherwise):
                        continue
                    pv, _ = self.eval_expr(pat, local_env, type_check_only=False)
                    if pv == target_v:
                        return self.eval_expr(case.expr, local_env, type_check_only=False)
            if fallback_case is not None:
                return self.eval_expr(fallback_case.expr, local_env, type_check_only=False)
            raise RuntimeErrorLFun('Nenhum caso do when foi aplicável')

        if isinstance(e, Call):
            av, at = self.eval_expr(e.arg, local_env, type_check_only)
            if e.name in ('tamanho', 'vazio', 'cabeca', 'cauda'):
                if not self.is_list_type(at):
                    raise SemanticError(f"Argumento de {e.name} deve ser uma lista", e.arg)
                item_type = self.list_item_type(at)
                if e.name == 'tamanho':
                    if type_check_only or av is None:
                        return None, 'Int'
                    return len(av), 'Int'
                if e.name == 'vazio':
                    if type_check_only or av is None:
                        return None, 'Bool'
                    return len(av) == 0, 'Bool'
                if e.name == 'cabeca':
                    if type_check_only or av is None:
                        return None, item_type
                    if len(av) == 0:
                        raise RuntimeErrorLFun('cabeca aplicada a lista vazia')
                    return av[0], item_type
                if e.name == 'cauda':
                    if type_check_only or av is None:
                        return None, at
                    if len(av) == 0:
                        return [], at
                    return av[1:], at
            if e.name in self.builtins:
                arg_t, ret_t, fn = self.builtins[e.name]
                self.require_type(arg_t, at, f"argumento de {e.name}", e.arg)
                if type_check_only or av is None:
                    return None, ret_t
                return fn(av), ret_t
            if e.name not in self.functions:
                if type_check_only and e.name in self.fun_sigs:
                    arg_t, ret_t = self.fun_sigs[e.name]
                    self.require_type(arg_t, at, f"argumento de {e.name}", e.arg)
                    return None, ret_t
                raise SemanticError(f"Função '{e.name}' não definida", e)
            f = self.functions[e.name]
            self.require_type(f.arg_type, at, f"argumento de {e.name}", e.arg)
            if type_check_only or av is None:
                return None, f.ret_type
            try:
                return self.eval_expr(f.body, {**local_env, f.arg_name: (av, f.arg_type)}, type_check_only=False)
            except RecursionError as exc:
                raise RuntimeErrorLFun('Recursão excedeu o limite máximo de chamadas') from exc

        raise RuntimeErrorLFun(f"Expressão não suportada: {e}")

    def is_list_type(self, type_name):
        return isinstance(type_name, str) and type_name.startswith('List[') and type_name.endswith(']')

    def list_item_type(self, type_name):
        if not self.is_list_type(type_name):
            return None
        return type_name[5:-1]

    def types_compatible(self, expected, actual):
        if expected == actual:
            return True
        if self.is_list_type(expected) and self.is_list_type(actual):
            expected_item = self.list_item_type(expected)
            actual_item = self.list_item_type(actual)
            if expected_item == 'Unknown' or actual_item == 'Unknown':
                return True
        return False

    def require_type(self, expected, actual, ctx, node=None):
        if not self.types_compatible(expected, actual):
            raise SemanticError(f"Erro de tipos em {ctx}: esperado {expected}, obtido {actual}", node)

def format_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, list):
        return "[" + ", ".join(format_value(item) for item in v) + "]"
    return str(v)
