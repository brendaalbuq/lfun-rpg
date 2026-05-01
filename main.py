import sys
from lexer import build_lexer
from parser import build_parser, set_source_text
from interpreter import Interpreter, SemanticError, RuntimeErrorLFun, format_value
from error_utils import format_semantic_error

def parse_program(parser, text):
    set_source_text(text)
    lexer = build_lexer()
    ast = parser.parse(text, lexer=lexer)
    return ast


def execute_chunk(parser, interp, text):
    ast = parse_program(parser, text)
    return interp.run(ast)


def print_outputs(outputs):
    for value, typ in outputs:
        print(f"resultado: {format_value(value)} tipo: {typ}")


def render_error(error, source):
    if isinstance(error, SemanticError):
        return format_semantic_error(error, source)
    return str(error)


def split_complete_statements(text):
    lexer = build_lexer()
    lexer.input(text)

    when_depth = 0
    paren_depth = 0
    last_complete_pos = -1

    while True:
        tok = lexer.token()
        if tok is None:
            break
        if tok.type == 'WHEN':
            when_depth += 1
        elif tok.type == 'END' and when_depth > 0:
            when_depth -= 1
        elif tok.type == 'LPAREN':
            paren_depth += 1
        elif tok.type == 'RPAREN' and paren_depth > 0:
            paren_depth -= 1
        elif tok.type == 'SEMI' and when_depth == 0 and paren_depth == 0:
            last_complete_pos = tok.lexpos + 1

    if last_complete_pos == -1:
        return '', text
    return text[:last_complete_pos], text[last_complete_pos:]


def run_file(parser, interp, path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    outputs = execute_chunk(parser, interp, text)
    print_outputs(outputs)


def run_repl(parser, interp):
    print('Modo interativo LFun/RPG. Escreva comandos e termine cada instrução com ";" (Ctrl+D para sair).')
    buffer = ''

    while True:
        prompt = '... ' if buffer.strip() else '>>> '
        try:
            line = input(prompt)
        except EOFError:
            if buffer.strip():
                print('ERRO: comando incompleto no fim da entrada')
            break

        buffer += line + '\n'

        while True:
            try:
                complete_text, remaining = split_complete_statements(buffer)
            except SyntaxError as e:
                print(f"ERRO: {e}")
                buffer = ''
                break

            if not complete_text.strip():
                break

            buffer = remaining
            try:
                outputs = execute_chunk(parser, interp, complete_text)
                print_outputs(outputs)
            except (SyntaxError, SemanticError, RuntimeErrorLFun) as e:
                print(f"ERRO: {render_error(e, complete_text)}")

def main():
    if len(sys.argv) > 2:
        print('Uso: python main.py [ficheiro.lf]')
        sys.exit(1)

    parser = build_parser(write_tables=False, debug=False)
    interp = Interpreter()

    if len(sys.argv) == 2:
        source = ''
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                source = f.read()
            outputs = execute_chunk(parser, interp, source)
            print_outputs(outputs)
        except (SyntaxError, SemanticError, RuntimeErrorLFun) as e:
            print(f"ERRO: {render_error(e, source)}")
            sys.exit(2)
        return

    run_repl(parser, interp)

if __name__ == '__main__':
    main()
