#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

# with open('README.rst') as readme_file:
#     readme = readme_file.read()
#
# with open('./HISTORY.rst') as history_file:
#     history = history_file.read()

with open('./requirements.txt') as requirements_file:
    requirements = requirements_file.read()

setup_requirements = []

test_requirements = []

setup(
    author="Laurent Copey",
    author_email='laurent.copey@gmail.com',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    entry_points={
        'console_scripts': [
            '_template=_template.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    # long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='docstring_format',
    name='docstring_format',
    # packages=find_packages(include=['_template', '_template.*']),
    packages=find_packages(),
    # package_data={'': ['qss/*']},
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lcopey/docstring_format',
    version='0.9.0',
    zip_safe=False,
)
