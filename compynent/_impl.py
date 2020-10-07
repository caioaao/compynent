from contextlib import ExitStack, contextmanager


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


class System:
    def __init__(self, components):
        self.components = {
            name: {'dependencies': list(deps.keys()) if isinstance(deps, dict) else list(deps),
                   'aliases': deps if isinstance(deps, dict) else {v: v for v in deps},
                   'constructor': constructor}
            for name, (constructor, deps) in components.items()}
        _ensure_completenes(self.components)
        self.order = _toposort(self.components)

    @contextmanager
    def start(self):
        system_map = {}
        with ExitStack() as stack:
            for component_name in self.order:
                config = self.components[component_name]
                component_context = config['constructor'](
                    **{dep_alias: system_map[dep_name]
                       for dep_name, dep_alias in config['aliases'].items()})
                system_map[component_name] = stack.enter_context(component_context)
            yield system_map
