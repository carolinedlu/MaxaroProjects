from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight

from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay, CollisionHandlerEvent
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode, CollisionBox, Point3
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
        self.floor()
        self.set_cam()
        self.set_lights()
        self.collition_setup()
        self.furniture()

        self.dragging = False
        self.disableMouse()
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept('mouse1', self.grabItem)
        self.accept('mouse1-up', self.releaseItem)
        self.picker.showCollisions(render)

        

    def floor(self):
        cm = CardMaker('floor')
        cm.setFrame(-8, 8, -8, 8)  # This will create a plane of size 16x16
        floor = render.attachNewNode(cm.generate())
        floor.setColor(0.7, 0.7, 0.7, 1)  # Set the color to a light gray
        floor.setP(-90)  # Rotate it to be horizontal    
    
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
            self.picker.addCollider(cNodePath, self.furnitureCollisionHandler)
            
            self.furniture.append(box)

    def collition_setup(self):
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.furnitureCollisionHandler = CollisionHandlerEvent()

        self.furnitureCollisionHandler.setInPattern('furniture-into-furniture')

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)

        self.accept('furniture-into-furniture', self.handleCollision)

    def handleCollision(self, entry):
        print(entry)

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

def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())

app = MyApp()
app.run()