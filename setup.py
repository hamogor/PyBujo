from setuptools import setup, find_packages

setup(
    name='bujo',
    version='1.0.8',
    description='A CLI tool for tracking anything and everything',
    keywords="cli note diary journal note-taking bullet_journal",
    long_description=open('README.rst').read(),
    long_description_content_type="text/markdown",
    author="Oref",
    author_email='orefdev@gmail.com',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ),
)
