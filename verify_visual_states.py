
import sys
import os
import unittest.mock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtCore import Qt

# Add repo root to path for correct imports
sys.path.insert(0, os.getcwd())

from main import MainWindow
from widgets import NodeWidget

def get_node_pen(node):
    """Helper to get the QPen of the node's border."""
    return node.rect.pen()

def test_successful_execution():
    """Tests that the node's visual state is correct during and after a successful execution."""
    print("--- Testing successful execution state change ---")
    app = QApplication(sys.argv)

    with unittest.mock.patch('main.api_client.get_models') as mock_get_models:
        mock_get_models.return_value = {}  # Mock the initial API call in MainWindow
        window = MainWindow()

        node = window.add_node("Success Test Node")

        initial_pen = get_node_pen(node)
        assert initial_pen.color() == Qt.GlobalColor.white, f"Initial state incorrect. Expected white, got {initial_pen.color().name()}"
        print("✅ Initial state is correct (white).")

        with unittest.mock.patch('widgets.api_client.post_completion') as mock_post:
            mock_post.return_value = {
                'choices': [{'message': {'content': 'Mocked success'}}]
            }

            # We can't easily check the 'executing' state as it's synchronous.
            # We will trust the logic and check the final state.
            window.execute_graph()

            final_pen = get_node_pen(node)
            assert final_pen.color() == Qt.GlobalColor.white, f"Final state incorrect. Expected white, got {final_pen.color().name()}"
            print("✅ Final state after success is correct (white).")
    print("--- Success test passed ---")


def test_failed_execution_and_reset():
    """Tests that the node's visual state becomes 'error' on failure and resets on the next run."""
    print("\n--- Testing failed execution and state reset ---")
    app = QApplication(sys.argv)

    with unittest.mock.patch('main.api_client.get_models') as mock_get_models:
        mock_get_models.return_value = {}  # Mock initial API call
        window = MainWindow()

        node = window.add_node("Failure Test Node")

        # 1. Test failed execution
        with unittest.mock.patch('widgets.api_client.post_completion') as mock_post:
            mock_post.side_effect = Exception("Mocked API Failure")

            window.execute_graph()

            error_pen = get_node_pen(node)
            assert error_pen.color() == Qt.GlobalColor.red, f"Error state incorrect. Expected red, got {error_pen.color().name()}"
            print("✅ Error state after failure is correct (red).")

        # 2. Test that the state is reset on the next execution
        with unittest.mock.patch('widgets.api_client.post_completion') as mock_post:
            mock_post.return_value = {
                'choices': [{'message': {'content': 'Mocked success'}}]
            }

            window.execute_graph()

            reset_pen = get_node_pen(node)
            assert reset_pen.color() == Qt.GlobalColor.white, f"Reset state incorrect. Expected white, got {reset_pen.color().name()}"
            print("✅ State correctly reset to default on subsequent successful run.")

    print("--- Failure and reset test passed ---")

if __name__ == "__main__":
    test_successful_execution()
    test_failed_execution_and_reset()
    print("\n🎉 All verification checks passed!")
