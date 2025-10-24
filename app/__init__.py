"""Compatibility package that re-exports :mod:`backend.app` as :mod:`app`."""

from importlib import import_module
import pkgutil
import sys

_backend_app = import_module("backend.app")

# Share the backend package path so standard import mechanics continue to work.
__path__ = _backend_app.__path__  # type: ignore[attr-defined]

# Mirror the backend package attributes for convenience.
for _name, _value in vars(_backend_app).items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _value

# Expose submodules under the ``app`` namespace so ``import app.main`` works.
for _module in pkgutil.walk_packages(_backend_app.__path__, prefix="backend.app."):
    module_name = _module.name
    alias = module_name.replace("backend.app", "app", 1)
    if alias in sys.modules:
        continue
    sys.modules[alias] = import_module(module_name)

__all__ = [name for name in globals() if not name.startswith("__")]
