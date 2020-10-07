import sys

from contextlib import AbstractContextManager, ExitStack, contextmanager


def _ensure_completenes(components):
    for component, cfg in components.items():
        for dep in cfg['dependencies']:
            if dep not in components:
                msg = f'Dependency {dep} needed for component {component} not found'
                raise RuntimeError(msg)


def _toposort(components):
    leafs = [name for name, cfg
             in components.items()
             if len(cfg['dependencies']) == 0]

    remaining = [(name, cfg['dependencies']) for name, cfg
                 in components.items()
                 if len(cfg['dependencies']) > 0]
    sorted_components = []

    while len(leafs) > 0:
        cur_leaf = leafs.pop()

        remaining = [(name, [dep for dep in deps if dep != cur_leaf])
                     for name, deps in remaining]
        new_leafs = [name for name, deps in remaining if len(deps) == 0]
        remaining = [(name, deps) for name, deps in remaining if len(deps) > 0]
        leafs.extend(new_leafs)
        sorted_components.append(cur_leaf)
    return sorted_components


def _build_system_map(components, order):
    system_map = {}
    for component_name in order:
        config = components[component_name]
        system_map[component_name] = config['constructor'](
            **{dep_alias: system_map[dep_name]
               for dep_name, dep_alias in config['aliases'].items()})
    return system_map


def build_system(components):
    components = {
        name: {'dependencies': list(deps.keys()) if isinstance(deps, dict) else list(deps),
               'aliases': deps if isinstance(deps, dict) else {v: v for v in deps},
               'constructor': constructor}
        for name, (constructor, deps) in components.items()}
    _ensure_completenes(components)
    order = _toposort(components)
    return _build_system_map(components, order), order


@contextmanager
def system_context(system_map, order):
    initialized_map = {}
    with ExitStack() as stack:
        for name in order:
            initialized_map[name] = stack.enter_context(system_map[name])
        yield initialized_map
