"""Compatibility layer mirroring :mod:`backend.app.routers`."""

from importlib import import_module
import pkgutil
import sys

_backend_routers = import_module("backend.app.routers")

__path__ = _backend_routers.__path__  # type: ignore[attr-defined]
__all__: list[str] = []

for _module in pkgutil.iter_modules(_backend_routers.__path__, prefix="backend.app.routers."):
    module_name = _module.name
    alias = module_name.replace("backend.app.routers", "app.routers", 1)
    module = import_module(module_name)
    sys.modules[alias] = module
    globals()[module_name.rsplit(".", 1)[-1]] = module
    __all__.append(module_name.rsplit(".", 1)[-1])
