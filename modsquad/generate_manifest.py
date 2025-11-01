import json
from pathlib import Path

manifest = {'modsquad_extensions': [], 'backend_routers': [], 'backend_services': [], 'backend_models': [], 'backend_markets': [], 'backend_strategies': [], 'scripts': [], 'frontend_components': []}

modsquad_ext = Path('modsquad/extensions')
if modsquad_ext.exists():
    manifest['modsquad_extensions'] = sorted([f.stem for f in modsquad_ext.glob('*.py') if f.stem not in ['__init__', 'utils']])

backend_routers = Path('backend/app/routers')
if backend_routers.exists():
    manifest['backend_routers'] = sorted([f.stem for f in backend_routers.glob('*.py') if f.stem not in ['__init__']])

backend_services = Path('backend/app/services')
if backend_services.exists():
    for f in backend_services.rglob('*.py'):
        if f.stem not in ['__init__']:
            manifest['backend_services'].append(str(f.relative_to(backend_services)).replace('\', '/').replace('.py', ''))
    manifest['backend_services'] = sorted(manifest['backend_services'])

backend_models = Path('backend/app/models')
if backend_models.exists():
    manifest['backend_models'] = sorted([f.stem for f in backend_models.glob('*.py') if f.stem not in ['__init__']])

backend_markets = Path('backend/app/markets')
if backend_markets.exists():
    for f in backend_markets.rglob('*.py'):
        if f.stem not in ['__init__']:
            manifest['backend_markets'].append(str(f.relative_to(backend_markets)).replace('\', '/').replace('.py', ''))
    manifest['backend_markets'] = sorted(manifest['backend_markets'])

backend_strategies = Path('backend/strategies')
if backend_strategies.exists():
    manifest['backend_strategies'] = sorted([f.stem for f in backend_strategies.glob('*.py') if f.stem not in ['__init__']])

scripts_path = Path('scripts')
if scripts_path.exists():
    for f in scripts_path.rglob('*.py'):
        if f.stem not in ['__init__']:
            manifest['scripts'].append(str(f.relative_to(scripts_path)).replace('\', '/').replace('.py', ''))
    manifest['scripts'] = sorted(manifest['scripts'])

frontend_components = Path('frontend/components')
if frontend_components.exists():
    manifest['frontend_components'] = sorted([f.stem for f in frontend_components.glob('*.tsx') if f.stem not in ['index']])

manifest['_totals'] = {cat: len(items) for cat, items in manifest.items() if not cat.startswith('_')}
manifest['_totals']['total'] = sum(manifest['_totals'].values())

print(json.dumps(manifest, indent=2))
