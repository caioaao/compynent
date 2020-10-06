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


if "pytest" in sys.modules:
    class InitCounter(AbstractContextManager):
        def __init__(self):
            self.cnt = -1

        def incr(self):
            self.cnt += 1
            return self.cnt

        def __enter__(self):
            self.cnt = 0
            return self

        def __exit__(self, *args):
            self.cnt = -1

    class Config(AbstractContextManager):
        def __init__(self, init_counter):
            self._counter = init_counter

        def __enter__(self):
            self.bar = 1
            self.incr = 10
            self._when = self._counter.incr()
            return self

        def __exit__(self, *args):
            self.bar = None
            self.incr = None

    class Counter(AbstractContextManager):
        def __init__(self, counter, config: Config):
            self._config = config
            self._counter = counter

        def increment(self):
            self.counter += self._config.incr

        def __enter__(self):
            self.counter = self._config.bar
            self._when = self._counter.incr()
            return self

        def __exit__(self, *args):
            self.counter = None

    class App(AbstractContextManager):
        def __init__(self, cfg: Config, counter: Counter, init_counter):
            self._config = cfg
            self._counter = counter
            self._init_counter = init_counter

        def get_counter(self):
            return self._counter.counter

        def incr_counter(self):
            return self._counter.increment()

        def __enter__(self):
            self._when = self._init_counter.incr()
            return self

        def __exit__(self, *args):
            pass

    def sys_config():
        return {'app': (App, ['counter', 'cfg', 'init_counter']),
                'init_counter': (InitCounter, []),
                'cfg': (Config, ['init_counter']),
                'counter': (Counter, {'cfg': 'config',
                                      'init_counter': 'counter'})}

    def test_dag():
        _, order = build_system(sys_config())
        assert order == ['init_counter', 'cfg', 'counter', 'app']
        pass

    def test_system_map():
        sys_map, _ = build_system(sys_config())
        # assert top level
        assert isinstance(sys_map['app'], App)
        assert isinstance(sys_map['cfg'], Config)
        assert isinstance(sys_map['counter'], Counter)

        # assert dependencies
        assert sys_map['app']._config is sys_map['cfg']
        assert sys_map['app']._counter is sys_map['counter']
        assert sys_map['counter']._config is sys_map['cfg']

    def test_initialization_order():
        sys_map, order = build_system(
            sys_config())

        with system_context(sys_map, order) as ctx:
            pass
        assert sys_map['cfg']._when == 1
        assert sys_map['counter']._when == 2
        assert sys_map['app']._when == 3

    def test_context_management():
        sys_map, order = build_system(
            sys_config())

        with system_context(sys_map, order) as ctx:
            assert ctx['app'].get_counter() == 1
            ctx['app'].incr_counter()
            assert ctx['app'].get_counter() == 11
        assert ctx['app'].get_counter() is None
