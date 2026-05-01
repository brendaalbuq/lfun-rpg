# Calculadora de RPG em LFun

Projeto prático de Processamento de Linguagens: interpretador de uma linguagem funcional simples, com tema de RPG.

A linguagem permite:

- expressões aritméticas `+ - * / %`;
- expressões booleanas `< <= > >= == != and or not`;
- definições `let nome : Tipo = expressão;`;
- funções com assinatura `fun nome : Tipo -> Tipo;` e definição `let nome arg = expressão;`;
- condicional `if condição then expr1 else expr2`;
- seleção de casos `when (...) is ... end;` com padrões múltiplos e negativos (`-1, 1 -> ...`);
- comentários `--` e `{- -}`;
- tipos `Int`, `Bool` e extensões oficiais `String`, **Recursão** e **Listas**;
- listas com tipo explícito `List[T]`, literais (`[1, 2, 3]`) e built-ins `tamanho`, `vazio`, `cabeca`, `cauda`;
- funções RPG pré-definidas: `critico`, `bonus`, `vivo`.

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py examples/entrada.lf
```

Também pode testar recursão em:

```bash
python main.py examples/recursao.lf
```

Exemplo focado em listas:

```bash
python main.py examples/listas_rpg.lf
```

Também pode ser usado pelo terminal:

```bash
python main.py
```

No modo interativo, o interpretador lê comandos incrementalmente e executa assim que encontra uma instrução completa terminada em `;`.

## Erros com contexto

Erros léxicos, sintáticos e semânticos incluem posição no código:

- linha e coluna;
- trecho da linha com marcador `^` na posição do erro.

Isso facilita o diagnóstico quando uma expressão é inválida ou tem incompatibilidade de tipos.

## Testes

```bash
python -m unittest discover -s tests -v
```

## Exemplo

```lf
let forca : Int = 15;
fun dano : Int -> Int;
let dano n = n * 2;
dano(forca);
```

Saída esperada:

```txt
resultado: 30 tipo: Int
```

## Estrutura

- `lexer.py`: reconhecedor léxico com PLY Lex.
- `parser.py`: reconhecedor sintático com PLY Yacc e construção da AST.
- `ast_nodes.py`: classes da árvore de sintaxe abstrata.
- `interpreter.py`: análise semântica, tabela de símbolos, verificação de tipos e avaliação.
- `main.py`: entrada do programa e apresentação dos resultados.
- `error_utils.py`: formatação de erros com linha/coluna/trecho.
- `examples/`: exemplos válidos (incluindo recursão e listas) e exemplo com erro semântico.
- `tests/`: suíte de testes unitários.
