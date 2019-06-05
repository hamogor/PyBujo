from setuptools import setup, find_packages
import bujo

setup(
    name='bujo',
    version='1.0',
    description='A CLI tool for tracking anything and everything',
    author=bujo.__author__,
    author_email='ferovax@gmail.com',
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
