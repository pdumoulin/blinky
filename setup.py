#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Blinky',
    version='2.0',
    description='wemo switch control',
    author='Paul Dumoulin',
    author_email='paul.l.dumoulin@gmail.com',
    url='https://github.com/pdumoulin/blinky',
    install_requires=[
        'requests==2.12.4'
    ]
)
