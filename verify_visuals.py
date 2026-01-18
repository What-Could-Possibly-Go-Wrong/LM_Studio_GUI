import sys
import os
import unittest
from unittest.mock import patch, Mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor

# Add the root directory to the Python path
sys.path.append(os.getcwd())

from main import MainWindow
from widgets import NODE_COLOR_SUCCESS, NODE_COLOR_FAILURE, NODE_COLOR_DEFAULT
import requests

class TestNodeVisuals(unittest.TestCase):
    app = None

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)

    def setUp(self):
        # Mock api_client.get_models to avoid network calls during init
        self.get_models_patch = patch('api_client.get_models')
        self.get_models_mock = self.get_models_patch.start()
        self.get_models_mock.return_value = {"models": []}

        self.window = MainWindow()

    def tearDown(self):
        self.get_models_patch.stop()
        self.window.close()

    @patch('api_client.post_completion')
    def test_node_success_color(self, mock_post_completion):
        """Test that a node turns green on successful execution."""
        mock_post_completion.return_value = {
            'choices': [{'message': {'content': 'Success!'}}]
        }

        node = self.window.add_node()
        self.window.execute_graph()

        # Allow the UI to process events
        self.app.processEvents()

        self.assertEqual(node.rect_item.brush().color(), NODE_COLOR_SUCCESS)
        print("Test passed: Node turns green on success.")

    @patch('api_client.post_completion')
    def test_node_failure_color(self, mock_post_completion):
        """Test that a node turns red on failed execution."""
        mock_post_completion.side_effect = requests.exceptions.RequestException("API Error")

        node = self.window.add_node()
        self.window.execute_graph()

        self.app.processEvents()

        self.assertEqual(node.rect_item.brush().color(), NODE_COLOR_FAILURE)
        print("Test passed: Node turns red on failure.")

    @patch('api_client.post_completion')
    def test_node_color_reset(self, mock_post_completion):
        """Test that a node's color is reset on a subsequent run."""
        # First run: Failure
        mock_post_completion.side_effect = requests.exceptions.RequestException("API Error")
        node = self.window.add_node()
        self.window.execute_graph()
        self.app.processEvents()
        self.assertEqual(node.rect_item.brush().color(), NODE_COLOR_FAILURE)
        print("Verified node is red after failure.")

        # Second run: Success
        mock_post_completion.side_effect = None
        mock_post_completion.return_value = {
            'choices': [{'message': {'content': 'Success!'}}]
        }
        self.window.execute_graph()
        self.app.processEvents()
        self.assertEqual(node.rect_item.brush().color(), NODE_COLOR_SUCCESS)
        print("Test passed: Node color resets and turns green on subsequent success.")


if __name__ == '__main__':
    # Using a QTimer to run the tests and then exit, ensuring the event loop runs
    # This is a workaround for running PyQt tests in a script
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNodeVisuals))

    # We can't use unittest.main() directly as it blocks
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    # Exit with a status code indicating success or failure
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)
