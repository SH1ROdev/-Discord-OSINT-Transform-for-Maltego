import sys
from extensions import registry

print("[transforms/__init__.py] Loading transforms module", file=sys.stderr)

from .FullDiscordOSINT import FullDiscordOSINT

print("[transforms/__init__.py] Imported FullDiscordOSINT", file=sys.stderr)

if 'discord' not in registry.transform_sets:
    registry.transform_sets['discord'] = []

class_name_lower = FullDiscordOSINT.__name__.lower()
if class_name_lower in registry.transform_metas:
    meta = registry.transform_metas[class_name_lower]
    registry.transform_sets['discord'].append(meta)
    print(f"[transforms/__init__.py] Added {meta.display_name} to discord seed", file=sys.stderr)
else:
    print(f"[transforms/__init__.py] Warning: {class_name_lower} not found in transform_metas", file=sys.stderr)
    print(f"[transforms/__init__.py] Available metas: {list(registry.transform_metas.keys())}", file=sys.stderr)

print(f"[transforms/__init__.py] Now transform_sets: {list(registry.transform_sets.keys())}", file=sys.stderr)

print("[transforms/__init__.py] Done", file=sys.stderr)
