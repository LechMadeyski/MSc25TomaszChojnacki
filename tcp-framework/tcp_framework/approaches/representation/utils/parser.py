from typing import Callable

import tree_sitter_java
from tree_sitter import Language, Node, Parser

_parser = Parser(Language(tree_sitter_java.language()))


def _tokens(code: str, condition: Callable[[Node], bool]) -> str:
    data = bytes(code, "utf8")
    result: list[str] = []

    def _traverse(node: Node) -> None:
        if node.child_count == 0:
            if condition(node):
                result.append(data[node.start_byte : node.end_byte].decode())
        else:
            for child in node.children:
                _traverse(child)

    tree = _parser.parse(data)
    _traverse(tree.root_node)
    return " ".join(result)


def normalize_code(code: str) -> str:
    return _tokens(code, lambda _: True)


def extract_code_identifiers(code: str) -> str:
    return _tokens(code, lambda node: node.type in ("identifier", "type_identifier"))
