import sys
import os
import unittest.mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
import requests

# Add the project root to the Python path to allow for module imports
sys.path.insert(0, os.getcwd())

from main import MainWindow
from widgets import NodeWidget

def verify_error_state():
    """
    Programmatically verifies that a NodeWidget correctly enters the 'error'
    visual state when its execution fails due to an API error.
    """
    # Patch the api_client functions to avoid actual network calls.
    # get_models is called on MainWindow initialization, and post_completion
    # is called during graph execution.
    with unittest.mock.patch('main.api_client.get_models', return_value={}), \
         unittest.mock.patch('api_client.post_completion') as mock_post_completion:

        # Configure the mock to simulate an API failure
        mock_post_completion.side_effect = requests.exceptions.RequestException("Simulated API Error")

        # Set up the headless PyQt application
        app = QApplication.instance() or QApplication(sys.argv)
        window = MainWindow()

        # Add a node to the scene
        node = window.add_node("Test Error Node")

        # Execute the graph, which should trigger the error
        window.execute_graph()

        # Find the node in the scene
        nodes_in_scene = [item for item in window.scene.items() if isinstance(item, NodeWidget)]
        assert len(nodes_in_scene) == 1, "There should be exactly one node in the scene."
        test_node = nodes_in_scene[0]

        # Assert that the node's border color is red
        error_color = QColor(Qt.GlobalColor.red)
        current_color = test_node.rect_item.pen().color()

        assert current_color == error_color, f"Node color should be {error_color.name()}, but got {current_color.name()}"

        print("Verification successful: Node correctly changes to 'error' state on API failure.")

if __name__ == "__main__":
    verify_error_state()
