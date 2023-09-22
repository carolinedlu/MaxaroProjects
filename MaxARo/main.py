from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight

from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode, LineSegs, CollisionSolid
from panda3d.core import CollisionHandlerQueue, CollisionRay, CollisionHandlerEvent
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode, CollisionBox, Point3, NodePath
from panda3d.core import LPoint3, LVector3, BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import sys
from panda3d.core import Plane, PlaneNode, GeomNode, CardMaker

loadPrcFile('settings.prc')

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.set_cam()
        self.set_lights()
        self.collision_setup()
        self.init()
        self.furniture()
        #self.room()
        self.taskMgr.add(self.drawLine, "update_line_task")
        

        
    def init(self):
        self.dragging = False
        self.disableMouse()
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept('mouse1', self.grabItem)
        self.accept('mouse1-up', self.releaseItem)
        #self.picker.showCollisions(render)
        self.inProx = False
        self.obj1 = None
        self.obj2 = None
        self.line_segs = LineSegs()
        self.line_segs.setThickness(4)
        self.line_node = self.line_segs.create()
        self.line_node_path = self.render.attachNewNode(self.line_node)
        self.distanceTextNodes = []
        if not hasattr(self, 'lines_parent_node'):
            self.lines_parent_node = self.render.attachNewNode("LinesParent")

    def room(self):
        room = loader.loadModel("./Living room/living room.blend")
        room.reparentTo(render)
        room.setPos(0, 0, -1)
        room.setScale(4)  
    
    def set_cam(self):
        camera.setPosHpr(5, -20, 10, 0, 0, 0)  # Set the camera
        camera.lookAt(0, 0, 0)

    def set_lights(self):
        mainLight = DirectionalLight('main light')
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(30, -60, 0)
        render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.2, 0.2, 0.2, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)

    def furniture(self):
        self.furniture = []
        for i in range(5):  # Create 5 pieces of furniture
            box = loader.loadModel("grass-block.glb")  # Assuming you have a box model
            box.reparentTo(render)
            box.setScale(0.5)  # Adjust the size as needed
            box.setPos(i*2 - 4, i*2 - 4, 0.5)  # Position them in the room
            
            dragNode = CollisionNode('drag')
            cBox = CollisionBox(Point3(-1, -1, -1), Point3(1, 1, 1))
            dragNode.addSolid(cBox)
            dragNode.setIntoCollideMask(BitMask32.bit(1))
            dragNode.set_from_collide_mask(0)
            dragNodePath = box.attachNewNode(dragNode)
            self.picker.addCollider(dragNodePath, self.pq)
            
            # Collision for furniture collision detection
            cNode = CollisionNode('furniture')
            cNode.addSolid(cBox)
            cNode.setFromCollideMask(BitMask32.bit(2))
            cNodePath = box.attachNewNode(cNode)
            self.picker.addCollider(cNodePath, self.furColHandler)

            rad = 2
            proximityNode = CollisionNode('proximity')
            proximityBox = CollisionBox(Point3(-rad, -rad, -1), Point3(rad, rad, 1))
            proximityBox.setTangible(False)
            proximityNode.addSolid(proximityBox)
            proximityNode.setIntoCollideMask(0)
            proximityNode.setFromCollideMask(BitMask32.bit(3))
            proximityNodePath = box.attachNewNode(proximityNode)
            self.picker.addCollider(proximityNodePath, self.lineQ)
            
            self.furniture.append(box)

    def collision_setup(self):
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.lineQ = CollisionHandlerQueue()
        self.furColHandler = CollisionHandlerEvent()
        self.furColHandler.setInPattern('furniture-into-furniture')

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)

        self.accept('furniture-into-furniture', self.handleCollision)

    def handleCollision(self, entry):
        movObject = entry.getFromNodePath().getParent()
        if entry.getIntoNodePath().getName() == 'furniture' and entry.getFromNodePath().getName() == 'furniture':
            movObject.setPos(entry.getSurfaceNormal(render) + movObject.getPos())

    def mouseTask(self, task):
        if self.mouseWatcherNode.hasMouse():
            mpos = self.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            if self.dragging:
                nearPoint = render.getRelativePoint(
                    camera, self.pickerRay.getOrigin())
                nearVec = render.getRelativeVector(
                    camera, self.pickerRay.getDirection())
                self.dragging.setPos(PointAtZ(.5, nearPoint, nearVec))

            self.picker.traverse(render)
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
        return Task.cont
    
    def grabItem(self):
        if self.pq.getNumEntries() > 0:
            self.dragging = self.pq.getEntry(0).getIntoNodePath().getParent()

    def releaseItem(self):
        self.dragging = False

    def drawLine(self, task):
        if self.lineQ.getNumEntries() > 0:
            self.lineQ.sortEntries()
            # Remove all children of the parent node to clear previous lines
            self.lines_parent_node.node().removeAllChildren()
            
            for i in range(self.lineQ.getNumEntries()):
                self.ent = self.lineQ.getEntry(i)
                ob1pos = self.ent.getFromNodePath().getParent().getPos()
                ob2pos = self.ent.getIntoNodePath().getParent().getPos()
                # Create a new LineSegs for each entry
                line_segs = LineSegs()
                line_segs.moveTo(ob1pos)
                line_segs.drawTo(ob2pos)
                
                distance = (ob1pos - ob2pos).length()

                # Create a new node for the line and attach it to the parent node
                line_node = line_segs.create()
                self.lines_parent_node.attachNewNode(line_node)

                midpoint = (ob1pos + ob2pos) / 2
                
                if i < len(self.distanceTextNodes):
                    textNode = self.distanceTextNodes[i]
                    textNode.node().setText(f"{distance:.2f}")
                    textNode.setPos(midpoint)
                else:
                    # Create a new text node for this line
                    distanceTextNode = TextNode(f'distanceTextNode_{i}')
                    distanceTextNode.setTextColor(1, 1, 1, 1)  # Set text color to white
                    distanceText = self.render.attachNewNode(distanceTextNode)
                    distanceText.setScale(0.1)  # Adjust the scale as needed
                    distanceText.setPos(midpoint)
                    distanceTextNode.setText(f"{distance:.2f}")
                    self.distanceTextNodes.append(distanceText)
        else:
            print("No collisions")
            for textNode in self.distanceTextNodes:
                textNode.removeNode()
            self.lines_parent_node.node().removeAllChildren()
            self.distanceTextNodes.clear()
        return Task.cont

def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())

app = MyApp()
app.run()