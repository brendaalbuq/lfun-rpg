def _extract_line_context(source, lexpos):
    if source is None or lexpos is None:
        return None
    if lexpos < 0:
        lexpos = 0
    if lexpos > len(source):
        lexpos = len(source)

    line = source.count('\n', 0, lexpos) + 1
    line_start = source.rfind('\n', 0, lexpos) + 1
    line_end = source.find('\n', lexpos)
    if line_end == -1:
        line_end = len(source)

    line_text = source[line_start:line_end]
    column = (lexpos - line_start) + 1
    return line, column, line_text


def format_source_error(prefix, message, source, lexpos):
    context = _extract_line_context(source, lexpos)
    if context is None:
        return f"{prefix}: {message}"

    line, column, line_text = context
    caret = ' ' * max(column - 1, 0) + '^'
    return f"{prefix}: {message} (linha {line}, coluna {column})\n{line_text}\n{caret}"


def format_semantic_error(error, source):
    node = getattr(error, 'node', None)
    lexpos = getattr(node, 'lexpos', None)
    message = str(error)
    if lexpos is None:
        return f"Erro semântico: {message}"
    return format_source_error("Erro semântico", message, source, lexpos)
