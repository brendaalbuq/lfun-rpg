# LFun RPG — Interpretador com análise semântica em duas fases

Projeto de Processamento de Linguagens (2025/2026) com PLY (lex/yacc).

## O que já está implementado

- Lexer completo com comentários `--` e `{- -}`.
- Parser com precedência de operadores, `if` e `when`.
- AST explícita.
- **Semântica em duas fases**:
  1) validação de tipos/tabela de símbolos (`semantic_analyzer.py`);
  2) execução (`interpreter.py`).
- REPL com comandos de produtividade: `:env`, `:reset`, `:load ficheiro.lf`.

## Extensões escolhidas

1. **Listas** (`List[T]`, `[]`, built-ins `tamanho`, `vazio`, `cabeca`, `cauda`).
2. **Recursão** (funções com assinatura + definição e chamadas recursivas).

Também foi incluído `String` por utilidade prática no domínio RPG.

## Execução

```bash
pip install -r requirements.txt
python main.py examples/campanha_rpg.lf
```

Modo interativo:

```bash
python main.py
```

Comandos REPL:
- `:env` mostra ambiente atual (declarações e assinaturas);
- `:reset` limpa ambiente;
- `:load examples/campanha_rpg.lf` carrega e executa ficheiro.

## Testes

```bash
python -m unittest discover -s tests -v
```

## Mapeamento critério -> evidência

- Léxico: `lexer.py`
- Sintático + AST: `parser.py`, `ast_nodes.py`
- Semântico (tipos, símbolos): `semantic_analyzer.py`
- Execução/interpretação: `interpreter.py`
- REPL e integração: `main.py`
- Cenários de uso: `examples/`
