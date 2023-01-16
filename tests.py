import unittest
from internal.content import Pack
from internal.memory import Game, Memory
from loguru import logger as log

mem = Memory()
log.level("DEBUG")

class TestStringMethods(unittest.TestCase):
    pack1 = Pack("test1", 1, "test", "test.txt", True)
    pack2 = Pack("test2", 1, "test", "test.txt", True)
    game = Game(mem.packs[0])
    log.debug(game.pack.title)
    game.update_pack([pack1, pack2, mem.packs[0]])
    log.debug(game.pack.title)
    game.update_pack([pack1, pack2, mem.packs[0]])
    log.debug(game.pack.title)

if __name__ == '__main__':
    unittest.main()