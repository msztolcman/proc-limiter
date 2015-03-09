from setuptools import setup
from os import path

BASE_DIR = path.abspath(path.dirname(__file__))

setup(
    name='proc-limiter',
    version='0.3.0',
    description='limit instances of given process to specified quantity',
    long_description='',
    url='http://github.com/mysz/proc-limiter',
    author='Marcin Sztolcman',
    author_email='marcin@urzenia.net',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['argparse'],
    py_modules=['proc_limiter'],

    keywords='limiter processes management',

    entry_points={
        'console_scripts': [
            'proc-limiter=proc_limiter:main',
        ],
    },
)

