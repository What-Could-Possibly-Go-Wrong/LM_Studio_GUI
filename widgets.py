import uuid
import logging
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem, QVBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QPen, QPainterPath, QColor
import api_client

# Define some constants for colors
NODE_COLOR_DEFAULT = QColor("#3c3c3c")  # A dark grey
NODE_COLOR_PROCESSING = QColor("#5a5a9b") # A purplish blue

class Port(QGraphicsItem):
    def __init__(self, parent, is_output=False):
        super().__init__(parent)
        self.is_output = is_output
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.rect = QGraphicsRectItem(-5, -5, 10, 10, self)
        self.rect.setBrush(QBrush(Qt.GlobalColor.cyan))

    def boundingRect(self):
        return self.rect.boundingRect()

    def paint(self, painter, option, widget):
        pass # The child rect will paint itself

class NodeWidget(QGraphicsItem):
    def __init__(self, name="LLM Box", node_id=None):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.name = name
        self.node_id = node_id or str(uuid.uuid4())
        self.inputs = []
        self.output = None

        # Create the main box
        self.rect = QGraphicsRectItem(0, 0, 150, 100, self)
        self.rect.setBrush(QBrush(NODE_COLOR_DEFAULT))
        self.rect.setPen(QPen(Qt.GlobalColor.white))

        # Create the title
        self.title = QGraphicsTextItem(self.name, self)
        self.title.setDefaultTextColor(Qt.GlobalColor.white)
        self.title.setPos(5, 5)

        # Add ports
        self.input_port = Port(self)
        self.input_port.setPos(0, 50)

        self.output_port = Port(self, is_output=True)
        self.output_port.setPos(150, 50)

    def to_dict(self):
        return {
            'id': self.node_id,
            'name': self.name,
            'pos': [self.pos().x(), self.pos().y()]
        }

    def set_processing(self, is_processing):
        """Changes the color of the node to indicate processing."""
        if is_processing:
            self.rect.setBrush(QBrush(NODE_COLOR_PROCESSING))
        else:
            self.rect.setBrush(QBrush(NODE_COLOR_DEFAULT))
        self.update()

    def execute(self):
        try:
            # For now, we'll just join the inputs
            prompt = " ".join(map(str, self.inputs)) # Ensure all inputs are strings
            logging.info(f"Executing node {self.node_id} with prompt: {prompt}")
            completion = api_client.post_completion(prompt)
            if completion and 'choices' in completion and completion['choices']:
                message = completion['choices'][0].get('message', {})
                self.output = message.get('content', '')
                logging.info(f"Node {self.node_id} produced output: {self.output}")
            else:
                self.output = "Error or empty response"
                logging.warning(f"Node {self.node_id} received an empty or invalid response.")
        except Exception as e:
            self.output = f"Error: {e}"
            logging.error(f"Node {self.node_id} failed to execute: {e}")
        return self.output


    def boundingRect(self):
        return self.rect.boundingRect()

    def paint(self, painter, option, widget):
        pass

class Connection(QGraphicsPathItem):
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.update_path()

    def to_dict(self):
        start_node = self.start_port.parentItem()
        end_node = self.end_port.parentItem()
        return {
            'from_node': start_node.node_id,
            'to_node': end_node.node_id,
        }

    def update_path(self):
        path = QPainterPath()
        start_pos = self.start_port.scenePos()
        end_pos = self.end_port.scenePos()
        path.moveTo(start_pos)
        path.lineTo(end_pos)
        self.setPath(path)
