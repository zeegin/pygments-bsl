import os
import sys


def _register_local_lexers():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from pygments.lexers import _mapping, _lexer_cache
    from pygments_bsl.lexer import BslLexer, SdblLexer

    _mapping.LEXERS['BslLexer'] = (
        'pygments_bsl',
        BslLexer.name,
        ('bsl',),
        ('*.bsl', '*.os'),
        ('text/x-bsl',),
    )
    _mapping.LEXERS['SdblLexer'] = (
        'pygments_bsl',
        SdblLexer.name,
        ('sdbl',),
        ('*.sdbl',),
        ('text/x-sdbl',),
    )

    _lexer_cache[BslLexer.name] = BslLexer
    _lexer_cache[SdblLexer.name] = SdblLexer


def on_config(config):
    _register_local_lexers()
    return config
