import tkinter as tk
import random
import math
from tkinter import simpledialog, Scrollbar, Text

class BatmanNetworkGUI:
    def __init__(self, master, num_nodes):
        self.master = master
        self.master.title("B.A.T.M.A.N Network Visualiser")

        self.canvas = tk.Canvas(self.master, width=800, height=600, bg="lightgray")
        self.canvas.pack()

        self.zoomFactor = 1.0
        self.minDistance = 100
        self.nodes = [Node(i, self.minDistance, self) for i in range(num_nodes)]
        self.simulationRunning = True
        self.selected_node_id = None  # Track the node for which the routing table is displayed

        self.createRoutingTableFrame()
        self.createButtons()
        self.startSimulation()

    def createRoutingTableFrame(self):
        self.routingTableFrame = tk.Frame(self.master)
        self.routingTableFrame.pack(side=tk.RIGHT, fill=tk.Y)

        self.routingTableText = Text(self.routingTableFrame, wrap=tk.NONE)
        self.routingTableText.pack(side=tk.LEFT, fill=tk.Y)

        self.scrollbar = Scrollbar(self.routingTableFrame, command=self.routingTableText.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.routingTableText.config(yscrollcommand=self.scrollbar.set)

    def createButtons(self):
        startButton = tk.Button(self.master, text="Start Simulation", command=self.startSimulation)
        startButton.pack(side=tk.LEFT)

        stopButton = tk.Button(self.master, text="Stop Simulation", command=self.stopSimulation)
        stopButton.pack(side=tk.LEFT)

        addNodeButton = tk.Button(self.master, text="Add Node", command=self.addNode)
        addNodeButton.pack(side=tk.LEFT)

        removeNodeButton = tk.Button(self.master, text="Remove Node", command=self.removeNode)
        removeNodeButton.pack(side=tk.LEFT)

        showRoutingTableButton = tk.Button(self.master, text="Show Routing Table", command=self.promptRoutingTable)
        showRoutingTableButton.pack(side=tk.LEFT)

        explainBATMANButton = tk.Button(self.master, text="Explain BATMAN", command=self.explainBATMAN)
        explainBATMANButton.pack(side=tk.LEFT)

        zoomOutButton = tk.Button(self.master, text="Zoom Out", command=lambda: self.zoom(0.9))
        zoomOutButton.pack(side=tk.BOTTOM)

        zoomInButton = tk.Button(self.master, text="Zoom In", command=lambda: self.zoom(1.1))
        zoomInButton.pack(side=tk.BOTTOM)

        broadcastMessageButton = tk.Button(self.master, text="Broadcast Message", command=self.broadcastMessage)
        broadcastMessageButton.pack(side=tk.LEFT)

    def startSimulation(self):
        self.simulationRunning = True
        self.infiniteLoop()

    def stopSimulation(self):
        self.simulationRunning = False

    def addNode(self):
        newNode = Node(len(self.nodes), self.minDistance, self)
        self.nodes.append(newNode)
        self.connectToNearestNodes()

    def removeNode(self):
        if self.nodes:
            node_to_remove = self.nodes.pop()
            for node in self.nodes:
                node.neighbors.discard(node_to_remove)
                if node_to_remove.nodeId in node.routing_table:
                    del node.routing_table[node_to_remove.nodeId]
        self.updateRoutingTable()

    def promptRoutingTable(self):
        self.stopSimulation()
        node_id = simpledialog.askinteger("Input", "Enter Node ID:", parent=self.master, minvalue=0, maxvalue=len(self.nodes)-1)
        if node_id is not None:
            self.selected_node_id = node_id
            self.startSimulation()  # Resume the simulation
        else:
            self.selected_node_id = None

    def updateRoutingTable(self):
        if self.selected_node_id is not None:
            node = self.nodes[self.selected_node_id]
            routing_info = f"Node {self.selected_node_id} Routing Table:\n"
            for dest, (next_hop, seq_num) in node.routing_table.items():
                routing_info += f"Destination: {dest}, Next Hop: {next_hop.nodeId}, Sequence Number: {seq_num}\n"
            self.routingTableText.delete("1.0", tk.END)
            self.routingTableText.insert(tk.END, routing_info)

    def explainBATMAN(self):
        explanation_window = tk.Toplevel(self.master)
        explanation_window.title("BATMAN Explanation")
        explanation_text = ("BATMAN (Better Approach To Mobile Adhoc Networking) is a routing protocol designed "
                            "for decentralized, ad-hoc networks. In this simulation, nodes broadcast Originator "
                            "Messages (OGMs) to announce their presence and learn about the network topology. Each "
                            "node maintains a routing table that stores the best next hop for reaching other nodes "
                            "based on the most recent OGMs received.")
        label = tk.Label(explanation_window, text=explanation_text, wraplength=400, justify=tk.LEFT)
        label.pack()

    def infiniteLoop(self):
        if self.simulationRunning:
            self.scatterNodes()
            self.master.after(2000, self.moveTowardsEachOther)

    def scatterNodes(self):
        for node in self.nodes:
            node.scatter(self.nodes)
        self.drawNetwork()
        if self.simulationRunning:
            self.master.after(200, self.scatterNodes)

    def moveTowardsEachOther(self):
        for node in self.nodes:
            node.moveTowardsEachOther()

        self.createConnectedNetwork()
        if self.simulationRunning:
            self.master.after(200, self.broadcastOGMs)

    def createConnectedNetwork(self):
        # Ensure nodes are not directly connected to everyone but to a subset of nodes to simulate an ad-hoc network
        for node in self.nodes:
            node.connectToNearestNodes(self.nodes)

    def broadcastOGMs(self):
        for node in self.nodes:
            node.broadcastOGM()
        self.updateRoutingTable()  # Update the routing table dynamically

        self.drawNetwork()
        if self.simulationRunning:
            self.master.after(200, self.departFromPositions)

    def departFromPositions(self):
        for node in self.nodes:
            node.departFromPosition()

        self.disconnectNodes()
        if self.simulationRunning:
            self.master.after(200, self.connectToNearestNodes)

    def disconnectNodes(self):
        for node in self.nodes:
            node.clearNeighbors()

    def connectToNearestNodes(self):
        for node in self.nodes:
            node.connectToNearestNodes(self.nodes)

        self.drawNetwork()
        if self.simulationRunning:
            self.master.after(200, self.infiniteLoop)

    def drawNetwork(self):
        self.canvas.delete("all")

        for node in self.nodes:
            x, y = node.getScaledPosition(self.zoomFactor)
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill=node.color, outline="black")
            self.canvas.create_text(x, y - 15, text=f"{node.nodeId}", fill="black")  # Label each node with its ID

            for neighbor in node.neighbors:
                x1, y1 = node.getScaledPosition(self.zoomFactor)
                x2, y2 = neighbor.getScaledPosition(self.zoomFactor)
                transmissionRate = random.choice([100, 125, 150])  # Simulated network speeds
                self.drawConnection(x1, y1, x2, y2, transmissionRate)

        self.master.update()

    def drawConnection(self, x1, y1, x2, y2, transmissionRate):
        self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
        midX = (x1 + x2) / 2
        midY = (y1 + y2) / 2
        self.canvas.create_text(midX, midY, text=f"{transmissionRate}", fill="red")  # Show network speed without units

    def zoom(self, factor):
        self.zoomFactor *= factor
        self.drawNetwork()

    def broadcastMessage(self):
        if self.nodes:
            # Select a random node to initiate the broadcast
            initial_node = random.choice(self.nodes)
            initial_node.color = "red"  # Change color to red to indicate broadcasting
            self.drawNetwork()
            self.master.after(100, lambda: initial_node.broadcastMulticastMessage(message_id=random.randint(1, 1000)))

class Node:
    def __init__(self, nodeId, minDistance, master):
        self.nodeId = nodeId
        self.neighbors = set()
        self.x = random.uniform(50, 750)
        self.y = random.uniform(50, 550)
        self.finalX = random.uniform(50, 750)
        self.finalY = random.uniform(50, 550)
        self.minDistance = minDistance
        self.routing_table = {}  # Destination -> (Next Hop, Sequence Number)
        self.seq_num = 0  # Sequence number for OGMs
        self.received_messages = set()  # Track received messages to prevent loops
        self.color = "blue"  # Default color for the node
        self.master = master

    def addNeighbor(self, neighbor):
        self.neighbors.add(neighbor)
        neighbor.neighbors.add(self)

    def scatter(self, allNodes):
        speed = 0.005
        newX = self.x + (random.uniform(50, 750) - self.x) * speed
        newY = self.y + (random.uniform(50, 550) - self.y) * speed

        for otherNode in allNodes:
            if self != otherNode:
                distance = math.sqrt((newX - otherNode.x)**2 + (newY - otherNode.y)**2)
                if distance < self.minDistance:
                    return

        self.x = newX
        self.y = newY

    def moveTowardsEachOther(self):
        speed = 0.005
        self.x += (self.finalX - self.x) * speed
        self.y += (self.finalY - self.y) * speed

    def departFromPosition(self):
        speed = 0.005
        self.x += (random.uniform(50, 750) - self.x) * speed
        self.y += (random.uniform(50, 550) - self.y) * speed

    def clearNeighbors(self):
        self.neighbors.clear()

    def connectToNearestNodes(self, allNodes):
        # Connect only to nearest nodes within a certain distance to simulate an ad-hoc network
        for otherNode in allNodes:
            if self != otherNode:
                distance = math.sqrt((self.x - otherNode.x)**2 + (self.y - otherNode.y)**2)
                if distance <= self.minDistance * 1.5:
                    self.addNeighbor(otherNode)

    def getScaledPosition(self, zoomFactor):
        return self.x * zoomFactor, self.y * zoomFactor

    def broadcastOGM(self):
        """Broadcast Originator Messages (OGMs) to all neighbors."""
        self.seq_num += 1
        for neighbor in self.neighbors:
            neighbor.receiveOGM(self.nodeId, self, self.seq_num)

    def receiveOGM(self, originator_id, sender, seq_num):
        """Process an incoming OGM."""
        if originator_id not in self.routing_table or seq_num > self.routing_table[originator_id][1]:
            # Update routing table with the best next hop and the newest sequence number
            self.routing_table[originator_id] = (sender, seq_num)
            # Re-broadcast the OGM to other neighbors except the sender
            for neighbor in self.neighbors:
                if neighbor != sender:
                    neighbor.receiveOGM(originator_id, self, seq_num)

    def broadcastMulticastMessage(self, message_id):
        """Broadcast a multicast message to all neighbors."""
        if message_id not in self.received_messages:
            self.received_messages.add(message_id)
            self.color = "green"  # Change color to green to show message received
            self.updateGUI()  # Update the GUI to reflect the color change
            self.master.master.after(200, lambda: self.forwardMessage(message_id))  # Delay the forwarding slightly

    def forwardMessage(self, message_id):
        """Forward the message to all neighbors after a slight delay."""
        for neighbor in self.neighbors:
            neighbor.receiveMulticastMessage(message_id, self)
        self.master.master.after(500, self.resetColorAfterDelay)  # Reset color after 500ms delay

    def receiveMulticastMessage(self, message_id, sender):
        """Process and forward a multicast message."""
        if message_id not in self.received_messages:
            self.received_messages.add(message_id)
            self.color = "green"  # Change color to green to show message received
            self.updateGUI()  # Update the GUI to reflect the color change
            self.master.master.after(200, lambda: self.forwardMessageToNeighbors(message_id, sender))  # Delay forwarding slightly

    def forwardMessageToNeighbors(self, message_id, sender):
        """Forward the message to all neighbors except the sender after a slight delay."""
        for neighbor in self.neighbors:
            if neighbor != sender:
                neighbor.receiveMulticastMessage(message_id, self)
        self.master.master.after(500, self.resetColorAfterDelay)  # Reset color after 500ms delay

    def resetColorAfterDelay(self):
        """Reset node color to blue after a short delay."""
        self.color = "blue"
        self.updateGUI()

    def updateGUI(self):
        """Helper function to refresh the GUI and apply color changes."""
        self.master.drawNetwork()
        self.master.master.update_idletasks()

if __name__ == "__main__":
    numNodes = 10

    root = tk.Tk()
    app = BatmanNetworkGUI(root, numNodes)
    root.mainloop()
