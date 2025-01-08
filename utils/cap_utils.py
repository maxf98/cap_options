import ast
import re

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

class FunctionParser(ast.NodeTransformer):

    def __init__(self, fs, f_assigns):
        super().__init__()
        self._fs = fs
        self._f_assigns = f_assigns

    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name):
            f_sig = ast.unparse(node).strip()
            f_name = ast.unparse(node.func).strip()
            self._fs[f_name] = f_sig
        return node

    def visit_Assign(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Call):
            assign_str = ast.unparse(node).strip()
            f_name = ast.unparse(node.value.func).strip()
            self._f_assigns[f_name] = assign_str
        return node


def extract_code(res):
    if '```python' in res:
        pattern = r'```python\n(.*?)```'
    elif '```Python' in res:
        pattern = r'```Python\n(.*?)```'
    elif '```' in res:
        pattern = r'```\n(.*?)```'
    else:
        pattern = r'.*'
    code_string = re.search(pattern, res, re.DOTALL)
    if not code_string:
        print('input: ', res)
        raise ValueError('extract failed')
    if pattern == r'.*':
        code_string = code_string.group(0).strip()
    else:
        code_string = code_string.group(1).strip()

    lines = code_string.splitlines()
    if '```' in code_string:
        lines = lines[1:]
    lines = [line for line in lines if line.strip() != '']
    code_string = "\n".join(lines)

    return code_string


def exec_safe(code_str, gvars=None, lvars=None):
    if '```' in code_str:
        code_str = extract_code(code_str)

    if 'import' in code_str:
        import_pattern = re.compile(r'^\s*(import .*|from .* import .*)$', re.MULTILINE)
        code_str = import_pattern.sub('', code_str).strip()
    assert '__' not in code_str

    if gvars is None:
        gvars = {}
    if lvars is None:
        lvars = {}
    empty_fn = lambda *args, **kwargs: None
    custom_gvars = merge_dicts([
        gvars,
        {'exec': empty_fn, 'eval': empty_fn}
    ])
    # print(f'THE CODE STRING IS\n{code_str}\nEND')
    exec(code_str, custom_gvars, lvars)


def merge_dicts(dicts):
    return {
        k: v
        for d in dicts
        for k, v in d.items()
    }


def var_exists(name, all_vars):
    try:
        eval(name, all_vars)
    except:
        exists = False
    else:
        exists = True
    return exists

def print_code(code):
    print(highlight(f'{code}', PythonLexer(), TerminalFormatter()))
