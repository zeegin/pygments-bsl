[![PyPI - Version](https://img.shields.io/pypi/v/pygments-bsl?style=flat-square&logo=pypi&label=pypi%20package&color=green)](https://pypi.org/project/pygments-bsl/)

pygments-bsl
=============

[Pygments](http://pygments.org/) is a syntax highlighting tool.

[Who uses Pygments?](https://pygments.org/faq/#who-uses-pygments)

Online example [Zensical](https://zensical.org/docs/) with `pygments-bsl` support https://zeegin.github.io/pygments-bsl/

`pygments-bsl` used in:
- https://1c-syntax.github.io/bsl-language-server/
- https://pr-mex.github.io/vanessa-automation/

Syntax rules adopted from https://github.com/1c-syntax.

Install
--------

```
$ pip install pygments-bsl
```

Install local
--------
```bash
python -m pip install -e .
```

Build
------

```bash
python -m pip install --upgrade build
python -m build
```

Test
------

```bash
python -m pip install --upgrade pytest
pytest

```

Validate release artifacts
------

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
python tools/check_dist.py
```

Docs
------

```bash
python3.12 -m venv .venv-docs
source .venv-docs/bin/activate
pip install --upgrade pip
pip install -e .
pip install "zensical==0.0.24"
zensical serve
```

Python 3.10+ is required. The command above uses Python 3.12 because that's the tested docs environment. The docs environment is separate from the package's main runtime.

Generate lexer data from JSON (after updating files in `3rd_party/`)
------

```bash
python tools/generate_data.py
```

Usage
-------

```bash
pygmentize "C:\git\pygments-bsl\tests\examplefiles\bsl\samples.bsl"
pygmentize "C:\git\pygments-bsl\tests\examplefiles\bsl\samples.os"
pygmentize "C:\git\pygments-bsl\tests\examplefiles\sdbl\samples.sdbl"
```
