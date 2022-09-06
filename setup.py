from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='qbot',
    version='1.0',
    packages=find_packages(),
    install_requires=open('requirements.txt').read().splitlines(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
)
