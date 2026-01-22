import sys
import os
import unittest
from unittest.mock import patch
import requests
from PyQt6.QtWidgets import QApplication
from main import MainWindow
from widgets import NODE_COLOR_DEFAULT, NODE_COLOR_ERROR

# Add the repository root to the Python path
sys.path.insert(0, os.getcwd())

# A QApplication instance is required for any PyQt tests
app = QApplication(sys.argv)

class TestVisualStates(unittest.TestCase):

    @patch('main.api_client.get_models', return_value={'data': []})
    def setUp(self, mock_get_models):
        """Set up the test environment before each test."""
        self.window = MainWindow()

    @patch('widgets.api_client.post_completion')
    def test_node_success_state(self, mock_post_completion):
        """Verify that a node's border returns to default after a successful execution."""
        mock_post_completion.return_value = {
            'choices': [{'message': {'content': 'Mocked success response'}}]
        }

        node = self.window.add_node("Success Node")
        self.window.execute_graph()

        pen = node.rect_item.pen()
        self.assertEqual(pen.color(), NODE_COLOR_DEFAULT, "Node border should be default color on success.")

    @patch('widgets.api_client.post_completion')
    def test_node_error_state(self, mock_post_completion):
        """Verify that a node's border turns red on a failed execution."""
        mock_post_completion.side_effect = requests.exceptions.RequestException("Mocked connection error")

        node = self.window.add_node("Error Node")
        self.window.execute_graph()

        pen = node.rect_item.pen()
        self.assertEqual(pen.color(), NODE_COLOR_ERROR, "Node border should be red on error.")

    @patch('widgets.api_client.post_completion')
    def test_node_state_resets_before_execution(self, mock_post_completion):
        """Verify that a node in an error state is reset on the next execution."""
        # First execution fails, putting the node in an error state
        mock_post_completion.side_effect = requests.exceptions.RequestException("Mocked connection error")
        node = self.window.add_node("Reset Test Node")
        self.window.execute_graph()

        # Confirm it's in the error state
        pen_after_error = node.rect_item.pen()
        self.assertEqual(pen_after_error.color(), NODE_COLOR_ERROR, "Node border should be red after initial error.")

        # Second execution succeeds
        mock_post_completion.side_effect = None
        mock_post_completion.return_value = {
            'choices': [{'message': {'content': 'Mocked success response'}}]
        }
        self.window.execute_graph()

        # Confirm it's back in the default state
        pen_after_success = node.rect_item.pen()
        self.assertEqual(pen_after_success.color(), NODE_COLOR_DEFAULT, "Node border should reset to default on subsequent successful run.")

if __name__ == '__main__':
    unittest.main()
