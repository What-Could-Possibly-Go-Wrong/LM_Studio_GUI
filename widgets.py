import uuid
import logging
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem
from PyQt6.QtCore import QPointF
from PyQt6.QtGui import QBrush, QPen, QPainterPath, QColor
import api_client

class Port(QGraphicsItem):
    def __init__(self, parent, is_output=False):
        super().__init__(parent)
        self.is_output = is_output
        self.connections = []
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.rect = QGraphicsRectItem(-5, -5, 10, 10, self)
        self.rect.setBrush(QBrush(QColor("#00ffff")))

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemScenePositionHasChanged:
            for conn in self.connections:
                conn.update_path()
        return super().itemChange(change, value)

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
        self.rect.setBrush(QBrush(QColor("darkgray")))
        self.rect.setPen(QPen(QColor("white")))

        # Create the title
        self.title = QGraphicsTextItem(self.name, self)
        self.title.setDefaultTextColor(QColor("white"))
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
        # For now, we'll just join the inputs
        prompt = " ".join(self.inputs)
        logging.info(f"Executing node {self.node_id} with prompt: {prompt}")
        completion = api_client.post_completion(prompt)
        if completion:
            # A simple way to get the content, this might need to be adjusted
            # based on the actual response structure from LM Studio
            self.output = completion.get('choices', [{}])[0].get('message', {}).get('content', '')
            logging.info(f"Node {self.node_id} produced output: {self.output}")
        else:
            self.output = "" # Or handle the error appropriately
        return self.output


    def boundingRect(self):
        return self.rect.boundingRect()

    def paint(self, painter, option, widget):
        pass

class Connection(QGraphicsPathItem):
    def __init__(self, start_port, end_port):
        super().__init__()
        self.start_port, self.end_port = start_port, end_port
        self.start_port.connections.append(self)
        self.end_port.connections.append(self)
        self.setPen(QPen(QColor("white"), 2))
        self.update_path()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged and not value:
            for p in [self.start_port, self.end_port]:
                if self in p.connections:
                    p.connections.remove(self)
        return super().itemChange(change, value)

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

        # Cubic Bezier curve for a smoother look
        dx = end_pos.x() - start_pos.x()
        cp1 = QPointF(start_pos.x() + dx / 2, start_pos.y())
        cp2 = QPointF(end_pos.x() - dx / 2, end_pos.y())
        path.cubicTo(cp1, cp2, end_pos)

        self.setPath(path)
