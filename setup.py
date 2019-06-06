from setuptools import setup, find_packages
import bujo

setup(
    name='bujo',
    version='1.0.5',
    description='A CLI tool for tracking anything and everything',
    keywords="cli note diary journal note-taking bullet_journal",
    long_description=open('README.rst').read(),
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
        'Programming Language :: Python :: 3.4',
    ),
)
