from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight, PointLight

from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode, LineSegs, CollisionHandlerPusher
from panda3d.core import CollisionHandlerQueue, CollisionRay, CollisionHandlerEvent
from panda3d.core import AmbientLight, DirectionalLight, LightAttrib
from panda3d.core import TextNode, CollisionBox, Point3, NodePath
from panda3d.core import LPoint3, LVector3, BitMask32, Vec3, VBase4, TextureStage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
import numpy as np
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
        self.room()
        self.taskMgr.add(self.drawLine, "update_line_task")
        

        
    def init(self):
        self.dragging = False
        self.disableMouse()
        self.mouseTask = taskMgr.add(self.mouseTask, 'mouseTask')
        self.accept('mouse1', self.grabItem)
        self.accept('mouse1-up', self.releaseItem)
        self.picker.showCollisions(render)
        self.inProx = False
        self.obj1 = None
        self.obj2 = None
        self.distanceTextNodes = []
        if not hasattr(self, 'lines_parent_node'):
            self.lines_parent_node = self.render.attachNewNode("LinesParent")

    def room(self):
        def add_collision_box(plane, center, half_diagonal, name):
            cbox = CollisionBox(center, half_diagonal)
            cnode = CollisionNode(name)
            cnode.setIntoCollideMask(BitMask32.bit(2))
            cnode.setFromCollideMask(0)
            cnode.addSolid(cbox)
            plane.attachNewNode(cnode)

        
        wall_tex = loader.loadTexture("wall.jpg")
        ceiling_tex = loader.loadTexture("floor.jpg")
        floor_tex = loader.loadTexture("ceiling.jpg")

        cm = CardMaker("plane")
        cm.setFrame(-10, 10, -10, 10)

        floor = self.render.attachNewNode(cm.generate())
        floor.setPos(0, 0, 0)
        floor.setP(-90)
        floor.setTexture(floor_tex)
        floor.setTexScale(TextureStage.getDefault(), 3, 3)

        left = self.render.attachNewNode(cm.generate())
        left.setPos(-10, 0, 0)
        left.setH(90)
        left.setTexture(wall_tex)
        left.setTexScale(TextureStage.getDefault(), 1, 1)
        add_collision_box(left, LPoint3(-10, 0, 0), LPoint3(10, 5, 10), "wall_left")
        
        right = self.render.attachNewNode(cm.generate())
        right.setPos(0, 10, 0)
        right.setTexture(wall_tex)
        right.setTexScale(TextureStage.getDefault(), 1, 1)
        add_collision_box(right, LPoint3(-15, -0, 0), LVector3(10, 5, 10), "wall_right")

        ceiling = self.render.attachNewNode(cm.generate())
        ceiling.setPos(0, 0, 10)
        ceiling.setP(90)
        ceiling.setTexture(ceiling_tex)
    
    def set_cam(self):
        camera.setPosHpr(15, -12.5, 7.5, 0, 0, 0)  # Set the camera
        #camera.setPosHpr(15, -12.5, 50, 0, 0, 0)
        camera.lookAt(0, 0, 5)

    def set_lights(self):
        mainLight = PointLight('main light')
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setPos(3, -3, 8)
        mainLight.setColor(VBase4(1.9, 1.82, 1.33, 1))
        render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor(VBase4(0.1, 0.1, 0.1, .5))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)


    def furniture(self):
        self.furniture = []
        for i in range(5):  # Create 5 pieces of furniture
            box = loader.loadModel("grass-block.glb")  # Assuming you have a box model
            box.reparentTo(render)
            box.setScale(.5)  # Adjust the size as needed
            box.setPos(i*3 - 4, i*3 - 4, 0.5)  # Position them in the room
            
            dragNode = CollisionNode(f'dragfur{i}')
            cBox = CollisionBox(Point3(-1, -1, -1), Point3(1, 1, 1))
            dragNode.addSolid(cBox)
            dragNode.setIntoCollideMask(BitMask32.bit(1))
            dragNode.set_from_collide_mask(0)
            dragNodePath = box.attachNewNode(dragNode)
            self.picker.addCollider(dragNodePath, self.pq)
            
            # Collision for furniture collision detection
            cNode = CollisionNode(f'fur{i}')
            cNode.addSolid(cBox)
            cNode.setFromCollideMask(BitMask32.bit(2))
            cNode.setIntoCollideMask(BitMask32.bit(2))
            self.cNodePath = box.attachNewNode(cNode)
            self.pusher.addCollider(self.cNodePath, box)
            self.picker.addCollider(self.cNodePath, self.pusher)

            rad = 2
            proximityNode = CollisionNode('proximity')
            proximityBox = CollisionBox(Point3(-rad, -rad, -1), Point3(rad, rad, 1))
            proximityBox.setTangible(False)
            proximityNode.addSolid(proximityBox)
            proximityNode.setIntoCollideMask(BitMask32.bit(3))
            proximityNode.setFromCollideMask(BitMask32.bit(3))
            proximityNodePath = box.attachNewNode(proximityNode)
            self.picker.addCollider(proximityNodePath, self.lineQ)
            
            self.furniture.append(box)

    def collision_setup(self):
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.lineQ = CollisionHandlerQueue()
        self.pusher = CollisionHandlerPusher()

        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)


    def mouseTask(self, task):
        if self.mouseWatcherNode.hasMouse():
            if not hasattr(self, 'allowX'):
                self.allowX = True
            if not hasattr(self, 'allowY'):
                self.allowY = True
            
            mpos = self.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            if self.dragging :
                if not hasattr(self, 'prevPos'):
                    self.prevPos = self.dragging.getPos()

                nearPoint = render.getRelativePoint(
                    camera, self.pickerRay.getOrigin())
                nearVec = render.getRelativeVector(
                    camera, self.pickerRay.getDirection())
                newPos = PointAtZ(.5, nearPoint, nearVec)

                if self.prevPos:
                    base_speed = 0
                    acceleration_factor = 10
                    direction = newPos - self.prevPos
                    distance = direction.length()
                    speed = base_speed + distance * acceleration_factor
                    if speed > 40:
                        speed = 40
                    direction.normalize()

                    # Calculate the movement for this frame
                    movement = direction * speed * globalClock.getDt()

                    # Update the object's position
                    self.dragging.setPos(self.dragging.getPos() + movement)

                    # Update previous position
                    self.prevPos = self.dragging.getPos()

            self.picker.traverse(render)
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
        return Task.cont
    
    def grabItem(self):
        if self.pq.getNumEntries() > 0:
            self.dragging = self.pq.getEntry(0).getIntoNodePath().getParent()
            self.movObject = self.pq.getEntry(0).getIntoNodePath()

    def releaseItem(self):
        self.dragging = False

    def drawLine(self, task):
        self.lines_parent_node.node().removeAllChildren()
        if self.lineQ.getNumEntries() > 0:
            
            for i in range(self.lineQ.getNumEntries()):
                self.ent = self.lineQ.getEntry(i)
                ob1pos = self.ent.getFromNodePath().getParent().getPos()
                ob2pos = self.ent.getIntoNodePath().getParent().getPos()
                
                distance = (ob1pos - ob2pos).length()
                
                #if distance < 0:

                # Create a new LineSegs for each entry
                line_segs = LineSegs()
                line_segs.moveTo(ob1pos)
                line_segs.drawTo(ob2pos)
                
                # Create a new node for the line and attach it to the parent node
                line_node = line_segs.create()
                self.lines_parent_node.attachNewNode(line_node)

                midpoint = (ob1pos + ob2pos) / 2

                direction = (midpoint - camera.getPos()).normalized()

                fixed_distance = 10

                text_position = camera.getPos() + direction * fixed_distance
                
                if i < len(self.distanceTextNodes):
                    textNode = self.distanceTextNodes[i]
                    textNode.node().setText(f"{distance:.2f}")
                    textNode.setPos(text_position)
                    textNode.lookAt(camera)
                    textNode.setHpr(90, 0, 0)
                else:
                    distanceTextNode = TextNode(f'distanceTextNode_{i}')
                    distanceTextNode.setTextColor(1, 1, 1, 1)  # Set text color to white
                    distanceText = self.render.attachNewNode(distanceTextNode)
                    distanceText.setScale(.25)  # Adjust the scale as needed
                    distanceText.setPos(text_position)
                    distanceTextNode.setText(f"{distance:.2f}")
                    distanceText.lookAt(camera)
                    distanceText.setHpr(90, 0, 0)
                    self.distanceTextNodes.append(distanceText)
        else:
            for textNode in self.distanceTextNodes:
                textNode.removeNode()
            self.distanceTextNodes = []
        return Task.cont


def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())

app = MyApp()
app.run()