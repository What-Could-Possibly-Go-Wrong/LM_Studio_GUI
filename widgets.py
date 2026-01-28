import uuid
import logging
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem, QVBoxLayout, QLineEdit
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QBrush, QPen, QPainterPath, QColor
import api_client

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
        self.rect.setBrush(QBrush(Qt.GlobalColor.darkGray))
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

    def execute(self):
        self.set_visual_state("executing")
        # For now, we'll just join the inputs
        prompt = " ".join(self.inputs)
        logging.info(f"Executing node {self.node_id} with prompt: {prompt}")
        completion = api_client.post_completion(prompt)
        if completion:
            # A simple way to get the content, this might need to be adjusted
            # based on the actual response structure from LM Studio
            self.output = completion.get('choices', [{}])[0].get('message', {}).get('content', '')
            logging.info(f"Node {self.node_id} produced output: {self.output}")
            self.set_visual_state("default")
        else:
            self.output = "" # Or handle the error appropriately
            self.set_visual_state("error")
        return self.output

    def set_visual_state(self, state):
        if state == "executing":
            self.rect.setPen(QPen(QColor("blue"), 2))
        elif state == "error":
            self.rect.setPen(QPen(QColor("red"), 2))
        else: # "default"
            self.rect.setPen(QPen(Qt.GlobalColor.white))
        self.update()

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
