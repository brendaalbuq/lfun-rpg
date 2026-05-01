from dataclasses import dataclass
from typing import Any, Dict, Callable

from ast_nodes import *
from semantic_analyzer import SemanticAnalyzer, SemanticError


@dataclass
class FunctionValue:
    arg_name: str
    arg_type: str
    ret_type: str
    body: Any


class RuntimeErrorLFun(Exception):
    pass


class Interpreter:
    """Fase 2: execução. Recebe programa já validado semanticamente."""

    def __init__(self):
        self.values: Dict[str, Any] = {}
        self.types: Dict[str, str] = {}
        self.fun_sigs: Dict[str, tuple[str, str]] = {}
        self.functions: Dict[str, FunctionValue] = {}
        self.builtins: Dict[str, tuple[str, str, Callable[[Any], Any]]] = {
            'critico': ('Int', 'Int', lambda n: n * 2),
            'bonus': ('Int', 'Int', lambda n: n + 2),
            'vivo': ('Int', 'Bool', lambda hp: hp > 0),
        }

    def analyze(self, program: Program):
        analyzer = SemanticAnalyzer()
        analyzer.analyze(program)

    def run(self, program: Program):
        self.analyze(program)
        outputs = []
        for st in program.statements:
            result = self.exec_statement(st)
            if isinstance(st, ExprStmt):
                outputs.append((result[0], result[1]))
        return outputs

    def exec_statement(self, st):
        if isinstance(st, LetDecl):
            value, typ = self.eval_expr(st.expr, {})
            self.values[st.name] = value
            self.types[st.name] = typ
            return value, typ
        if isinstance(st, FunSig):
            self.fun_sigs[st.name] = (st.arg_type, st.ret_type)
            return None, 'Unit'
        if isinstance(st, FunDef):
            arg_type, ret_type = self.fun_sigs[st.name]
            self.functions[st.name] = FunctionValue(st.arg_name, arg_type, ret_type, st.expr)
            return None, 'Unit'
        if isinstance(st, ExprStmt):
            return self.eval_expr(st.expr, {})
        raise RuntimeErrorLFun(f"Instrução não suportada: {st}")

    def eval_expr(self, e, local_env):
        if isinstance(e, IntLit): return e.value, 'Int'
        if isinstance(e, BoolLit): return e.value, 'Bool'
        if isinstance(e, StringLit): return e.value, 'String'
        if isinstance(e, ListLit):
            values = []
            elem_t = 'Unknown'
            for item in e.items:
                v, t = self.eval_expr(item, local_env)
                values.append(v)
                elem_t = t if elem_t == 'Unknown' else elem_t
            return values, f'List[{elem_t}]'
        if isinstance(e, Var):
            if e.name in local_env: return local_env[e.name]
            return self.values[e.name], self.types[e.name]
        if isinstance(e, UnaryOp):
            v, t = self.eval_expr(e.expr, local_env)
            return (-v, 'Int') if e.op == '-' else (not v, 'Bool')
        if isinstance(e, BinOp):
            lv, lt = self.eval_expr(e.left, local_env)
            rv, rt = self.eval_expr(e.right, local_env)
            op = e.op
            if op == '+' and lt == 'String' and rt == 'String': return lv + rv, 'String'
            if op == '+': return lv + rv, 'Int'
            if op == '-': return lv - rv, 'Int'
            if op == '*': return lv * rv, 'Int'
            if op == '/':
                if rv == 0: raise RuntimeErrorLFun('Divisão por zero')
                return lv // rv, 'Int'
            if op == '%':
                if rv == 0: raise RuntimeErrorLFun('Resto por zero')
                return lv % rv, 'Int'
            if op == '<': return lv < rv, 'Bool'
            if op == '<=': return lv <= rv, 'Bool'
            if op == '>': return lv > rv, 'Bool'
            if op == '>=': return lv >= rv, 'Bool'
            if op == '==': return lv == rv, 'Bool'
            if op == '!=': return lv != rv, 'Bool'
            if op == 'and': return lv and rv, 'Bool'
            if op == 'or': return lv or rv, 'Bool'
        if isinstance(e, IfExpr):
            cv, _ = self.eval_expr(e.cond, local_env)
            return self.eval_expr(e.then_expr if cv else e.else_expr, local_env)
        if isinstance(e, WhenExpr):
            target_v, _ = self.eval_expr(e.target, local_env)
            fallback = None
            for case in e.cases:
                for pat in case.patterns:
                    if isinstance(pat, Otherwise):
                        fallback = case
                        continue
                    pv, _ = self.eval_expr(pat, local_env)
                    if pv == target_v:
                        return self.eval_expr(case.expr, local_env)
            if fallback is not None:
                return self.eval_expr(fallback.expr, local_env)
            raise RuntimeErrorLFun('Nenhum caso do when foi aplicável')
        if isinstance(e, Call):
            av, at = self.eval_expr(e.arg, local_env)
            if e.name == 'tamanho': return len(av), 'Int'
            if e.name == 'vazio': return len(av) == 0, 'Bool'
            if e.name == 'cabeca':
                if not av: raise RuntimeErrorLFun('cabeca aplicada a lista vazia')
                return av[0], at[5:-1]
            if e.name == 'cauda': return av[1:] if av else [], at
            if e.name in self.builtins:
                _, ret_t, fn = self.builtins[e.name]
                return fn(av), ret_t
            f = self.functions[e.name]
            return self.eval_expr(f.body, {**local_env, f.arg_name: (av, f.arg_type)})
        raise RuntimeErrorLFun(f"Expressão não suportada: {e}")



def format_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, list):
        return '[' + ', '.join(format_value(x) for x in v) + ']'
    return str(v)
