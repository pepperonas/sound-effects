"""
Generator modules for sound-effects.

Each module in this package defines:

    CATEGORY    : str   — folder name the sounds are sorted into
    DESCRIPTION : str   — one-line summary of the category
    SOUNDS      : list of (name, description, fn) tuples
                          where fn() -> list[float] sample buffer

`discover()` returns all generator modules in a stable, sorted order.
"""
import importlib
import pkgutil


def discover():
    mods = []
    for info in pkgutil.iter_modules(__path__):
        if info.name.startswith("_"):
            continue
        mod = importlib.import_module(f"{__name__}.{info.name}")
        if hasattr(mod, "CATEGORY") and hasattr(mod, "SOUNDS"):
            mods.append(mod)
    mods.sort(key=lambda m: m.CATEGORY)
    return mods
