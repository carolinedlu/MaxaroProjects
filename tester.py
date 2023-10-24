from direct.showbase.ShowBase import ShowBase
from panda3d.core import Geom, GeomNode, GeomVertexFormat, GeomVertexData
from panda3d.core import GeomTriangles, GeomVertexWriter
from panda3d.core import LVector3, DirectionalLight, AmbientLight

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.init()
        self.createRoom()
        self.control()

        
    def init(self):
        self.tl = LVector3(-5, 5, 5)
        self.tr = LVector3(5, 5, 5)
        self.bl = LVector3(-5, -5, 5)
        self.br = LVector3(5, -5, 5)
        self._bl = LVector3(-5, -5, -5)
        self._br = LVector3(5, -5, -5)
        self._tl = LVector3(-5, 5, -5)
        self._tr = LVector3(5, 5, -5)

    def control(self):
        self.camera.setPos(0, -20, 10)
        self.camera.lookAt(0, 0, 5)

        # Lighting setup
        dlight = DirectionalLight('dlight')
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-45, -45, 0)  # Set light direction
        self.render.setLight(dlnp)

        alight = AmbientLight('alight')
        alight.setColor((0.5, 0.5, 0.5, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        # Key event setup
        self.accept("arrow_left", self.moveCorner, [[self.tr, self._tr], -0.5, 0])
        #self.accept("arrow_right", self.moveCorner, [self.tl, 0.5, 0])
        #self.accept("arrow_up", self.moveCorner, [self.tl, 0, 0.5])
        #self.accept("arrow_down", self.moveCorner, [self.tl, 0, -0.5])

    def createRoom(self):
        # Create a single node for all walls
        self.roomNode = self.render.attachNewNode("Room")

        # Create individual walls
        self.leftWall = self.createWall(self.bl, self.tl, self._bl, self._tl, (1,0,0,1))
        self.rightWall = self.createWall(self.br, self.tr, self._br, self._tr, (0,1,0,1))
        self.frontWall = self.createWall(self.bl, self.br, self._bl, self._br, (0,0,1,1))
        self.backWall = self.createWall(self.tl, self.tr, self._tl, self._tr, (1,1,0,1))
        self.floor = self.createWall(self.bl, self.br, self.tl, self.tr, (1,0,1,1))

        # Attach walls to the room node
        self.roomNode.attachNewNode(self.leftWall)
        self.roomNode.attachNewNode(self.rightWall)
        self.roomNode.attachNewNode(self.frontWall)
        self.roomNode.attachNewNode(self.backWall)
        self.roomNode.attachNewNode(self.floor)

    def createWall(self, p1, p2, p3, p4, color):
        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData('wall', format, Geom.UHDynamic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        vertexColor = GeomVertexWriter(vdata, 'color')

        # Define vertices for the wall
        vertex.addData3(p1)
        vertex.addData3(p2)
        vertex.addData3(p3)
        vertex.addData3(p4)

        # Set color for the wall
        for _ in range(4):
            vertexColor.addData4(color)

        tris = GeomTriangles(Geom.UHDynamic)
        if color == (1,0,0,1):  # Left wall color
            tris.addVertices(0, 2, 1)
            tris.addVertices(1, 2, 3)
        else:
            tris.addVertices(0, 1, 2)
            tris.addVertices(1, 3, 2)

        wall = Geom(vdata)
        wall.addPrimitive(tris)
        wallNode = GeomNode('wall')
        wallNode.addGeom(wall)
        return wallNode

    def moveCorner(self, corner, x, y):
        for corner in corner:
            corner.setX(corner.getX() + x)
            corner.setY(corner.getY() + y)
        self.roomNode.removeNode()
        self.createRoom()

app = MyApp()
app.run()
