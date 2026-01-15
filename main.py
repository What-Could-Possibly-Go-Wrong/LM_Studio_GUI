import sys
import logging
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QWidget, QPushButton, QGraphicsLineItem
from PyQt6.QtCore import Qt, QLineF
import api_client
from widgets import NodeWidget, Port, Connection, NODE_COLOR_DEFAULT

# Configure logging
logging.basicConfig(filename='debug.log',
                    level=logging.INFO,
                    filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class ConnectionView(QGraphicsView):
    def __init__(self, scene):
        super().__init__(scene)
        self.start_port = None
        self.temp_line = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, Port) and item.is_output:
            self.start_port = item
            self.temp_line = QGraphicsLineItem(QLineF(self.start_port.scenePos(), self.mapToScene(event.pos())))
            self.scene().addItem(self.temp_line)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.temp_line:
            self.temp_line.setLine(QLineF(self.start_port.scenePos(), self.mapToScene(event.pos())))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.temp_line:
            self.scene().removeItem(self.temp_line)
            item = self.itemAt(event.pos())
            if isinstance(item, Port) and not item.is_output and self.start_port:
                connection = Connection(self.start_port, item)
                self.scene().addItem(connection)
                logging.info("Created a new connection.")
        self.temp_line = None
        self.start_port = None
        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LLM Graph Tool")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.scene = QGraphicsScene()
        self.view = ConnectionView(self.scene)

        self.add_node_button = QPushButton("Add Node")
        self.add_node_button.clicked.connect(lambda: self.add_node())

        self.save_button = QPushButton("Save Graph")
        self.save_button.clicked.connect(self.save_graph)

        self.load_button = QPushButton("Load Graph")
        self.load_button.clicked.connect(self.load_graph)

        self.execute_button = QPushButton("Execute Graph")
        self.execute_button.clicked.connect(self.execute_graph)

        self.layout.addWidget(self.add_node_button)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.execute_button)
        self.layout.addWidget(self.view)

        logging.info("Application Started")
        api_client.get_models()

    def add_node(self, name="LLM Box", pos=None, node_id=None):
        node = NodeWidget(name, node_id=node_id)
        if pos:
            node.setPos(pos[0], pos[1])
        self.scene.addItem(node)
        logging.info(f"Added a new node to the scene: {node.node_id}")
        return node

    def save_graph(self):
        nodes = []
        connections = []
        for item in self.scene.items():
            if isinstance(item, NodeWidget):
                nodes.append(item.to_dict())
            elif isinstance(item, Connection):
                connections.append(item.to_dict())

        graph_data = {'nodes': nodes, 'connections': connections}

        with open('graph.json', 'w') as f:
            json.dump(graph_data, f, indent=4)
        logging.info("Graph saved to graph.json")

    def load_graph(self):
        try:
            with open('graph.json', 'r') as f:
                graph_data = json.load(f)
        except FileNotFoundError:
            logging.error("graph.json not found.")
            return

        self.scene.clear()
        nodes = {}
        for node_data in graph_data['nodes']:
            node = self.add_node(node_data['name'], node_data['pos'], node_data['id'])
            nodes[node_data['id']] = node

        for conn_data in graph_data['connections']:
            from_node = nodes.get(conn_data['from_node'])
            to_node = nodes.get(conn_data['to_node'])
            if from_node and to_node:
                connection = Connection(from_node.output_port, to_node.input_port)
                self.scene.addItem(connection)

        logging.info("Graph loaded from graph.json")

    def execute_graph(self):
        nodes = [item for item in self.scene.items() if isinstance(item, NodeWidget)]
        connections = [item for item in self.scene.items() if isinstance(item, Connection)]

        # Reset node states before execution
        for node in nodes:
            node.set_color(NODE_COLOR_DEFAULT)

        # Build adjacency list and in-degree map
        adj = {node.node_id: [] for node in nodes}
        in_degree = {node.node_id: 0 for node in nodes}
        node_map = {node.node_id: node for node in nodes}

        for conn in connections:
            start_node = conn.start_port.parentItem()
            end_node = conn.end_port.parentItem()
            adj[start_node.node_id].append(end_node.node_id)
            in_degree[end_node.node_id] += 1

        # Find nodes with in-degree 0
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]

        execution_order = []
        while queue:
            node_id = queue.pop(0)
            execution_order.append(node_id)

            for neighbor_id in adj[node_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        if len(execution_order) != len(nodes):
            logging.error("Cycle detected in the graph. Cannot execute.")
            return

        logging.info(f"Execution order: {execution_order}")

        for node_id in execution_order:
            node = node_map[node_id]
            # Gather inputs from connections
            node.inputs = []
            for conn in connections:
                if conn.end_port.parentItem() == node:
                    start_node = conn.start_port.parentItem()
                    node.inputs.append(start_node.output)

            node.execute()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Dark mode stylesheet
    app.setStyleSheet("""
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QMainWindow {
            background-color: #2b2b2b;
        }
        QGraphicsView {
            border: 1px solid #444444;
        }
        QPushButton {
            background-color: #555555;
            border: 1px solid #666666;
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #666666;
        }
        QLineEdit, QTextEdit {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 3px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
