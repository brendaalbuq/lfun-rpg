from dataclasses import dataclass
from typing import Any, List


@dataclass
class Program:
    statements: List[Any]


@dataclass
class LetDecl:
    name: str
    type_name: str
    expr: Any


@dataclass
class FunSig:
    name: str
    arg_type: str
    ret_type: str


@dataclass
class FunDef:
    name: str
    arg_name: str
    expr: Any


@dataclass
class ExprStmt:
    expr: Any


@dataclass
class IntLit:
    value: int


@dataclass
class BoolLit:
    value: bool


@dataclass
class StringLit:
    value: str


@dataclass
class ListLit:
    items: List[Any]


@dataclass
class Var:
    name: str


@dataclass
class BinOp:
    op: str
    left: Any
    right: Any


@dataclass
class UnaryOp:
    op: str
    expr: Any


@dataclass
class IfExpr:
    cond: Any
    then_expr: Any
    else_expr: Any


@dataclass
class Call:
    name: str
    arg: Any


@dataclass
class WhenCase:
    patterns: List[Any]
    expr: Any


@dataclass
class WhenExpr:
    target: Any
    cases: List[WhenCase]


@dataclass
class Otherwise:
    pass
