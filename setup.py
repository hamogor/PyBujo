from setuptools import setup, find_packages
from os import path
import bujo

root_dir = path.abspath(path.dirname(__file__))
with open(path.join(root_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bujo',
    version='1.0.2',
    description='A CLI tool for tracking anything and everything',
    keywords="cli note diary journal note-taking bullet_journal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=bujo.__author__,
    author_email='ferovax@gmail.com',
    url='https://github.com/oref/PyBujo.git',
    install_requires=[
        'Click',
        'pyyaml',
        'pick',
    ],
    packages=['bujo'],
    entry_points={
        'console_scripts': ['bujo = bujo:cli'],
    },
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
    ),
)
