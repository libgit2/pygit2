import unittest

import utils

class TestLeak(utils.RepoTestCase):
    def test_index_iter(self):
        index = self.repo.index
        while True:
            list(index)

    def test_index_getitem(self):
        index = self.repo.index
        while True:
            index[0]

if __name__ == '__main__':
    unittest.main()
