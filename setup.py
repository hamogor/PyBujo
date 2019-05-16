from setuptools import setup, find_packages
import bujo

setup(
    name='bujo',
    version='0.2.2',
    description='A CLI tool for tracking anything and everything',
    long_description_content_type = "text/markdown",
    long_description=open('README.md').read(),
    author=bujo.__author__,
    author_email='ferovax@gmail.com',
    py_modules=['bujo'],
    install_requires=[
        'Click',
        'PyFiglet',
        'pyyaml',
        'colorama',
    ],
    entry_points='''
        [console_scripts]
        bujo= bujo.bujo:cli
    ''',
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
    ),
)
