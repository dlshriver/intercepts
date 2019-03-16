.. intercepts documentation master file, created by
   sphinx-quickstart on Fri Mar 15 21:18:44 2019.

Intercepts
==========

Release v\ |version|. (:ref:`Installation <install>`)

.. image:: https://img.shields.io/github/license/dlshriver/intercepts.svg
    :target: https://github.com/dlshriver/intercepts/blob/master/LICENSE

.. image:: https://img.shields.io/pypi/v/intercepts.svg
    :target: https://pypi.org/project/intercepts/

.. image:: https://travis-ci.org/dlshriver/intercepts.svg?branch=master
    :target: https://travis-ci.org/dlshriver/intercepts


**Intercepts** allows you to intercept any function call in Python
and handle it in any manner you choose.

    >>> def print_handler(print_func, message):
    ...     return print_func(''.join(reversed(message)))
    >>> print("Hello world")
    Hello world
    >>> intercepts.register(print, print_handler)
    >>> print("Hello world")
    dlrow olleH


User Guide
==========

.. toctree::
   :maxdepth: 2

   user/install
   user/quickstart

API Documentation
=================

.. toctree::
   :maxdepth: 2

   api

