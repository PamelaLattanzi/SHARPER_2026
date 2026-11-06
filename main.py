"""
Punto di ingresso per la versione WEB (pygbag cerca un file main.py).
Sul computer si puo' continuare a usare: python benthos_game.py

NB: pygbag decide quali librerie scaricare guardando gli "import" di
QUESTO file: "import pygame" qui sotto e' necessario, non toglierlo.
"""
import asyncio

import pygame  # noqa: F401  (serve a pygbag per caricare pygame nel browser)

from benthos_game import main

asyncio.run(main())
