[![PyPI - Version](https://img.shields.io/pypi/v/pygments-bsl?style=flat-square&logo=pypi&label=pypi%20package&color=green)](https://pypi.org/project/pygments-bsl/)

pygments-bsl
=============

[Pygments](http://pygments.org/) is a syntax highlighting tool.

[Who uses Pygments?](https://pygments.org/faq/#who-uses-pygments)

Online example [MkDocs](https://www.mkdocs.org) with `pygments-bsl` support https://zeegin.github.io/pygments-bsl/

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
pip install .
```

Build
------

```bash
python -m build
```

Test
------

```bash
pytest

```

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
