[![PyPI - Version](https://img.shields.io/pypi/v/pygments-bsl?style=flat-square&logo=pypi&label=pypi%20package&color=green)](https://pypi.org/project/pygments-bsl/)

# Как собрать эту страницу?

```bash
python3.12 -m venv .venv-docs
source .venv-docs/bin/activate
pip install --upgrade pip
pip install -e .
pip install "zensical==0.0.24"
zensical serve
```

Подойдет любой Python 3.10+, но команда выше зафиксирована на Python 3.12 как на проверенной версии. Установка `pip install -e .` нужна, чтобы `zensical` видел локальный `pygments_bsl` и подсветку `bsl` / `sdbl` без публикации пакета.
