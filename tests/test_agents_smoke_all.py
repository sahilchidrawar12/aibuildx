import importlib, pkgutil, inspect
from pathlib import Path
from src.pipeline import agents as agents_pkg


def test_all_agents_process_no_crash():
    pkg_path = Path(agents_pkg.__file__).parent
    failures = []
    successes = []
    for finder, name, ispkg in pkgutil.iter_modules([str(pkg_path)]):
        if name.startswith('_'):
            continue
        module_name = f'src.pipeline.agents.{name}'
        try:
            mod = importlib.import_module(module_name)
            proc = None
            # try common names
            for attr in ('process', 'process_payload', 'run'):
                if hasattr(mod, attr) and inspect.isfunction(getattr(mod, attr)):
                    proc = getattr(mod, attr)
                    break
            if proc is None:
                # try classes with run
                for _, obj in inspect.getmembers(mod, inspect.isclass):
                    if hasattr(obj, 'run'):
                        inst = obj()
                        proc = getattr(inst, 'run')
                        break
            if proc is None:
                failures.append((name, 'no callable found'))
                continue
            res = proc({})
            if not isinstance(res, dict) or 'status' not in res:
                failures.append((name, 'bad result'))
            else:
                successes.append(name)
        except Exception as e:
            failures.append((name, str(e)))
    assert not failures, f'Agent failures: {failures}'
