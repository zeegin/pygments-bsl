from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pygments-bsl',
    version='0.6.1',
    packages=find_packages(exclude=[".vscode/*", "tests/*"]),
    author='Ingvar Vilkman',
    author_email='zeegin@zeegin.com',
    url='https://github.com/zeegin/pygments-bsl',
    license='MIT License',
    description='Pygments 1C (BSL) lexer',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'pygments >= 2.3'
    ],
    entry_points={
        'pygments.lexers': [
            'bsl=pygments_bsl:BSLLexer'
        ]
    },
    package_data={
        '': ['LICENSE', '*.md'],
    },
    test_suite='tests'
)
