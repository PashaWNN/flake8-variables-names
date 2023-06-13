import ast
from typing import List, Tuple, Union

from flake8_variables_names.list_helpers import flat


def extract_names_from_node(node: Union[ast.expr, ast.stmt]) -> List[ast.Name]:
    if isinstance(node, ast.Name):
        return [node]
    if isinstance(node, ast.Assign):
        nodes = []
        for target in node.targets:
            nodes.extend(extract_names_from_node(target))
        return nodes
    if isinstance(node, ast.AnnAssign):
        return extract_names_from_node(node.target)
    if isinstance(node, ast.Starred):
        return extract_names_from_node(node.value)
    if isinstance(node, ast.Tuple):
        nodes = []
        for elt in node.elts:
            nodes.extend(extract_names_from_node(elt))
        return nodes
    return []


def get_var_names_from_assignment(
    assignment_node: Union[ast.Assign, ast.AnnAssign],
) -> List[Tuple[str, ast.AST]]:
    return [(n.id, n) for n in extract_names_from_node(assignment_node)]


def get_var_names_from_funcdef(funcdef_node: ast.FunctionDef) -> List[Tuple[str, ast.arg]]:
    vars_info = []
    for arg in funcdef_node.args.args:
        vars_info.append(
            (arg.arg, arg),
        )
    return vars_info


def get_var_names_from_for(for_node: ast.For) -> List[Tuple[str, ast.AST]]:
    if isinstance(for_node.target, ast.Name):
        return [(for_node.target.id, for_node.target)]
    elif isinstance(for_node.target, ast.Tuple):
        return [(n.id, n) for n in for_node.target.elts if isinstance(n, ast.Name)]
    return []


def extract_all_variable_names(ast_tree: ast.AST) -> List[Tuple[str, ast.AST]]:
    var_info: List[Tuple[str, ast.AST]] = []
    assignments = [n for n in ast.walk(ast_tree) if isinstance(n, (ast.Assign, ast.AnnAssign))]
    var_info += flat([get_var_names_from_assignment(a) for a in assignments])
    funcdefs = [n for n in ast.walk(ast_tree) if isinstance(n, ast.FunctionDef)]
    var_info += flat([get_var_names_from_funcdef(f) for f in funcdefs])
    fors = [n for n in ast.walk(ast_tree) if isinstance(n, ast.For)]
    var_info += flat([get_var_names_from_for(f) for f in fors])
    return var_info
