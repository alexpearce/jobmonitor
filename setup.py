#!/usr/bin/env python

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='jobmonitor',
    version='0.0.5',
    description='Physics-orientated job monitoring over HTTP with Flask.',
    author='Alex Pearce',
    author_email='alex@alexpearce.me',
    url='https://github.com/alexpearce/jobmonitor',
    license=read('LICENSE'),
    long_description=read('README.rst'),
    packages=['jobmonitor'],
    include_package_data=True,
    install_requires=[
        'Flask>=0.10.1',
        'rq>=0.4.6',
        'redis==2.10.1'
    ],
    test_suite='tests',
    tests_require=['unittest2', 'mock', 'fakeredis'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: MIT License'
    ]
)
