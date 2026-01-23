# File: arifos_code/ast_verifier.py
"""
AST-Based Code Verification

Uses Python's Abstract Syntax Tree module to mathematically prove
that code references (functions, classes, variables) exist in the substrate.

This moves Truth from heuristic to law.
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class ASTCodebaseAnalyzer:
    """
    Analyzes Python codebase using AST to extract all definitions.

    This provides mathematical proof that referenced code elements exist,
    enforcing Truth ≥ 0.99 at the structural level.
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize analyzer with workspace root.

        Args:
            workspace_root: Path to codebase root
        """
        self.workspace_root = workspace_root
        self._codebase_index: Optional[Dict[str, Set[str]]] = None

    def index_codebase(self) -> Dict[str, Set[str]]:
        """
        Build index of all functions, classes, and methods in codebase.

        Returns:
            {
                "functions": {"validate_token", "compute_metrics", ...},
                "classes": {"APEXPrime", "Metrics", ...},
                "methods": {"judge", "compute_truth", ...},
                "variables": {"truth_score", "apex", ...}
            }
        """
        if self._codebase_index is not None:
            return self._codebase_index

        index = {
            "functions": set(),
            "classes": set(),
            "methods": set(),
            "variables": set(),
            "imports": set()
        }

        # Find all Python files
        python_files = list(self.workspace_root.rglob("*.py"))

        for file_path in python_files:
            try:
                self._index_file(file_path, index)
            except SyntaxError as e:
                logger.warning(f"Could not parse {file_path}: {e}")
                continue
            except Exception as e:
                logger.warning(f"Error indexing {file_path}: {e}")
                continue

        self._codebase_index = index
        return index

    def _index_file(self, file_path: Path, index: Dict[str, Set[str]]) -> None:
        """
        Parse single file and extract definitions.

        Args:
            file_path: Path to Python file
            index: Dictionary to populate with definitions
        """
        source = file_path.read_text(encoding="utf-8")

        try:
            tree = ast.parse(source)
        except SyntaxError:
            # File has syntax errors - skip
            return

        for node in ast.walk(tree):
            # Extract function definitions
            if isinstance(node, ast.FunctionDef):
                index["functions"].add(node.name)

            # Extract class definitions
            elif isinstance(node, ast.ClassDef):
                index["classes"].add(node.name)

                # Extract methods within classes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        index["methods"].add(item.name)

            # Extract variable assignments (module-level)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        index["variables"].add(target.id)

            # Extract imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    index["imports"].add(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    index["imports"].add(node.module)

    def verify_code_reference(self, reference: str, reference_type: str = "any") -> bool:
        """
        Verify that a code reference exists in the codebase.

        Args:
            reference: Name of function, class, or method
            reference_type: Type to check ("function", "class", "method", "any")

        Returns:
            True if reference exists, False otherwise

        Examples:
            >>> analyzer.verify_code_reference("validate_token", "function")
            True
            >>> analyzer.verify_code_reference("NonExistentClass", "class")
            False
        """
        index = self.index_codebase()

        if reference_type == "any":
            # Check all categories
            return (
                reference in index["functions"]
                or reference in index["classes"]
                or reference in index["methods"]
                or reference in index["variables"]
            )
        elif reference_type in index:
            return reference in index[reference_type]
        else:
            return False

    def verify_import(self, import_statement: str) -> bool:
        """
        Verify that an import can be resolved.

        Args:
            import_statement: Import line (e.g., "from pathlib import Path")

        Returns:
            True if import is resolvable, False otherwise
        """
        # Extract module name from import statement
        if "from " in import_statement:
            # e.g., "from pathlib import Path" → "pathlib"
            module = import_statement.split("from ")[1].split(" import")[0].strip()
        elif "import " in import_statement:
            # e.g., "import pathlib" → "pathlib"
            module = import_statement.split("import ")[1].split(" as")[0].strip()
        else:
            return False

        # Check if module is in codebase
        index = self.index_codebase()
        if module in index["imports"]:
            return True

        # Check if it's a standard library or installed package
        try:
            __import__(module)
            return True
        except ImportError:
            return False

    def get_function_signature(self, function_name: str) -> Optional[Dict]:
        """
        Get function signature (parameters, return type) if it exists.

        Args:
            function_name: Name of function to look up

        Returns:
            {
                "file": Path,
                "parameters": ["param1", "param2", ...],
                "return_annotation": str or None,
                "docstring": str or None
            }
            or None if function not found
        """
        python_files = list(self.workspace_root.rglob("*.py"))

        for file_path in python_files:
            try:
                source = file_path.read_text(encoding="utf-8")
                tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        # Extract parameters
                        params = [arg.arg for arg in node.args.args]

                        # Extract return annotation
                        return_annotation = None
                        if node.returns:
                            return_annotation = ast.unparse(node.returns)

                        # Extract docstring
                        docstring = ast.get_docstring(node)

                        return {
                            "file": file_path,
                            "parameters": params,
                            "return_annotation": return_annotation,
                            "docstring": docstring
                        }

            except Exception:
                continue

        return None

    def verify_function_call_matches_signature(
        self,
        function_name: str,
        call_args: List[str]
    ) -> bool:
        """
        Verify that a function call matches the function's signature.

        Args:
            function_name: Name of function being called
            call_args: Arguments in the call

        Returns:
            True if call matches signature, False otherwise
        """
        signature = self.get_function_signature(function_name)
        if signature is None:
            return False

        # Simple check: number of arguments
        expected_params = len(signature["parameters"])
        actual_args = len(call_args)

        # Allow for *args, **kwargs (not checking rigorously here)
        return actual_args <= expected_params + 2


class ASTTruthVerifier:
    """
    High-level Truth verifier using AST analysis.

    Wraps ASTCodebaseAnalyzer with convenient methods for
    Truth floor enforcement.
    """

    def __init__(self, workspace_root: Path):
        self.analyzer = ASTCodebaseAnalyzer(workspace_root)

    def compute_truth_score(
        self,
        response: str,
        file_operations: List[Dict]
    ) -> float:
        """
        Compute Truth score using AST-based verification.

        Args:
            response: Claude's response text
            file_operations: List of file operations

        Returns:
            Truth score (0.0 to 1.0)
        """
        truth_score = 1.00

        # Extract code references from response
        code_refs = self._extract_code_references(response)

        # Verify each reference exists
        for ref_name, ref_type in code_refs:
            if not self.analyzer.verify_code_reference(ref_name, ref_type):
                truth_score *= 0.85  # Penalize hallucinated reference
                logger.warning(f"Hallucinated reference: {ref_type} '{ref_name}'")

        # Verify imports in file operations
        for op in file_operations:
            if op.get("type") in ["write", "edit"]:
                new_content = op.get("new_content", "")
                imports = self._extract_imports(new_content)

                for import_stmt in imports:
                    if not self.analyzer.verify_import(import_stmt):
                        truth_score *= 0.90  # Penalize unresolvable import
                        logger.warning(f"Unresolvable import: {import_stmt}")

        return max(0.0, truth_score)

    def _extract_code_references(self, text: str) -> List[tuple]:
        """
        Extract function/class references from natural language text.

        Args:
            text: Natural language response

        Returns:
            List of (name, type) tuples
            e.g., [("validate_token", "function"), ("APEXPrime", "class")]
        """
        import re

        refs = []

        # Pattern: "function <name>"
        function_pattern = r'\bfunction\s+(\w+)'
        for match in re.finditer(function_pattern, text):
            refs.append((match.group(1), "function"))

        # Pattern: "class <name>"
        class_pattern = r'\bclass\s+(\w+)'
        for match in re.finditer(class_pattern, text):
            refs.append((match.group(1), "class"))

        # Pattern: "method <name>"
        method_pattern = r'\bmethod\s+(\w+)'
        for match in re.finditer(method_pattern, text):
            refs.append((match.group(1), "method"))

        # Pattern: "<name>() function call"
        call_pattern = r'\b(\w+)\(\)'
        for match in re.finditer(call_pattern, text):
            refs.append((match.group(1), "any"))

        return refs

    def _extract_imports(self, code: str) -> List[str]:
        """
        Extract import statements from code.

        Args:
            code: Python source code

        Returns:
            List of import statements
        """
        import_lines = [
            line.strip() for line in code.split('\n')
            if line.strip().startswith('import ') or line.strip().startswith('from ')
        ]
        return import_lines
