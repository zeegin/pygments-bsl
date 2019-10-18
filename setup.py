from setuptools import setup, find_packages

setup(
    name='pygments-bsl',
    version='0.2',
    packages=find_packages(),
    author='Ingvar Vilkman',
    author_email='zeegin@zeegin.com',
    url='https://github.com/zeegin/pygments-bsl',
    license='MIT License',
    description='Pygments 1C (BSL) lexer',
    classifiers=[
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ],
    install_requires=['pygments'],
    entry_points={
        'pygments.lexers': [
            'bsl=pygments_bsl:BSLLexer'
        ]
    },
    package_data={
        '': ['LICENSE', '*.rst'],
    }
)