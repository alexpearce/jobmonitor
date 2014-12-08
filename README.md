# Job monitoring

A [Flask](http://flask.pocoo.org/) web application to monitor [rq](http://python-rq.org/) jobs, with a preference for monitoring histograms using [d3.plotable](https://github.com/alexpearce/histograms).

This base package allows you to quickly get a robust submit-poll loop up on running on the client side, with the server handling job submission and results retrieval.

See [`example-monitoring-app`](https://github.com/alexpearce/example-monitoring-app) for an example application that uses `jobmonitor` to display [histograms](http://en.wikipedia.org/wiki/Histogram) from a [ROOT](http://root.cern.ch/) file, including example deployment scripts in a [Vagrant](https://www.vagrantup.com/) virtual machine.

## Installing

[Pip](https://pip.pypa.io/en/latest/) is the recommend way of installing the `jobmonitor` module.
As the latest release is available on [PyPI](https://pypi.python.org/pypi/jobmonitor), installing it is simple.

```bash
$ pip install jobmonitor
```

The latest development version, the [head of the master branch](https://github.com/alexpearce/jobmonitor/tree/master), can be installed instead, if desired.

```bash
$ pip install "git+https://github.com/alexpearce/jobmonitor.git#egg=jobmonitor"
```

Either option will automatically install the monitor's dependencies.

## Running

The job monitor doesn't do much user-facing stuff by itself, instead it is expected that you will want to [create a 'child' application](https://github.com/alexpearce/example-monitoring-app) that uses `jobmonitor`.
You can run the application if you like though, once it is [installed](#installing), by creating and running a script to start Flask's development server.

```python
import jobmonitor
app = jobmonitor.create_app()
app.run(debug=True)
```

The [rq workers](http://python-rq.org/docs/workers/) can be started with a separate script. An [example `start_worker.py` script](https://github.com/alexpearce/jobmonitor/blob/master/webmonitor/start_worker.py) is included.
A [Redis database](http://redis.io/) is expected to be running when the workers start.

## Testing

[Tox](http://tox.readthedocs.org/en/latest/) is recommended to run the test suite for the `jobmonitor` module.

```bash
$ git clone https://github.com/alexpearce/jobmonitor.git
$ cd jobmonitor
$ pip install tox
$ tox
```

This will run the test suite under the Python environments defined in the [`tox.ini`](https://github.com/alexpearce/jobmonitor/blob/master/tox.ini) file.

[![Build status](https://travis-ci.org/alexpearce/jobmonitor.svg?branch=modularise)](http://travis-ci.org/alexpearce/jobmonitor)
