import unittest

from error_utils import format_semantic_error
from interpreter import Interpreter, SemanticError
from lexer import build_lexer
from parser import build_parser, set_source_text


def parse_source(parser, source):
    set_source_text(source)
    return parser.parse(source, lexer=build_lexer())


class LFunInterpreterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parser = build_parser(debug=False, write_tables=False)

    def run_program(self, source):
        ast = parse_source(self.parser, source)
        interpreter = Interpreter()
        return interpreter.run(ast)

    def test_function_and_arithmetic(self):
        source = """
            let hp : Int = 8;
            fun dano : Int -> Int;
            let dano x = x * 2;
            dano(hp);
        """
        outputs = self.run_program(source)
        self.assertEqual(outputs, [(16, "Int")])

    def test_when_with_negative_pattern(self):
        source = """
            when(-1) is
                -1 -> 10;
                _ -> 0;
            end;
        """
        outputs = self.run_program(source)
        self.assertEqual(outputs, [(10, "Int")])

    def test_list_builtins(self):
        source = """
            let golpes : List[Int] = [12, 5, 8];
            tamanho(golpes);
            cabeca(golpes);
            cauda(golpes);
            vazio([]);
        """
        outputs = self.run_program(source)
        self.assertEqual(outputs[0], (3, "Int"))
        self.assertEqual(outputs[1], (12, "Int"))
        self.assertEqual(outputs[2], ([5, 8], "List[Int]"))
        self.assertEqual(outputs[3], (True, "Bool"))

    def test_recursive_sum_on_list(self):
        source = """
            fun soma : List[Int] -> Int;
            let soma xs = if vazio(xs) then 0 else cabeca(xs) + soma(cauda(xs));
            soma([1, 2, 3, 4]);
        """
        outputs = self.run_program(source)
        self.assertEqual(outputs, [(10, "Int")])

    def test_syntax_error_has_context(self):
        source = "let hp : Int = 8"
        with self.assertRaises(SyntaxError) as ctx:
            parse_source(self.parser, source)

        message = str(ctx.exception)
        self.assertIn("Erro sintático", message)
        self.assertIn("linha", message)
        self.assertIn("coluna", message)
        self.assertIn("^", message)

    def test_lexical_error_has_context(self):
        source = "let hp : Int = 8; @"
        with self.assertRaises(SyntaxError) as ctx:
            parse_source(self.parser, source)

        message = str(ctx.exception)
        self.assertIn("Erro léxico", message)
        self.assertIn("@", message)
        self.assertIn("^", message)

    def test_semantic_error_has_context(self):
        source = "let hp : Int = true;"
        ast = parse_source(self.parser, source)
        interpreter = Interpreter()

        with self.assertRaises(SemanticError) as ctx:
            interpreter.run(ast)

        message = format_semantic_error(ctx.exception, source)
        self.assertIn("Erro semântico", message)
        self.assertIn("esperado Int, obtido Bool", message)
        self.assertIn("linha", message)
        self.assertIn("coluna", message)
        self.assertIn("^", message)


if __name__ == "__main__":
    unittest.main()
