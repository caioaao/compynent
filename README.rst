=========
compynent
=========


.. image:: https://img.shields.io/pypi/v/compynent.svg
        :target: https://pypi.python.org/pypi/compynent

.. image:: https://img.shields.io/travis/caioaao/compynent.svg
        :target: https://travis-ci.com/caioaao/compynent

.. image:: https://readthedocs.org/projects/compynent/badge/?version=latest
        :target: https://compynent.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


An easy way to define a dependency graph between parts of your application and manage their life-cycle using the built-in context managers.

Compynent is a micro library for managing state in an application.


* Free software: MIT license
* Documentation: https://compynent.readthedocs.io.


Install
-------

Recommended install is using pip:

.. code-block:: console

    $ pip install compynent


Usage
-----

The first step is to learn about `context managers`_. Go ahead, I'll wait.

Now that you know what is the basis for this library, everything else is trivial. "Components" in your application are just context managers. All of them receive their dependencies in their init, and they will be initialized by the time the context is "entered".

For an example, let's define two components `A`, and `B`, and `A` depends on `B`.


>>> from contextlib import contextmanager
>>> @contextmanager
... def component_a(b):
...    print('entered A')
...    yield b
...    print('exiting A')
>>> @contextmanager
... def component_b():
...     print('entered B')
...     yield 35
...     print('exiting B')


Now, let's define our system config:

>>> from compynent import build_system
>>> system = build_system({'a': (component_a, ['b']),
...                        'b': (component_b, [])})


When we run the code block above, we get::

 entered B
 entered A

Now, to actually run our system, we do:

>>> from compynent import system_context
>>> with system_context(*system) as ctx:  # `build_system' actually returns a tuple with the system and the calculated execution order
...     print(ctx['a'])
...     print(ctx['b'])

Now we get the output::

 35
 35
 exiting A
 exiting B

But why?
--------

Dependency Injection is a good idea for many reasons. I suggest reading about it and learning for yourself (trust me, it's worth it).

Now, why not use one of the many dependency injection libraries out there?

Let's start with two opinionated guidelines for good code:

1. Explicit is better than implicit
2. Less is more and simplicity is key

All the libraries fall short in one or two of these rules. Some will depend on incantations to automatically find where to inject code, while others provide a complex API for defining all sorts of dependencies, bindings, providers, containers, etc. This library doesn't do that.  It provides a way to define that component A depends on component B and **that's it**. Everything else is up to the user. No singletons, factories, etc. I'm sorry, but we don't need that in Python.

Another reason is state management. One important feature of dependency injection is being able to share state between different parts of your code while maintaining the parts decoupled. This means the dependency graph is important to define the order in which the application parts must be initialized. But, if you want an application that is actually easily testable, you also want the cleanup to be done properly in the reverse order of initialization. Most libraries out there assume your program will run forever or that you will handle releasing resources manually after it's done. Well, Python solves that pretty well already with context managers, so why not take advantage of that?

Dependency Injection Libraries
------------------------------

Python community came up with other great libraries. If this one is not for you, make sure to check the others out:

- http://python-dependency-injector.ets-labs.org/
- https://github.com/google/pinject
- https://github.com/ivankorobkov/python-inject

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

It was completely inspired by the Component_ library for Clojure, written by `Stuart Sierra`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Component: https://github.com/stuartsierra/component
.. _`Stuart Sierra`: https://stuartsierra.com/
.. _`context managers`: https://docs.python.org/3/library/stdtypes.html#typecontextmanager
