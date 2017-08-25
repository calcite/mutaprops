#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'aiohttp==1.0.2',
    'async-timeout==1.0.0',
    'chardet==2.3.0',
    'docutils==0.13.1',
    'multidict==2.1.2',
    'sockjs==0.5.0',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='mutaprops',
    version='0.5.6',
    description="Simple UI, autogenerated from your classes.",
    long_description=readme + '\n\n' + history,
    author="Josef Nevrly",
    author_email='jnevrly@alps.cz',
    url='http://10.54.13.215/gitlab/alcz_connectivity/mutaprops',
    # url='https://github.com/JNevrly/mutaprops',
    packages=[
        'mutaprops',
    ],
    package_dir={'mutaprops':
                 'mutaprops'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='mutaprops',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        # 'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
