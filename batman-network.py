import tkinter as tk
import random
import math
import time

class BatmanNetworkGUI:
    def __init__(self, master, num_nodes):
        self.master = master
        self.master.title("B.A.T.M.A.N Network Visualiser")

        self.canvas = tk.Canvas(self.master, width=800, height=600, bg="lightgray")
        self.canvas.pack()

        self.zoomFactor = 1.0
        self.numNodes = num_nodes
        self.minDistance = 100
        self.nodes = [Node(i, self.minDistance) for i in range(num_nodes)]

        self.createButtons()

        self.infiniteLoop()

    def createButtons(self):
        zoomOutButton = tk.Button(self.master, text="Zoom Out", command=lambda: self.zoom(0.9))
        zoomOutButton.pack(side=tk.BOTTOM)

        zoomInButton = tk.Button(self.master, text="Zoom In", command=lambda: self.zoom(1.1))
        zoomInButton.pack(side=tk.BOTTOM)

    def infiniteLoop(self):
        self.scatterNodes()
        self.master.after(2000, self.moveTowardsEachOther)

    def scatterNodes(self):
        for node in self.nodes:
            node.scatter(self.nodes)

        self.drawNetwork()
        self.master.after(200, self.scatterNodes)

    def moveTowardsEachOther(self):
        for node in self.nodes:
            node.moveTowardsEachOther()

        self.createConnectedNetwork()
        self.master.after(200, self.animateDataTransfer)

    def createConnectedNetwork(self):
        for i in range(self.numNodes - 1):
            for j in range(i + 1, self.numNodes):
                self.nodes[i].addNeighbor(self.nodes[j])

    def animateDataTransfer(self):
        self.drawNetwork()
        self.master.after(200, self.departFromPositions)

    def departFromPositions(self):
        for node in self.nodes:
            node.departFromPosition()

        self.disconnectNodes()
        self.master.after(200, self.connectToNearestNodes)

    def disconnectNodes(self):
        for node in self.nodes:
            node.clearNeighbors()

    def connectToNearestNodes(self):
        for node in self.nodes:
            node.connectToNearestNodes(self.nodes)

        self.drawNetwork()
        self.master.after(200, self.infiniteLoop)

    def drawNetwork(self):
        self.canvas.delete("all")

        for node in self.nodes:
            x, y = node.getScaledPosition(self.zoomFactor)
            self.canvas.create_oval(x - 10, y - 10, x + 10, y + 10, fill="blue", outline="black")

            for neighbor in node.neighbors:
                x1, y1 = node.getScaledPosition(self.zoomFactor)
                x2, y2 = neighbor.getScaledPosition(self.zoomFactor)
                transmissionRate = random.choice([100, 125, 150])
                transmissionText = f"{transmissionRate} Kbit/s"
                self.drawConnection(x1, y1, x2, y2, transmissionText)

        self.master.update()

    def drawConnection(self, x1, y1, x2, y2, transmissionText):
        self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
        midX = (x1 + x2) / 2
        midY = (y1 + y2) / 2
        self.canvas.create_text(midX, midY, text=transmissionText, fill="red")

    def zoom(self, factor):
        self.zoomFactor *= factor
        self.drawNetwork()

class Node:
    def __init__(self, nodeId, minDistance):
        self.nodeId = nodeId
        self.neighbors = set()
        self.x = random.uniform(50, 750)
        self.y = random.uniform(50, 550)
        self.finalX = random.uniform(50, 750)
        self.finalY = random.uniform(50, 550)
        self.minDistance = minDistance

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
        for otherNode in allNodes:
            if self != otherNode and random.random() < 0.3:
                distance = math.sqrt((self.x - otherNode.x)**2 + (self.y - otherNode.y)**2)
                if distance > self.minDistance:
                    self.addNeighbor(otherNode)

    def getScaledPosition(self, zoomFactor):
        return self.x * zoomFactor, self.y * zoomFactor

if __name__ == "__main__":
    numNodes = 10

    root = tk.Tk()
    app = BatmanNetworkGUI(root, numNodes)
    root.mainloop()
