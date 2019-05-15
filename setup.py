from setuptools import setup

setup(
    name='bujo',
    version='0.2',
    py_modules=['bujo'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        bujo=bujo:cli
    ''',
)