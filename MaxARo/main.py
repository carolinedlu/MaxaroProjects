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
        self.distanceTextNodes = []
        if not hasattr(self, 'lines_parent_node'):
            self.lines_parent_node = self.render.attachNewNode("LinesParent")

    def room(self):
        room = loader.loadModel("./Living room/living room.blend")
        room.reparentTo(render)
        room.setPos(0, 0, -1)
        room.setScale(4)  
    
    def set_cam(self):
        camera.setPosHpr(15, 0, 5, 0, 0, 0)  # Set the camera
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
            self.picker.addCollider(self.cNodePath, self.furColHandler)
            print(self.cNodePath.getName())

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
        if 'fur' in entry.getIntoNodePath().getName() and entry.getFromNodePath().getName() in self.movObject.getName():
            
            self.othObj = entry.getIntoNodePath().getParent()
            self.pos = self.findAngle(self.movObject.getParent().getPos(), self.othObj.getPos())
            if self.pos == 'front':
                self.allowY = True
                self.allowX = False
            elif self.pos == 'back':
                self.allowY = True
                self.allowX = False
            elif self.pos == 'left':
                self.allowX = True
                self.allowY = False
            elif self.pos == 'right':
                self.allowX = True
                self.allowY = False

    def mouseTask(self, task):
        if self.mouseWatcherNode.hasMouse():
            if not hasattr(self, 'allowX'):
                self.allowX = True
            if not hasattr(self, 'allowY'):
                self.allowY = True
            if not hasattr(self, 'prevPos'):
                self.prevPos = None
            
            mpos = self.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(self.camNode, mpos.getX(), mpos.getY())

            if self.dragging :
                nearPoint = render.getRelativePoint(
                    camera, self.pickerRay.getOrigin())
                nearVec = render.getRelativeVector(
                    camera, self.pickerRay.getDirection())
                newPos = PointAtZ(.5, nearPoint, nearVec)

                if self.prevPos:
                    self.direction = newPos - self.prevPos
                    self.direction.normalize()

                if hasattr(self, 'direction') and hasattr(self, 'pos'):
                    
                    if self.pos == 'front' and self.direction.getX() > 0:
                        self.allowX = True
                    elif self.pos == 'right' and self.direction.getY() > 0:
                        self.allowY = True
                    elif self.pos == 'back' and self.direction.getX() < 0:
                        self.allowX = True
                    elif self.pos == 'left' and self.direction.getY() < 0:
                        self.allowY = True
                try:
                    if self.movObject is not None and self.othObj is not None:
                        
                            minMov, maxMov = self.movObject.getParent().getTightBounds()
                            minOth, maxOth = self.othObj.getTightBounds()

                            if (minMov.getY() > maxOth.getY() or maxMov.getY() < minOth.getY()) and (self.pos == 'front' or self.pos == 'back'):
                                self.allowX = True
                            elif (minMov.getX() > maxOth.getX() or maxMov.getX() < minOth.getX()) and (self.pos == 'left' or self.pos == 'right'):
                                self.allowY = True
                except AttributeError:
                    pass

                if not self.allowX:
                    newPos.setX(self.dragging.getX())
                if not self.allowY:
                    newPos.setY(self.dragging.getY())
                self.dragging.setPos(newPos)

                # Update previous position
                self.prevPos = newPos

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
            self.lineQ.sortEntries()
            # Remove all children of the parent node to clear previous lines
            
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
                    print("else")
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


    def findAngle(self, obj1, obj2):
        pos = None

        object1 = {
            'position': obj1,
            'forward': np.array([0, 1, 0]),
            'right': np.array([1, 0, 0])
        }

        object2 = {
            'position': obj2
        }

        # Compute relative position
        relative_position = object2['position'] - object1['position']

        # Project onto reference directions
        forward_proj = np.dot(relative_position, object1['forward'])
        right_proj = np.dot(relative_position, object1['right'])
        # Determine relative positions
        if forward_proj > 0.5 and abs(forward_proj) > abs(right_proj):
            pos = 'left'
        elif forward_proj < -0.5 and abs(forward_proj) > abs(right_proj):
            pos = 'right'
        elif right_proj < -0.5 and abs(right_proj) > abs(forward_proj):
            pos = 'front'
        elif right_proj > 0.5 and abs(right_proj) > abs(forward_proj):
            pos = 'back'

        return pos




def PointAtZ(z, point, vec):
    return point + vec * ((z - point.getZ()) / vec.getZ())

app = MyApp()
app.run()