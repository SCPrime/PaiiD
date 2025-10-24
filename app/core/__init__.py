"""Compatibility layer mirroring :mod:`backend.app.core`."""

from importlib import import_module
import pkgutil
import sys

_backend_core = import_module("backend.app.core")

__path__ = _backend_core.__path__  # type: ignore[attr-defined]
__all__: list[str] = []

for _module in pkgutil.iter_modules(_backend_core.__path__, prefix="backend.app.core."):
    module_name = _module.name
    alias = module_name.replace("backend.app.core", "app.core", 1)
    module = import_module(module_name)
    sys.modules[alias] = module
    globals()[module_name.rsplit(".", 1)[-1]] = module
    __all__.append(module_name.rsplit(".", 1)[-1])
