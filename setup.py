from setuptools import setup

with open('README.md') as fp:
    long_description = fp.read()

setup(
    name='asyncpipe',
    version='0.0.1',
    author='Jacob Beck',
    author_email='pypi@jacob.ebeck.io',
    description='An async-compatible library for composing Python shell pipelines',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/beckjake/asyncpipe',
    py_modules=['asyncpipe'],
    classifiers=[
        # TODO: test 3.5/3.7, set up tox or whatever
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
    ],
)