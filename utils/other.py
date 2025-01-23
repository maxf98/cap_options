# @dataclass
# class AABBBoundingBox:
#     """Axis-aligned bounding box, represented by two points"""

#     minPoint: Point3D
#     maxPoint: Point3D

#     @property
#     def size(self) -> tuple[float, float, float]:
#         """return size of bounding box as tuple of (width, depth, height)"""
#         return (
#             abs(self.minPoint.x - self.maxPoint.x),
#             abs(self.minPoint.y - self.maxPoint.y),
#             abs(self.minPoint.z - self.maxPoint.z),
#         )

# def get_bbox(self, obj: TaskObject) -> AABBBoundingBox:
#     """gets the bounding box of an object"""
#     aabb_min, aabb_max = self.env.getBoundingBox(obj.id)

#     return AABBBoundingBox(Point3D.from_xyz(aabb_min), Point3D.from_xyz(aabb_max))


# def fgen_lmp(f_name, f_sig, all_vars, f_description=None):
#     messages = [{"role": "system", "content": FGEN_PROMPT}, {"role": "user", "content": f"write the function code for {f_name} with signature {f_sig}"}]
#     response = query_llm(messages)
#     f_src = parse_code_response(response)

#     lvars = {}

#     exec_safe(f_src, all_vars, lvars)

#     f = lvars[f_name]

#     return f, f_src


# def create_new_fs_from_code(code_str, gvars):
#     if '```' in code_str:
#         code_str = extract_code(code_str)

#     fs, f_assigns = {}, {}
#     f_parser = FunctionParser(fs, f_assigns)
#     f_parser.visit(ast.parse(code_str))
#     for f_name, f_assign in f_assigns.items():
#         if f_name in fs:
#             fs[f_name] = f_assign

#     new_fs = {}
#     srcs = {}
#     for f_name, f_sig in fs.items():
#         all_vars = merge_dicts([gvars, new_fs])
#         if not var_exists(f_name, all_vars):
#             f, f_src = fgen_lmp(
#                 f_name,
#                 f_sig,
#                 new_fs
#             )

#             # recursively define child_fs in the function body if needed
#             f_def_body = ast.unparse(ast.parse(f_src).body[0].body)
#             child_fs, child_f_srcs = create_new_fs_from_code(
#                 f_def_body, all_vars
#             )

#             if len(child_fs) > 0:
#                 new_fs.update(child_fs)
#                 srcs.update(child_f_srcs)

#                 # redefine parent f so newly created child_fs are in scope
#                 gvars = merge_dicts(
#                     [gvars, new_fs]
#                 )
#                 lvars = {}

#                 exec_safe(f_src, gvars, lvars)

#                 f = lvars[f_name]

#             new_fs[f_name], srcs[f_name] = f, f_src

#     return new_fs, srcs


# class FunctionParser(ast.NodeTransformer):
#     def __init__(self, fs, f_assigns):
#         super().__init__()
#         self._fs = fs
#         self._f_assigns = f_assigns

#     def visit_Call(self, node):
#         self.generic_visit(node)
#         if isinstance(node.func, ast.Name):
#             f_sig = ast.unparse(node).strip()
#             f_name = ast.unparse(node.func).strip()
#             self._fs[f_name] = f_sig
#         return node

#     def visit_Assign(self, node):
#         self.generic_visit(node)
#         if isinstance(node.value, ast.Call):
#             assign_str = ast.unparse(node).strip()
#             f_name = ast.unparse(node.value.func).strip()
#             self._f_assigns[f_name] = assign_str
#         return node


# def merge_dicts(dicts):
#     return {k: v for d in dicts for k, v in d.items()}


# def var_exists(name, all_vars):
#     try:
#         eval(name, all_vars)
#     except:
#         exists = False
#     else:
#         exists = True
#     return exists
