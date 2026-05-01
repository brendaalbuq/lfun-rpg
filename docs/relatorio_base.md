# Relatório base - Calculadora de RPG em LFun

## 1. Introdução

O objetivo do trabalho foi desenvolver uma aplicação em Python, recorrendo à biblioteca PLY, capaz de processar uma linguagem funcional simplificada. A linguagem criada tem o tema de uma calculadora de RPG, permitindo calcular atributos, dano, estados de vida e condições de personagens.

A escolha do tema facilita a apresentação porque os exemplos são intuitivos: força, vida, dano crítico, bónus e estados como vivo, crítico ou morto.

## 2. Linguagem desenvolvida

A linguagem suporta instruções semelhantes à LFun indicada no enunciado:

```lf
let forca : Int = 15;
fun dano : Int -> Int;
let dano n = n * 2;
dano(forca);
```

O resultado esperado é:

```txt
resultado: 30 tipo: Int
```

## 3. Gramática concreta usada

De forma resumida, a gramática aceita:

```txt
program     -> statements
statement   -> let id : type = expr ;
statement   -> fun id : type -> type ;
statement   -> let id id = expr ;
statement   -> expr ;
type        -> Int | Bool | String
expr        -> number | true | false | string | id
expr        -> expr op expr
expr        -> not expr | - expr
expr        -> id ( expr )
expr        -> if expr then expr else expr
expr        -> when ( expr ) is cases end
case        -> patterns -> expr ;
pattern     -> number | true | false | string | _
```

## 4. Análise léxica

O reconhecedor léxico identifica palavras reservadas, identificadores, números inteiros, strings, operadores, parênteses, `;`, `:`, `->`, comentários de uma linha com `--` e comentários de várias linhas com `{- ... -}`.

## 5. Análise sintática e AST

O parser foi implementado com PLY Yacc. Para cada regra principal é criado um nó da AST. Exemplos de nós usados:

- `LetDecl`, para declarações com tipo;
- `FunSig`, para assinaturas de funções;
- `FunDef`, para definições de funções;
- `BinOp`, para operações binárias;
- `IfExpr`, para condicionais;
- `WhenExpr`, para seleção de casos.

## 6. Análise semântica

A análise semântica usa tabelas de símbolos para guardar variáveis e funções. O interpretador verifica:

- se uma variável já foi declarada;
- se uma variável foi usada sem declaração;
- se a expressão atribuída corresponde ao tipo declarado;
- se uma função foi declarada antes da definição;
- se o tipo do argumento e do resultado da função está correto;
- se operações aritméticas usam `Int`;
- se operações lógicas usam `Bool`;
- se os ramos de `if` e `when` devolvem o mesmo tipo.

## 7. Extensões implementadas

Foram implementadas duas extensões simples e adequadas ao tema:

1. Tipo `String`, útil para devolver estados textuais de personagens, como `"vivo"`, `"morto"` ou `"critico"`.
2. Funções pré-definidas de RPG: `critico(Int) -> Int`, `bonus(Int) -> Int` e `vivo(Int) -> Bool`.

## 8. Testes

Exemplo válido:

```lf
let forca : Int = 15;
fun dano : Int -> Int;
let dano n = n * 2;
dano(forca);
```

Exemplo com erro semântico:

```lf
let ativo : Bool = true;
let erro : Int = ativo;
```

Este exemplo deve ser rejeitado porque `ativo` tem tipo `Bool`, mas a variável `erro` foi declarada como `Int`.

## 9. Conclusão

A solução desenvolvida cumpre as fases principais do trabalho: análise léxica, análise sintática, construção da AST, análise semântica com tabela de símbolos e avaliação da árvore. O tema de RPG torna os exemplos mais fáceis de compreender sem alterar a base funcional pedida no enunciado.
