# Auditoria técnica do projeto LFun-RPG (maio/2026)

## Estado geral

**Veredito:** o projeto está **funcional e bem acima de um protótipo mínimo**. Implementa análise léxica, sintática, AST, análise semântica e interpretação, conforme o enunciado base.

## Cobertura dos requisitos do enunciado

### 1) Gramática concreta
- Existe gramática implementada com PLY/Yacc (`parser.py`) para declarações, funções, expressões, `if`, `when`, chamadas e listas.
- Precedência de operadores está definida.

### 2) Reconhecedor léxico (lex)
- Lexer com PLY/lex (`lexer.py`), incluindo:
  - identificadores, inteiros, strings;
  - operadores aritméticos, relacionais e lógicos;
  - comentários de uma linha (`--`) e bloco (`{- -}`).
- Erros léxicos com contexto (linha/coluna/ponteiro).

### 3) Reconhecedor sintático (yacc)
- Parser funcional com produção de AST.
- Suporte a instruções e expressões esperadas no enunciado.
- Erros sintáticos com contexto detalhado.

### 4) AST + ações semânticas de tradução
- AST explícita em `ast_nodes.py`.
- Ações do parser constroem nós semânticos para todas as construções principais.

### 5) Análise semântica + tabela de símbolos + tipos
- Feita no interpretador (`interpreter.py`):
  - tabela de variáveis/tipos;
  - tabela de assinaturas e definições de funções;
  - verificação de tipos em operadores, `if`, `when`, chamadas.

### 6) Execução/interpretação
- Interpretação completa da AST em `Interpreter.eval_expr`.
- Modo ficheiro e REPL (`main.py`).

## Extensões

O enunciado pede 2 extensões da lista. Vocês têm:
- **Listas** (tipo `List[T]`, literais e built-ins `tamanho/vazio/cabeca/cauda`);
- **Recursão** (testada com soma de lista e outros exemplos);
- Extra adicional: **String**.

Isto é positivo para avaliação, desde que esteja bem documentado no relatório.

## Pontos fortes

1. **Arquitetura limpa e separada por responsabilidade** (`lexer`, `parser`, `ast`, `interpreter`, `main`).
2. **Mensagens de erro com contexto de origem** (excelente para defesa).
3. **Testes unitários úteis** para sintaxe, semântica e recursão.
4. **Cobertura real do enunciado** (não está “só para demos”).

## Lacunas / riscos para a entrega

1. **Inconsistência entre documentação e implementação das extensões**
   - `docs/relatorio_base.md` afirma apenas `String` + built-ins RPG, mas o código implementa claramente listas e recursão.
   - Risco: professor interpretar como relatório incompleto.

2. **Forma de tipo de lista diferente do enunciado**
   - Implementado: `List[Int]`.
   - Enunciado sugere: `[T]`.
   - Não é necessariamente erro, mas precisa de **justificação explícita** no relatório.

3. **Sem geração de código C**
   - É opcional no enunciado, então ok. Mas convém dizer claramente que a abordagem escolhida foi interpretação.

4. **`pytest` falha por path/import**
   - `python -m unittest` passa, mas `pytest` falha em import (`ModuleNotFoundError` para `error_utils`).
   - Não bloqueia se vocês só prometem unittest, porém pode passar imagem de setup frágil.

5. **Possíveis sinais de “texto genérico/IA” no relatório**
   - Algumas secções estão demasiado genéricas e pouco “vossas” (sem decisões concretas, sem trade-offs, sem dificuldades reais, sem exemplos de erros encontrados).

## “Cara de IA”: o que revisar antes de entregar

Para reduzir risco de parecer texto gerado:

1. **Adicionar decisões reais do grupo**
   - Por que escolheram `List[T]` e não `[T]`?
   - Por que chamadas unárias (`f(x)`) e não múltiplos argumentos?
   - Como resolveram precedência e ambiguidades no `when`?

2. **Incluir problemas concretos e correções**
   - Ex.: conflito de precedência entre `-` unário e `-` binário;
   - Ex.: erros de posição no parser e solução com `lineno/lexpos`.

3. **Colocar exemplos próprios do vosso domínio RPG**
   - Não só “força/dano”; incluir 2-3 casos de teste que vocês realmente usaram e resultados obtidos.

4. **Mostrar limitações conhecidas (honestas)**
   - Ex.: sem funções de múltiplos parâmetros, sem inferência de tipos, sem otimização, etc.

## Recomendação final (prioridade alta)

1. **Atualizar o relatório** para refletir exatamente o que existe no código (listas + recursão + strings).
2. **Adicionar secção “Decisões de projeto e justificações”** com escolhas sintáticas e semânticas.
3. **Adicionar secção “Validação/Testes”** com tabela (caso, entrada, resultado esperado, resultado obtido).
4. **Padronizar comandos de teste** no README e no relatório (indicar `python -m unittest discover -s tests -v`).
5. **Preparar defesa** com 3 demos: 
   - programa válido com funções + if;
   - programa com `when` e padrões;
   - erro semântico com mensagem contextual.

## Conclusão objetiva

**Sim, o projeto atende quase todos os requisitos essenciais do professor e está funcional.**

O que falta para ficar “à prova de defesa” não é tanto código, mas **coerência e profundidade do relatório** (para não parecer texto genérico/IA e para mostrar autoria técnica clara).
