import uuid
import logging
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem, QVBoxLayout, QLineEdit, QApplication
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QBrush, QPen, QPainterPath
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
    NODE_WIDTH = 150
    NODE_HEIGHT = 100

    def __init__(self, name="LLM Box", node_id=None):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.name = name
        self.node_id = node_id or str(uuid.uuid4())
        self.inputs = []
        self.output = None
        self.is_executing = False

        # Add ports
        self.input_port = Port(self)
        self.input_port.setPos(0, self.NODE_HEIGHT / 2)

        self.output_port = Port(self, is_output=True)
        self.output_port.setPos(self.NODE_WIDTH, self.NODE_HEIGHT / 2)

    def to_dict(self):
        return {
            'id': self.node_id,
            'name': self.name,
            'pos': [self.pos().x(), self.pos().y()]
        }

    def execute(self):
        self.is_executing = True
        self.update()
        QApplication.processEvents()

        try:
            prompt = " ".join(map(str, self.inputs))
            logging.info(f"Executing node {self.node_id} with prompt: {prompt}")
            completion = api_client.post_completion(prompt)
            if completion:
                self.output = completion.get('choices', [{}])[0].get('message', {}).get('content', '')
                logging.info(f"Node {self.node_id} produced output: {self.output}")
            else:
                self.output = ""
        finally:
            self.is_executing = False
            self.update()

        return self.output


    def boundingRect(self):
        return QRectF(0, 0, self.NODE_WIDTH, self.NODE_HEIGHT)

    def paint(self, painter, option, widget):
        # Draw the main box
        brush = QBrush(Qt.GlobalColor.yellow) if self.is_executing else QBrush(Qt.GlobalColor.darkGray)
        painter.setBrush(brush)
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawRect(0, 0, self.NODE_WIDTH, self.NODE_HEIGHT)

        # Draw the title
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(5, 15, self.name)

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
