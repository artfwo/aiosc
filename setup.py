#! /usr/bin/env python3

from setuptools import setup

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='aiosc',
    author='Artem Popov',
    author_email='artfwo@gmail.com',
    url='https://github.com/artfwo/aiosc',
    description='Minimalistic Open Sound Control (OSC) communication module using asyncio',
    long_description=long_description,
    version='0.1.5',
    py_modules=['aiosc'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking',
    ],
    license='MIT'
)
