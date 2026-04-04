import ast
from dataclasses import dataclass, field
from .languages import get_parser_for_file

@dataclass
class ChangeReport:
    file_path: str
    added_functions: list[str] = field(default_factory=list)
    removed_functions: list[str] = field(default_factory=list)
    signature_changes: list[str] = field(default_factory=list)
    is_breaking: bool = False

def analyze_changes(file_path, old_content, new_content):
    """Analyze AST changes between two versions of a Python file."""
    report = ChangeReport(file_path=file_path)
    
    if not file_path.endswith(".py"):
        # For non-python, we might just do a basic diff analysis later
        return report

    try:
        old_tree = ast.parse(old_content)
        new_tree = ast.parse(new_content)
        
        def get_funcs(tree):
            return {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        
        old_funcs = get_funcs(old_tree)
        new_funcs = get_funcs(new_tree)
        
        # Added / Removed
        report.added_functions = [name for name in new_funcs if name not in old_funcs]
        report.removed_functions = [name for name in old_funcs if name not in new_funcs]
        
        if report.removed_functions:
            report.is_breaking = True
            
        # Signature changes
        for name, new_node in new_funcs.items():
            if name in old_funcs:
                old_node = old_funcs[name]
                # Compare arguments (simplified)
                old_args = [arg.arg for arg in old_node.args.args]
                new_args = [arg.arg for arg in new_node.args.args]
                if old_args != new_args:
                    report.signature_changes.append(f"Function '{name}': {old_args} -> {new_args}")
                    report.is_breaking = True
                    
    except Exception:
        pass
        
    return report
