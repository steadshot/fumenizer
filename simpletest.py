#!/usr/bin/env python

import functools

import unittest
import json

import fumenizer

class TestBuildMatrix(unittest.TestCase):
	def compareImageToFile(self, imageFile, dataFile):
		matrix = fumenizer.buildMatrix(imageFile, 20, 0)
		with open(dataFile, 'r') as f:
			expectedMatrix = json.load(f)

		self.assertEqual(self.compareMatrices(matrix, expectedMatrix), 0)

	def compareMatrices(self, matrix, expected):
		zipped = zip(matrix, expected)
		for row in zipped:
		    count = functools.reduce(lambda x, y: x != y, row)
		return count

	def test_empty(self):
		self.compareImageToFile('tetris1.png', 'test/tetris1.json')

	def test_tetris2(self):
		self.compareImageToFile('tetris2.png', 'test/tetris2.json')

	def test_tetris3(self):
		self.compareImageToFile('tetris3.png', 'test/tetris3.json')

if __name__ == '__main__':
    unittest.main()
