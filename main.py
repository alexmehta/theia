from pyglet.gl import *
from pyglet.window import key
import math
import ctypes
import pyglet.gl as gl
import numpy as np
import pyrealsense2 as rs
import itertools
import collections

pipeline = rs.pipeline()
config = rs.config()

resx = 640;
resy = 480;


config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pc = rs.pointcloud()
pipeline.start(config)


class Cloudpoint:
    def __init__(self,tup,sx,sy):
        self.tup = tup;
        self.sx = sx;
        self.sy = sy;

class Model:

    def __init__(self):

        self.ticks = 0;
        self.soundtick= 0;
        self.setpointinterval = 240;
        self.xskip = 40;
        self.yskip = 40;

        self.downsampled = [];
        self.floodfilled = [];
        self.colors = [
            (1,1,1,1),
            (1,0,0,1),
            (0,0,1,1),
            (0,1,0,1),
            (1,1,0,1),
            (0,1,1,1),
            (1,0,1,1),
            (0.5,0.5,0.5,1)
        ]

        self.batch = pyglet.graphics.Batch()

        pyglet.gl.glPointSize(3)

    def draw(self):

        if(self.ticks % self.setpointinterval == 0):


            self.soundtick= 0;

            self.downsampled = [];
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            color_image = np.asanyarray(color_frame.get_data())

            pc.map_to(color_frame)
            points = pc.calculate(depth_frame)

            pointcoords = np.asanyarray(points.get_vertices())


            for y in range(0, int(resy/self.yskip) ):
                for x in range(0, int(resx/self.xskip) ):

                    point = tuple(pointcoords[y * self.yskip * resx + x * self.xskip])

                    self.downsampled.append(Cloudpoint(point,x,y));

            self.floodfilled = floodfill(self.downsampled, 0.3);
            self.floodfilled = updownsort(self.floodfilled);

        self.batch = pyglet.graphics.Batch()

        i = 0;

        for pointlist in self.floodfilled:

            tuples = [point.tup for point in pointlist];

            flat = list(itertools.chain.from_iterable(tuples));

            pointlength = int(len(flat)/3)

            self.batch.add(pointlength, GL_POINTS, None, ('v3f',flat), ('c4f', (self.colors[i % len(self.colors)] * pointlength) ))

            i += 1;


        soundtickclone = self.soundtick;
        index = 0;

        while(index < len(self.floodfilled) and soundtickclone > len(self.floodfilled[index])):
            soundtickclone -= len(self.floodfilled[index]);
            index += 1;



        soundpoint = None;
        soundpointbatch = pyglet.graphics.Batch();

        if(index < len(self.floodfilled)):
            soundpoint = self.floodfilled[index][soundtickclone-1];
            soundpointbatch.add(1, GL_POINTS, None, ('v3f', (soundpoint.tup[0], soundpoint.tup[1], soundpoint.tup[2]) ), ('c4f', (1.0,1.0,1.0,1.0)) );
            print("YO: ",soundpoint.tup,not ( int(soundpoint.tup[0]) == int(soundpoint.tup[1]) == int(soundpoint.tup[2]) == 0));




        self.ticks += 1;
        self.soundtick+= 1;
        pyglet.gl.glPointSize(3)
        self.batch.draw()
        pyglet.gl.glPointSize(10)
        soundpointbatch.draw();


def floodfill(points,distancethres):

    lists = [];
    currlist = [];
    chunks = {};

    for point in points:
        floored = (int(point.tup[0] / distancethres), int(point.tup[1] / distancethres), int(point.tup[2] / distancethres))

        if floored in chunks:
            chunks[floored].append(point)
        else:
            chunks[floored] = [point];

    chunkslist = list(chunks.keys());

    notreached = 0;

    while True:

        while ( notreached < len(chunkslist) ) and ( (chunkslist[notreached] in chunks) == False):
            notreached += 1;

        if notreached == len(chunkslist):
            break;

        chain = collections.deque([ chunkslist[notreached] ]);

        currlist += chunks[chain[0]];
        del chunks[chain[0]];

        closest = [[0,0,1],[0,0,-1],[0,1,0],[0,-1,0],[1,0,0],[-1,0,0],
                    [0,1,1],[0,1,-1],[0,-1,1],[0,-1,-1],
                    [1,1,-1], [-1,1,-1], [1,-1,-1], [-1,-1,-1], [1,1,1], [-1,1,1], [1,-1,1], [-1,-1,1],
                    [0,-1,-1], [0,1,-1], [1,0,-1], [-1,0,-1],[0,-1,1], [0,1,1], [1,0,1], [-1,0,1] ]

        while len(chain) > 0:

            for vec in closest:
                achunk = (chain[0][0]+vec[0],chain[0][1]+vec[1],chain[0][2]+vec[2]);

                if (achunk in chunks) == False: continue;

                currlist += chunks[achunk];

                chain.append(achunk);
                del chunks[achunk];

            chain.popleft();

        lists.append(currlist);
        currlist = [];

    return lists;

def updownsort(points):

    newlist = [list(filter(lambda point: not ( point.tup[0] == point.tup[1] == point.tup[2] == 0), pointlist)) for pointlist in points ];
    newlist = filter(lambda pointlist: len(pointlist)>0, newlist)

    def avg_z(pointlist):
        z = 0;
        for point in pointlist: z += point.tup[2];
        z /= len(pointlist);
        return z;

    newlist = sorted(newlist, key=avg_z)
    newlist = [sorted(pointlist, key=lambda point: (point.sx * 1000 + point.sy) ) for pointlist in newlist];
    return newlist;

def distance(t1, t2):
    return math.sqrt( (t2[0] - t1[0])**2 + (t2[1]-t1[1])**2 + (t2[2]-t1[2])**2);



class Player:
    def __init__(self,pos=(0,0,0),rot=(0,0)):
        self.pos = list(pos)
        self.rot = list(rot)

    def mouse_motion(self,dx,dy):
        dx/=8; dy/=8; self.rot[0]+=dy; self.rot[1]-=dx
        if self.rot[0]>90: self.rot[0] = 90
        elif self.rot[0]<-90: self.rot[0] = -90

    def update(self,dt,keys):
        s = dt*10
        rotY = -self.rot[1]/180*math.pi
        dx,dz = s*math.sin(rotY),s*math.cos(rotY)

        if keys[key.W]: self.pos[0]+=dx; self.pos[2]-=dz
        if keys[key.S]: self.pos[0]-=dx; self.pos[2]+=dz
        if keys[key.A]: self.pos[0]-=dz; self.pos[2]-=dx
        if keys[key.D]: self.pos[0]+=dz; self.pos[2]+=dx

        if keys[key.SPACE]: self.pos[1]+=s
        if keys[key.LSHIFT]: self.pos[1]-=s


class Window(pyglet.window.Window):

    def push(self,pos,rot): glPushMatrix(); glRotatef(-rot[0],1,0,0); glRotatef(-rot[1],0,1,0); glTranslatef(-pos[0],-pos[1],-pos[2],)
    def Projection(self): glMatrixMode(GL_PROJECTION); glLoadIdentity()
    def Model(self): glMatrixMode(GL_MODELVIEW); glLoadIdentity()
    def set2d(self): self.Projection(); gluOrtho2D(0,self.width,0,self.height); self.Model()
    def set3d(self): self.Projection(); gluPerspective(70,self.width/self.height,0.05,1000); self.Model()

    def setLock(self,state): self.lock = state; self.set_exclusive_mouse(state)
    lock = False; mouse_lock = property(lambda self:self.lock,setLock)

    def __init__(self,*args,**kwargs):

        super().__init__(*args,**kwargs)
        self.set_minimum_size(300,200)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        pyglet.clock.schedule(self.update)

        self.model = Model()
        self.player = Player((0,0,0),(0,180))
        self.mouse_lock = True;

    def on_mouse_motion(self,x,y,dx,dy):
        self.player.mouse_motion(dx,dy)

    def on_key_press(self,KEY,MOD):
        if KEY == key.ESCAPE: self.close()
        elif KEY == key.E: self.mouse_lock = not self.mouse_lock

    def update(self,dt):

        self.player.update(dt,self.keys)

        self.clear()
        self.set3d()
        self.push(self.player.pos,self.player.rot)
        self.model.draw();
        glPopMatrix()

        print(pyglet.clock.get_fps());




    #def on_draw(self):


if __name__ == '__main__':
    window = Window(width=854,height=480,caption='Minecraft',resizable=True, vsync = True)
    glClearColor(0,0,0,1)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_CULL_FACE)
    pyglet.app.run()
