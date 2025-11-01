"""Interface Predictor - Anticipates function signatures at intersection points.

Part of ARMANI Squad for strategic integration. Uses AST analysis to predict
function signatures, type contracts, and call patterns at intersection points,
enabling proactive glue code generation before target batch completes.
"""

from __future__ import annotations

import ast
import re
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "interface_predictor"

__all__ = ["predict"]


def predict(
    intersection: dict[str, Any], batch_output: dict[str, Any]
) -> dict[str, Any]:
    """
    Predict interface at intersection point by analyzing batch output.

    Analysis includes:
    1. Function signatures (name, parameters, return type)
    2. Class definitions and methods
    3. Type hints and contracts
    4. Import dependencies
    5. Call patterns

    Args:
        intersection: Intersection point from intersection_mapper
        batch_output: Output from completed source batch

    Returns:
        Predicted interface with signatures, types, and patterns
    """
    config = load_extension_config()
    settings = config.get("interface_predictor", {})

    if not settings.get("enabled", False):
        return {
            "status": "disabled",
            "reason": "Interface predictor not enabled",
            "intersection": intersection,
        }

    intersection_type = intersection.get("type")
    location = intersection.get("location")

    # Extract created modules from batch output
    created_modules = _extract_created_modules(batch_output)

    predicted_interface = {
        "intersection": intersection,
        "intersection_type": intersection_type,
        "location": location,
        "predicted_functions": [],
        "predicted_classes": [],
        "predicted_imports": [],
        "predicted_function_calls": [],
        "type_hints": {},
        "confidence": "high",
    }

    # Analyze each created module for interface elements
    for module_path, module_info in created_modules.items():
        # Parse module content with AST
        try:
            tree = ast.parse(module_info.get("content", ""))

            # Extract function definitions
            functions = _extract_functions(tree, module_path)
            predicted_interface["predicted_functions"].extend(functions)

            # Extract class definitions
            classes = _extract_classes(tree, module_path)
            predicted_interface["predicted_classes"].extend(classes)

            # Extract imports
            imports = _extract_imports(tree, module_path)
            predicted_interface["predicted_imports"].extend(imports)

            # Extract type hints
            type_hints = _extract_type_hints(tree, module_path)
            predicted_interface["type_hints"].update(type_hints)

        except SyntaxError:
            # Fallback to regex-based extraction
            predicted_interface["confidence"] = "medium"
            functions = _extract_functions_regex(module_info.get("content", ""))
            predicted_interface["predicted_functions"].extend(functions)

    # Predict call patterns based on intersection type
    if intersection_type == "function_handoff":
        call_patterns = _predict_handoff_calls(
            intersection, predicted_interface["predicted_functions"]
        )
        predicted_interface["predicted_function_calls"].extend(call_patterns)

    elif intersection_type == "import_chain":
        import_patterns = _predict_import_patterns(
            intersection, predicted_interface["predicted_functions"]
        )
        predicted_interface["predicted_imports"].extend(import_patterns)

    # Persist predictions
    dump_jsonl(
        ARTIFACT_DIR / "interface_predictions.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "intersection_type": intersection_type,
            "location": location,
            "predicted_functions": len(predicted_interface["predicted_functions"]),
            "predicted_classes": len(predicted_interface["predicted_classes"]),
            "confidence": predicted_interface["confidence"],
        },
    )

    return predicted_interface


def _extract_created_modules(batch_output: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Extract created Python modules from batch output.

    Args:
        batch_output: Output from completed batch

    Returns:
        Dictionary mapping module paths to module info
    """
    created_modules = {}

    # Extract from 'created_files' field
    created_files = batch_output.get("created_files", [])
    for file_info in created_files:
        file_path = file_info.get("path", "")
        if file_path.endswith(".py"):
            created_modules[file_path] = {
                "content": file_info.get("content", ""),
                "type": "created",
            }

    # Extract from 'modified_files' field
    modified_files = batch_output.get("modified_files", [])
    for file_path in modified_files:
        if file_path.endswith(".py") and file_path not in created_modules:
            # Try to read file content
            try:
                path = Path(file_path)
                if path.exists():
                    with path.open("r", encoding="utf-8") as f:
                        content = f.read()
                    created_modules[file_path] = {"content": content, "type": "modified"}
            except Exception:
                pass

    return created_modules


def _extract_functions(tree: ast.AST, module_path: str) -> list[dict[str, Any]]:
    """
    Extract function definitions from AST.

    Args:
        tree: Parsed AST
        module_path: Path to module

    Returns:
        List of function signature dictionaries
    """
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            signature = _extract_function_signature(node)
            signature["module"] = module_path
            functions.append(signature)

    return functions


def _extract_function_signature(node: ast.FunctionDef) -> dict[str, Any]:
    """
    Extract function signature from FunctionDef node.

    Args:
        node: AST FunctionDef node

    Returns:
        Function signature dictionary
    """
    # Extract parameters
    parameters = []
    for arg in node.args.args:
        param = {"name": arg.arg, "annotation": None}

        # Extract type annotation
        if arg.annotation:
            param["annotation"] = ast.unparse(arg.annotation)

        parameters.append(param)

    # Extract return type
    return_type = None
    if node.returns:
        return_type = ast.unparse(node.returns)

    # Extract decorators
    decorators = [ast.unparse(dec) for dec in node.decorator_list]

    # Extract docstring
    docstring = ast.get_docstring(node)

    return {
        "name": node.name,
        "parameters": parameters,
        "return_type": return_type,
        "decorators": decorators,
        "docstring": docstring,
        "is_async": isinstance(node, ast.AsyncFunctionDef),
    }


def _extract_classes(tree: ast.AST, module_path: str) -> list[dict[str, Any]]:
    """
    Extract class definitions from AST.

    Args:
        tree: Parsed AST
        module_path: Path to module

    Returns:
        List of class definition dictionaries
    """
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "module": module_path,
                "bases": [ast.unparse(base) for base in node.bases],
                "methods": [],
                "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                "docstring": ast.get_docstring(node),
            }

            # Extract methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method = _extract_function_signature(item)
                    class_info["methods"].append(method)

            classes.append(class_info)

    return classes


def _extract_imports(tree: ast.AST, module_path: str) -> list[dict[str, Any]]:
    """
    Extract import statements from AST.

    Args:
        tree: Parsed AST
        module_path: Path to module

    Returns:
        List of import dictionaries
    """
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(
                    {
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                        "source_module": module_path,
                    }
                )

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(
                    {
                        "type": "from_import",
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "source_module": module_path,
                    }
                )

    return imports


def _extract_type_hints(tree: ast.AST, module_path: str) -> dict[str, str]:
    """
    Extract type hints from AST.

    Args:
        tree: Parsed AST
        module_path: Path to module

    Returns:
        Dictionary mapping variable names to type hints
    """
    type_hints = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            # Variable with type annotation
            if isinstance(node.target, ast.Name):
                var_name = node.target.id
                type_hint = ast.unparse(node.annotation)
                type_hints[f"{module_path}::{var_name}"] = type_hint

    return type_hints


def _extract_functions_regex(content: str) -> list[dict[str, Any]]:
    """
    Fallback: Extract function signatures using regex.

    Args:
        content: Module content as string

    Returns:
        List of function signature dictionaries
    """
    functions = []

    # Pattern: def function_name(param1: type1, param2: type2) -> return_type:
    pattern = r"def\s+(\w+)\s*\((.*?)\)\s*(?:->\s*([^:]+))?\s*:"

    for match in re.finditer(pattern, content, re.MULTILINE):
        func_name = match.group(1)
        params_str = match.group(2)
        return_type = match.group(3).strip() if match.group(3) else None

        # Parse parameters
        parameters = []
        if params_str:
            for param in params_str.split(","):
                param = param.strip()
                if ":" in param:
                    name, annotation = param.split(":", 1)
                    parameters.append(
                        {"name": name.strip(), "annotation": annotation.strip()}
                    )
                else:
                    parameters.append({"name": param, "annotation": None})

        functions.append(
            {
                "name": func_name,
                "parameters": parameters,
                "return_type": return_type,
                "decorators": [],
                "docstring": None,
                "is_async": False,
            }
        )

    return functions


def _predict_handoff_calls(
    intersection: dict[str, Any], predicted_functions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Predict function call patterns for handoff intersections.

    Args:
        intersection: Handoff intersection
        predicted_functions: Predicted function signatures

    Returns:
        List of predicted call patterns
    """
    call_patterns = []

    target_batch = intersection.get("target_batch")

    for func in predicted_functions:
        call_patterns.append(
            {
                "function": func["name"],
                "module": func.get("module", "unknown"),
                "parameters": func["parameters"],
                "expected_caller": target_batch,
                "call_context": "handoff_integration",
            }
        )

    return call_patterns


def _predict_import_patterns(
    intersection: dict[str, Any], predicted_functions: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Predict import patterns for import chain intersections.

    Args:
        intersection: Import chain intersection
        predicted_functions: Predicted function signatures

    Returns:
        List of predicted import patterns
    """
    import_patterns = []

    source_module = intersection.get("location", "")
    target_batch = intersection.get("target_batch")

    # Predict imports of functions from source module
    for func in predicted_functions:
        if func.get("module") == source_module:
            import_patterns.append(
                {
                    "type": "from_import",
                    "module": source_module,
                    "name": func["name"],
                    "expected_importer": target_batch,
                    "import_context": "import_chain_integration",
                }
            )

    return import_patterns


def cli() -> None:
    """CLI entry point for interface predictor."""
    print("Interface Predictor - ARMANI Squad")
    print("Run via elite_weaver.run() for full interface prediction")
