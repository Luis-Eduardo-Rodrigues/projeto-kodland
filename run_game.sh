#!/usr/bin/env sh

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$SCRIPT_DIR" || exit 1

# O SDL le esta opcao antes de o Pygame Zero criar a janela.
export SDL_VIDEO_CENTERED=1

exec pgzrun main.py
