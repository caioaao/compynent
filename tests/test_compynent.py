#!/usr/bin/env python

"""Tests for `compynent` package."""

from contextlib import AbstractContextManager, contextmanager

from compynent import System


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
    sys = System(sys_config())
    assert sys.order == ['init_counter', 'cfg', 'counter', 'app']
    pass


def test_system_map():
    sys = System(sys_config())
    # assert top level
    with sys.start() as ctx:
        assert isinstance(ctx['app'], App)
        assert isinstance(ctx['cfg'], Config)
        assert isinstance(ctx['counter'], Counter)

        # assert dependencies
        assert ctx['app']._config is ctx['cfg']
        assert ctx['app']._counter is ctx['counter']
        assert ctx['counter']._config is ctx['cfg']


def test_initialization_order():
    with System(sys_config()).start() as ctx:
        pass

    assert ctx['cfg']._when == 1
    assert ctx['counter']._when == 2
    assert ctx['app']._when == 3


def test_context_management():
    with System(sys_config()).start() as ctx:
        assert ctx['app'].get_counter() == 1
        ctx['app'].incr_counter()
        assert ctx['app'].get_counter() == 11
    assert ctx['app'].get_counter() is None


def test_using_generators():
    @contextmanager
    def make_counter():
        counter = [0]
        try:
            yield counter
        finally:
            counter[0] -= 1

    @contextmanager
    def make_outer(counter):
        yield counter[0] + 1

    system = System({'cnt': (make_counter, []),
                     'outer': (make_outer, {'cnt': 'counter'})})
    with system.start() as ctx:
        assert ctx['cnt'] == [0]
        ctx['cnt'][0] = 123
    assert ctx['cnt'] == [122]
