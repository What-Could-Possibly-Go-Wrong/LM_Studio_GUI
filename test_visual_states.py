
import sys
import os
import unittest
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPen

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from widgets import NodeWidget

class TestNodeWidgetVisualStates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @patch('api_client.get_models', return_value=[])
    def test_visual_states(self, mock_get_models):
        # Create a NodeWidget instance
        node = NodeWidget()

        # Test "executing" state
        node.set_visual_state("executing")
        self.assertEqual(node.rect.pen().color(), QColor("blue"))
        self.assertEqual(node.rect.pen().width(), 2)

        # Test "error" state
        node.set_visual_state("error")
        self.assertEqual(node.rect.pen().color(), QColor("red"))
        self.assertEqual(node.rect.pen().width(), 2)

        # Test "default" state
        node.set_visual_state("default")
        self.assertEqual(node.rect.pen().color(), QColor("white"))

if __name__ == '__main__':
    unittest.main()
