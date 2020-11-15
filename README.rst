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

Compynent is a micro library for dependency injection and managing state in an application.


* Free software: MIT license
* Documentation: https://compynent.readthedocs.io.


Install
-------

Recommended install is using pip:

.. code-block:: console

    $ pip install compynent


Quick start
-----------

"Components" in your application are just context managers. All of them receive their dependencies in their init, and they will be initialized by the time the context is "entered".

For example, let's define two components `A`, and `B`, and `A` depends on `B`.

.. code-block:: python

   from contextlib import contextmanager
   @contextmanager
   def component_a(b):
       print('entered A')
       yield b
       print('exiting A')
   @contextmanager
   def component_b():
       print('entered B')
       yield 35
       print('exiting B')


Now, let's define our system config and use it inside a context:

.. code-block:: python

   from compynent import System
   system = System({'a': (component_a, ['b']),
                    'b': (component_b, [])})
   with system.start() as ctx:
       print('A: %d' % ctx['a'])
       print('B: %d' % ctx['b'])

When we run the code block above, we get::

   entered B
   entered A
   A: 35
   B: 35
   exiting A
   exiting B


But why?
--------

Dependency Injection is a good idea for many reasons. I suggest reading about it and learning for yourself (trust me, it's worth it).

Now, why not use one of the many dependency injection libraries out there? My second suggestion is to start a Python REPL and run ``import this`` (or read about the `zen of python`_). This library is focused on the second and third lines:

- Explicit is better than implicit
- Simple is better than complex

All the libraries fall short in one or two of these rules. Some will depend on incantations to automatically find where to inject code, while others provide a complex API for defining all sorts of dependencies, bindings, providers, containers, etc. This library doesn't do that.  It provides a way to define that component A depends on component B and **that's it**. Everything else is up to the user. No singletons, factories, etc., for the sole reason that it's not needed in Python.

Another reason is state management. One important feature of dependency injection is being able to share state between different parts of your code while maintaining the parts decoupled. This means the dependency graph is important to define the order in which the application parts must be initialized. But, if you want an application that is actually easily testable, you also want the cleanup to be done properly in the reverse order of initialization. Most libraries out there assume your program will run forever or that you will handle releasing resources manually after it's done. Well, Python solves that pretty well already with `context managers`_, so why not take advantage of that?

Dependency Injection Libraries
------------------------------

Python community came up with other great libraries. If this one is not for you, make sure to check the others out:

- http://python-dependency-injector.ets-labs.org/
- https://github.com/google/pinject
- https://github.com/ivankorobkov/python-inject

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

It was inspired by the Component_ library for Clojure, written by `Stuart Sierra`_. I hope this project carries some of that simplicity with it.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _Component: https://github.com/stuartsierra/component
.. _`Stuart Sierra`: https://stuartsierra.com/
.. _`context managers`: https://docs.python.org/3/library/stdtypes.html#typecontextmanager
.. _`zen of python`: https://www.python.org/dev/peps/pep-0020/
