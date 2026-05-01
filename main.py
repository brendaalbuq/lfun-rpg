import sys
from lexer import build_lexer
from parser import build_parser, set_source_text
from interpreter import Interpreter, RuntimeErrorLFun, format_value
from semantic_analyzer import SemanticError
from error_utils import format_semantic_error


def parse_program(parser, text):
    set_source_text(text)
    return parser.parse(text, lexer=build_lexer())


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
        if tok.type == 'WHEN': when_depth += 1
        elif tok.type == 'END' and when_depth > 0: when_depth -= 1
        elif tok.type == 'LPAREN': paren_depth += 1
        elif tok.type == 'RPAREN' and paren_depth > 0: paren_depth -= 1
        elif tok.type == 'SEMI' and when_depth == 0 and paren_depth == 0:
            last_complete_pos = tok.lexpos + 1
    if last_complete_pos == -1:
        return '', text
    return text[:last_complete_pos], text[last_complete_pos:]


def run_source(parser, interp, source):
    outputs = execute_chunk(parser, interp, source)
    print_outputs(outputs)


def print_env(interp):
    print('--- Ambiente ---')
    if not interp.values and not interp.functions:
        print('(vazio)')
        return
    for name, value in interp.values.items():
        print(f"let {name} : {interp.types[name]} = {format_value(value)}")
    for name, (arg_t, ret_t) in interp.fun_sigs.items():
        print(f"fun {name} : {arg_t} -> {ret_t}")


def run_repl(parser):
    print('LFun REPL. Comandos: :env, :reset, :load ficheiro.lf, :help, :quit')
    interp = Interpreter()
    buffer = ''
    while True:
        prompt = '... ' if buffer.strip() else '>>> '
        try:
            line = input(prompt)
        except EOFError:
            break

        stripped = line.strip()
        if not buffer.strip() and stripped.startswith(':'):
            if stripped in (':quit', ':q'):
                break
            if stripped == ':help':
                print('Comandos: :env | :reset | :load ficheiro.lf | :quit')
                continue
            if stripped == ':env':
                print_env(interp)
                continue
            if stripped == ':reset':
                interp = Interpreter()
                print('Ambiente reiniciado.')
                continue
            if stripped.startswith(':load '):
                path = stripped[6:].strip()
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        run_source(parser, interp, f.read())
                except Exception as e:
                    print(f'ERRO: {e}')
                continue
            print('Comando desconhecido. Use :help.')
            continue

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
                run_source(parser, interp, complete_text)
            except (SyntaxError, SemanticError, RuntimeErrorLFun) as e:
                print(f"ERRO: {render_error(e, complete_text)}")


def main():
    parser = build_parser(write_tables=False, debug=False)
    if len(sys.argv) > 2:
        print('Uso: python main.py [ficheiro.lf]')
        sys.exit(1)
    if len(sys.argv) == 2:
        source = ''
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                source = f.read()
            interp = Interpreter()
            run_source(parser, interp, source)
        except (SyntaxError, SemanticError, RuntimeErrorLFun) as e:
            print(f"ERRO: {render_error(e, source)}")
            sys.exit(2)
        return
    run_repl(parser)


if __name__ == '__main__':
    main()
