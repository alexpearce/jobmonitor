Job monitoring
==============

A `Flask`_ web application to monitor `rq`_ jobs, with a preference for
monitoring histograms using |d3.plotable|_.

This base package allows you to quickly get a robust submit-poll loop up
on running on the client side, with the server handling job submission
and results retrieval.

See |example-monitoring-app|_ for an example application that uses
``jobmonitor`` to display `histograms`_ from a `ROOT`_ file, including
example deployment scripts in a `Vagrant`_ virtual machine.

Installing
----------

`Pip`_ is the recommend way of installing the ``jobmonitor`` module. As
the latest release is available on `PyPI`_, installing it is simple.

.. code:: bash

    $ pip install jobmonitor

The latest development version, the `head of the master branch`_, can be
installed instead, if desired.

.. code:: bash

    $ pip install "git+https://github.com/alexpearce/jobmonitor.git#egg=jobmonitor"

Either option will automatically install the monitor’s dependencies.

Running
-------

The job monitor doesn’t do much user-facing stuff by itself, instead it
is expected that you will want to `create a ‘child’ application`_ that
uses ``jobmonitor``. You can run the application if you like though,
once it is `installed`_, by creating and running a script to start
Flask’s development server.

.. code:: python

    import jobmonitor
    app = jobmonitor.create_app()
    app.run(debug=True)

The `rq workers`_ can be started with a separate script. An `example`_ is included. A `Redis database`_ is
expected to be running when the workers start.

Testing
-------

|Build status|

`Tox`_ is recommended to run the test suite for the ``jobmonitor``
module.

.. code:: bash

    $ git clone https://github.com/alexpearce/jobmonitor.git
    $ cd jobmonitor
    $ pip install tox
    $ tox

This will run the test suite under the Python environments defined in
the |tox.ini|_ file.

.. _Flask: http://flask.pocoo.org/
.. _rq: http://python-rq.org/
.. |d3.plotable| replace:: ``d3.plotable``
.. _d3.plotable: https://github.com/alexpearce/histograms
.. |example-monitoring-app| replace:: ``example-monitoring-app``
.. _example-monitoring-app: https://github.com/alexpearce/example-monitoring-app
.. _histograms: http://en.wikipedia.org/wiki/Histogram
.. _ROOT: http://root.cern.ch/
.. _Vagrant: https://www.vagrantup.com/
.. _Pip: https://pip.pypa.io/en/latest/
.. _PyPI: https://pypi.python.org/pypi/jobmonitor
.. _head of the master branch: https://github.com/alexpearce/jobmonitor/tree/master
.. _create a ‘child’ application: https://github.com/alexpearce/example-monitoring-app
.. _installed: #installing
.. _rq workers: http://python-rq.org/docs/workers/
.. _example: https://github.com/alexpearce/jobmonitor/blob/master/webmonitor/start_worker.py
.. _Redis database: http://redis.io/
.. _Tox: http://tox.readthedocs.org/en/latest/
.. |tox.ini| replace:: ``tox.ini``
.. _tox.ini: https://github.com/alexpearce/jobmonitor/blob/master/tox.ini

.. |Build status| image:: https://travis-ci.org/alexpearce/jobmonitor.svg?branch=modularise
   :target: http://travis-ci.org/alexpearce/jobmonitor
