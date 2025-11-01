"""Glue Code Generator - Creates handoff code at predetermined intersection points.

Part of ARMANI Squad for strategic integration. Generates integration code snippets,
import statements, validation commands, and type conversions needed to connect
parallel batch outputs into a cohesive codebase.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .utils import CONFIG_PATH, dump_jsonl, load_extension_config

ARTIFACT_DIR = CONFIG_PATH.parent.parent / "logs" / "run-history" / "glue_code_generator"

__all__ = ["generate", "GlueCode"]


@dataclass
class GlueCode:
    """Generated glue code for an intersection point."""

    code_snippet: str
    target_location: str
    validation_command: str
    imports: list[str]
    integration_pattern: str
    insertion_strategy: str
    metadata: dict[str, Any]


def generate(
    intersection: dict[str, Any], predicted_interface: dict[str, Any]
) -> GlueCode:
    """
    Generate glue code for an intersection point.

    Supported integration patterns:
    1. handoff_function: Create wrapper function to call batch A from batch B
    2. import_prediction: Generate import statements for batch B
    3. adapter_pattern: Create adapter for incompatible interfaces
    4. type_converter: Generate type conversion utilities

    Args:
        intersection: Intersection point from intersection_mapper
        predicted_interface: Predicted interface from interface_predictor

    Returns:
        GlueCode object with code snippet and metadata
    """
    config = load_extension_config()
    settings = config.get("glue_code_generator", {})

    if not settings.get("enabled", False):
        return GlueCode(
            code_snippet="",
            target_location="",
            validation_command="",
            imports=[],
            integration_pattern="disabled",
            insertion_strategy="none",
            metadata={"status": "disabled"},
        )

    integration_pattern = intersection.get("integration_pattern", "handoff_function")

    # Route to appropriate generator based on pattern
    if integration_pattern == "handoff_function":
        glue_code = _generate_handoff_function(intersection, predicted_interface)

    elif integration_pattern == "import_prediction":
        glue_code = _generate_import_statements(intersection, predicted_interface)

    elif integration_pattern == "adapter_pattern":
        glue_code = _generate_adapter_pattern(intersection, predicted_interface)

    elif integration_pattern == "type_converter":
        glue_code = _generate_type_converter(intersection, predicted_interface)

    else:
        # Default: simple import statement
        glue_code = _generate_simple_import(intersection, predicted_interface)

    # Persist generated glue code
    dump_jsonl(
        ARTIFACT_DIR / "glue_code.jsonl",
        {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "intersection_type": intersection.get("type"),
            "integration_pattern": integration_pattern,
            "target_location": glue_code.target_location,
            "code_length": len(glue_code.code_snippet),
        },
    )

    return glue_code


def _generate_handoff_function(
    intersection: dict[str, Any], predicted_interface: dict[str, Any]
) -> GlueCode:
    """
    Generate handoff function that calls source batch functions from target batch.

    Args:
        intersection: Intersection point
        predicted_interface: Predicted interface

    Returns:
        GlueCode with handoff function
    """
    source_batch = intersection.get("source_batch", "source")
    target_batch = intersection.get("target_batch", "target")

    predicted_functions = predicted_interface.get("predicted_functions", [])

    if not predicted_functions:
        return _generate_empty_glue_code(intersection, "No functions to handoff")

    # Generate wrapper function for each predicted function
    code_snippets = []
    imports = []

    for func in predicted_functions:
        func_name = func.get("name", "unknown_function")
        module = func.get("module", "")
        parameters = func.get("parameters", [])
        return_type = func.get("return_type", "Any")

        # Generate import statement
        if module:
            module_name = Path(module).stem
            imports.append(f"from {module_name} import {func_name}")

        # Generate parameter list
        param_list = []
        param_names = []
        for param in parameters:
            param_name = param.get("name", "arg")
            param_annotation = param.get("annotation")

            if param_annotation:
                param_list.append(f"{param_name}: {param_annotation}")
            else:
                param_list.append(param_name)

            param_names.append(param_name)

        param_str = ", ".join(param_list)
        call_param_str = ", ".join(param_names)

        # Generate wrapper function
        wrapper_code = f'''
def {func_name}_integration({param_str}) -> {return_type}:
    """
    Integration wrapper for {func_name} from {source_batch}.

    This function provides a handoff point between {source_batch} and {target_batch}.
    """
    return {func_name}({call_param_str})
'''

        code_snippets.append(textwrap.dedent(wrapper_code))

    code_snippet = "\n\n".join(code_snippets)

    # Generate validation command
    validation_command = f"python -m pytest tests/integration/test_{target_batch}.py"

    return GlueCode(
        code_snippet=code_snippet,
        target_location=intersection.get("location", "integration.py"),
        validation_command=validation_command,
        imports=imports,
        integration_pattern="handoff_function",
        insertion_strategy="append_to_module",
        metadata={
            "source_batch": source_batch,
            "target_batch": target_batch,
            "function_count": len(predicted_functions),
        },
    )


def _generate_import_statements(
    intersection: dict[str, Any], predicted_interface: dict[str, Any]
) -> GlueCode:
    """
    Generate import statements for import chain intersections.

    Args:
        intersection: Intersection point
        predicted_interface: Predicted interface

    Returns:
        GlueCode with import statements
    """
    source_module = intersection.get("location", "")
    predicted_imports = predicted_interface.get("predicted_imports", [])
    predicted_functions = predicted_interface.get("predicted_functions", [])

    if not source_module:
        return _generate_empty_glue_code(intersection, "No source module specified")

    imports = []

    # Generate imports from predicted imports
    for import_info in predicted_imports:
        if import_info.get("type") == "from_import":
            module = import_info.get("module", "")
            name = import_info.get("name", "")
            alias = import_info.get("alias")

            if alias:
                imports.append(f"from {module} import {name} as {alias}")
            else:
                imports.append(f"from {module} import {name}")

        elif import_info.get("type") == "import":
            module = import_info.get("module", "")
            alias = import_info.get("alias")

            if alias:
                imports.append(f"import {module} as {alias}")
            else:
                imports.append(f"import {module}")

    # Generate imports for predicted functions
    module_name = Path(source_module).stem if source_module else "module"
    for func in predicted_functions:
        func_name = func.get("name", "")
        if func_name:
            imports.append(f"from {module_name} import {func_name}")

    code_snippet = "\n".join(sorted(set(imports)))

    return GlueCode(
        code_snippet=code_snippet,
        target_location=intersection.get("location", ""),
        validation_command="python -m py_compile " + intersection.get("location", ""),
        imports=imports,
        integration_pattern="import_prediction",
        insertion_strategy="prepend_to_module",
        metadata={
            "import_count": len(imports),
            "source_module": source_module,
        },
    )


def _generate_adapter_pattern(
    intersection: dict[str, Any], predicted_interface: dict[str, Any]
) -> GlueCode:
    """
    Generate adapter pattern for incompatible interfaces.

    Args:
        intersection: Intersection point
        predicted_interface: Predicted interface

    Returns:
        GlueCode with adapter class
    """
    source_batch = intersection.get("source_batch", "source")
    target_batch = intersection.get("target_batch", "target")

    predicted_functions = predicted_interface.get("predicted_functions", [])

    if not predicted_functions:
        return _generate_empty_glue_code(intersection, "No functions for adapter")

    # Generate adapter class
    adapter_code = f'''
class {source_batch.title()}To{target_batch.title()}Adapter:
    """
    Adapter to make {source_batch} interface compatible with {target_batch}.

    This adapter wraps {source_batch} functions to match the expected interface
    of {target_batch}, handling parameter transformations and return type conversions.
    """

    def __init__(self):
        """Initialize the adapter."""
        self._initialized = True
'''

    # Generate adapter methods
    for func in predicted_functions:
        func_name = func.get("name", "unknown_function")
        parameters = func.get("parameters", [])
        return_type = func.get("return_type", "Any")

        param_str = ", ".join(
            f"{p.get('name', 'arg')}: {p.get('annotation', 'Any')}"
            for p in parameters
        )

        adapter_code += f'''

    def {func_name}(self, {param_str}) -> {return_type}:
        """Adapter method for {func_name}."""
        # TODO: Implement parameter transformation
        # TODO: Call original {func_name}
        # TODO: Implement return value conversion
        raise NotImplementedError("Adapter method not implemented")
'''

    imports = ["from typing import Any"]

    return GlueCode(
        code_snippet=textwrap.dedent(adapter_code),
        target_location=f"adapters/{source_batch}_to_{target_batch}_adapter.py",
        validation_command=f"python -m pytest tests/adapters/test_{source_batch}_adapter.py",
        imports=imports,
        integration_pattern="adapter_pattern",
        insertion_strategy="create_new_file",
        metadata={
            "source_batch": source_batch,
            "target_batch": target_batch,
            "adapter_methods": len(predicted_functions),
        },
    )


def _generate_type_converter(
    intersection: dict[str, Any], predicted_interface: dict[str, Any]
) -> GlueCode:
    """
    Generate type conversion utilities for incompatible types.

    Args:
        intersection: Intersection point
        predicted_interface: Predicted interface

    Returns:
        GlueCode with type converter functions
    """
    type_hints = predicted_interface.get("type_hints", {})

    if not type_hints:
        return _generate_empty_glue_code(intersection, "No type hints for conversion")

    # Generate converter functions
    converter_code = '''
from typing import Any, TypeVar, cast

T = TypeVar('T')


def convert_type(value: Any, target_type: type[T]) -> T:
    """
    Convert value to target type with validation.

    Args:
        value: Value to convert
        target_type: Target type

    Returns:
        Converted value

    Raises:
        TypeError: If conversion is not possible
    """
    try:
        return cast(T, target_type(value))
    except (TypeError, ValueError) as e:
        raise TypeError(f"Cannot convert {type(value)} to {target_type}: {e}")


def safe_convert(value: Any, target_type: type[T], default: T) -> T:
    """
    Safely convert value with fallback to default.

    Args:
        value: Value to convert
        target_type: Target type
        default: Default value if conversion fails

    Returns:
        Converted value or default
    """
    try:
        return convert_type(value, target_type)
    except TypeError:
        return default
'''

    return GlueCode(
        code_snippet=textwrap.dedent(converter_code),
        target_location="utils/type_converters.py",
        validation_command="python -m pytest tests/utils/test_type_converters.py",
        imports=["from typing import Any, TypeVar, cast"],
        integration_pattern="type_converter",
        insertion_strategy="create_new_file",
        metadata={
            "type_hint_count": len(type_hints),
        },
    )


def _generate_simple_import(
    intersection: dict[str, Any], predicted_interface: dict[str, Any]
) -> GlueCode:
    """
    Generate simple import statement as fallback.

    Args:
        intersection: Intersection point
        predicted_interface: Predicted interface

    Returns:
        GlueCode with simple import
    """
    location = intersection.get("location", "")

    if not location:
        return _generate_empty_glue_code(intersection, "No location specified")

    module_name = Path(location).stem if location else "module"
    code_snippet = f"import {module_name}"

    return GlueCode(
        code_snippet=code_snippet,
        target_location=intersection.get("location", ""),
        validation_command=f"python -c 'import {module_name}'",
        imports=[code_snippet],
        integration_pattern="simple_import",
        insertion_strategy="prepend_to_module",
        metadata={"module": module_name},
    )


def _generate_empty_glue_code(intersection: dict[str, Any], reason: str) -> GlueCode:
    """
    Generate empty glue code when generation is not possible.

    Args:
        intersection: Intersection point
        reason: Reason for empty code

    Returns:
        Empty GlueCode object
    """
    return GlueCode(
        code_snippet="# No glue code generated: " + reason,
        target_location="",
        validation_command="",
        imports=[],
        integration_pattern="none",
        insertion_strategy="none",
        metadata={"status": "empty", "reason": reason},
    )


def _extract_imports(intersection: dict[str, Any]) -> list[str]:
    """
    Extract required imports from intersection metadata.

    Args:
        intersection: Intersection point

    Returns:
        List of import statements
    """
    imports = []

    # Extract from location
    location = intersection.get("location", "")
    if location and location.endswith(".py"):
        module_name = Path(location).stem
        imports.append(f"import {module_name}")

    return imports


def cli() -> None:
    """CLI entry point for glue code generator."""
    print("Glue Code Generator - ARMANI Squad")
    print("Run via elite_weaver.run() for full glue code generation")
