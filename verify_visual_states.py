import sys
import os
import unittest
from unittest.mock import patch, Mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtCore import Qt

# Ensure the app modules can be imported
sys.path.insert(0, os.getcwd())

from widgets import NodeWidget

class TestNodeWidgetVisualStates(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # A QApplication instance is required to create and use widgets
        cls.app = QApplication.instance() or QApplication(sys.argv)

    @patch('widgets.api_client.post_completion')
    def test_execute_success_state(self, mock_post_completion):
        """Test that the node's visual state is set to default on successful execution."""
        # Arrange: Mock a successful API response
        mock_post_completion.return_value = {
            'choices': [{'message': {'content': 'Successful response'}}]
        }
        node = NodeWidget()

        # Act
        node.execute()

        # Assert: The border color should be white (default)
        self.assertEqual(node.rect.pen().color(), QColor(Qt.GlobalColor.white))

    @patch('widgets.api_client.post_completion')
    def test_execute_failure_state(self, mock_post_completion):
        """Test that the node's visual state is set to error on failed execution."""
        # Arrange: Mock a failed API response
        mock_post_completion.return_value = None
        node = NodeWidget()

        # Act
        node.execute()

        # Assert: The border color should be red (error)
        self.assertEqual(node.rect.pen().color(), QColor(Qt.GlobalColor.red))

if __name__ == '__main__':
    unittest.main()
