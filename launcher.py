"""Inicia o PgZero sem criar a janela temporaria de 100 x 100 pixels."""

import pgzero.builtins
import pgzero.loaders
import pgzero.runner
from pgzero.game import PGZeroGame


def prepare_game(module):
    """Prepara os recursos sem abrir uma janela antes de ler WIDTH e HEIGHT."""
    pgzero.loaders.set_root(module.__file__)
    PGZeroGame.show_default_icon()
    module.__dict__.update(pgzero.builtins.__dict__)


pgzero.runner.prepare_mod = prepare_game
pgzero.runner.main()
