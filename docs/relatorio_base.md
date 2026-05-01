# Relatório técnico — LFun RPG

## 1. Objetivo
Implementar um processador da linguagem LFun com PLY, cobrindo léxico, sintaxe, AST, semântica e execução.

## 2. Decisões técnicas do grupo

### 2.1 Extensões escolhidas
- **Listas** e **Recursão** (as duas extensões oficiais pedidas).
- `String` foi mantido como apoio ao domínio RPG.

### 2.2 Sintaxe de listas
Adotámos `List[T]` em vez de `[T]` por legibilidade no parser e para evitar ambiguidades com literais `[]`.
Trade-off: afasta-se da notação mais curta do enunciado, mas simplifica leitura e mensagens de erro.

### 2.3 Arquitetura semântica em duas fases
1) `semantic_analyzer.py`: valida tipos e símbolos sem executar.
2) `interpreter.py`: executa AST já validada.

Vantagem para defesa: separa responsabilidades e torna falhas de tipo reproduzíveis sem efeitos de runtime.

## 3. Cobertura dos critérios (critério → evidência)
- Reconhecedor léxico → `lexer.py`.
- Reconhecedor sintático → `parser.py`.
- AST + ações semânticas → `ast_nodes.py` + construção no parser.
- Tabela de símbolos e tipos → `semantic_analyzer.py`.
- Execução/interpretação → `interpreter.py`.
- Interface de uso (ficheiro + REPL) → `main.py`.

## 4. Funcionalidades da REPL
- `:env` inspeciona variáveis e assinaturas.
- `:reset` limpa ambiente.
- `:load ficheiro.lf` executa ficheiro sem sair da sessão.

## 5. Limitações atuais
- Funções com um único argumento (curried/múltiplos argumentos não implementados).
- Sem inferência global de tipos.
- Sem geração de C (opcional no enunciado, projeto focado em interpretação).

## 6. Validação
- Testes automatizados em `tests/test_lfun.py`.
- Exemplos completos em `examples/campanha_rpg.lf` e `examples/entrada.lf`.
