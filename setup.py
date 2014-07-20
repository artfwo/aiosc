#! /usr/bin/env python3
from setuptools import setup

setup(
    name='aiosc',
    author='Artem Popov',
    author_email='artfwo@gmail.com',
    url='https://github.com/artfwo/aiosc',
    description='Minimalistic OSC communication module using asyncio.',
    version='0.1',
    py_modules=['aiosc'],
    include_package_data=True,
    license='MIT',
)
