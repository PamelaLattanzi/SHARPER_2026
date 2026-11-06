"""
Punto di ingresso per la versione WEB (pygbag cerca un file main.py).
Sul computer si puo' continuare a usare: python benthos_game.py
"""
import asyncio

from benthos_game import main

asyncio.run(main())
