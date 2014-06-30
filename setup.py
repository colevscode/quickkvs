import os
from distutils.core import setup

root = os.path.dirname(os.path.realpath(__file__))

setup(
    name='quickkvs',
    version='0.1.0',
    author='Cole Krumbholz',
    author_email='cole@brace.io',
    description='Python simple key value store with in-memory, MongoDB and Redis backends.',
    packages=['quickkvs'],
    install_requires=open(root+"/requirements.txt").read().splitlines(),
    long_description=open(root+"/README.md").read(),
    license='LICENSE',
)