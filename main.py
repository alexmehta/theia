from pyglet.gl import *
from pyglet.window import key
import math
import ctypes
import pyglet.gl as gl
import numpy as np
import pyrealsense2 as rs
import itertools
import collections
import pygame.midi
import time

pygame.midi.init()
output = pygame.midi.Output(0)

def drum(pitch, volume, pan):
    output.write_short(192, 117);
    output.write_short(176, 10, pan);
    output.write_short(0x90, pitch, volume)
    output.write_short(192, 0);

def playnote(pitch, volume, pan):

    output.write_short(176, 10, pan);
    output.write_short(0x90, pitch, volume)

def offnote(pitch, volume):
    output.write_short(128, pitch, volume);


pipeline = rs.pipeline()
config = rs.config()

resx = 640;
resy = 480;


config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pc = rs.pointcloud()
pipeline.start(config)

audioplayer = pyglet.media.Player()
audioplayer.position = (0,0,0);

def get_soundindex(distance):

    if not (0.3 <= distance <= 5.3): return None;

    return int( 40 * ( (distance - 0.3) / 5 )**0.65 )



class Cloudpoint:
    def __init__(self,tup,sx,sy):
        self.tup = tup;
        self.sx = sx;
        self.sy = sy;

class Model:

    def __init__(self):

        self.ticks = 0;
        self.setpointinterval = 4000;

        self.soundtick= 0;
        self.soundtickinterval = 20;
        self.soundpoint = None;
        self.lastnote = None;
        self.repeated = False;

        self.thetamax = 45;

        self.xskip = 40;
        self.yskip = 40;

        self.downsampled = [];

        self.downsampledmap = [];

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
        self.soundpointbatch = pyglet.graphics.Batch()


        pyglet.gl.glPointSize(3)

    def draw(self):

        if(self.ticks % self.setpointinterval == 0):


            print("Redraw");

            self.soundtick= 0;

            self.downsampled = [];
            self.downsampledmap = [];

            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            color_image = np.asanyarray(color_frame.get_data())

            pc.map_to(color_frame)

            points = np.asanyarray(depth_frame.get_data());

            for x in range(0, int(resx / self.xskip)):
                for y in range(0, int(resy / self.yskip)):
                    depth = depth_frame.get_distance(x * self.xskip, y * self.yskip);
                    self.downsampled.append( depth );


                    inbound = get_soundindex(depth) != None;

                    if inbound:
                        self.downsampledmap.append( x / (resx / self.xskip) )
                        self.downsampledmap.append( y / (resx / self.xskip) )
                        self.downsampledmap.append( depth )


        if( (self.ticks % self.setpointinterval) % self.soundtickinterval == 0 and self.soundtick < len(self.downsampled) ):

            self.soundpointbatch = pyglet.graphics.Batch();

            soundindex = get_soundindex(self.downsampled[self.soundtick]);

            y = self.soundtick % (resy / self.yskip);
            x = int(self.soundtick / (resy / self.yskip));



            self.soundpointbatch.add(1, GL_POINTS, None, ('v3f',(

                x / (resx / self.xskip),y / (resx / self.xskip),self.downsampled[self.soundtick]))

            , ('c4f', (self.colors[1]) ))


            x = x / ( (resx / self.xskip) - 1)
            x = 128 - int(x * 128);

            if(self.lastnote != None):
                offnote(self.lastnote, 128);


            dorepeat = int(self.soundtick / (resy / self.yskip)) > int( (self.soundtick-1) / (resy / self.yskip))
            if(dorepeat and self.repeated == False):
                self.repeated = True;
                drum(70, 100, x);
                self.soundtick -= 1;
            elif(soundindex != None):
                playnote( (40-soundindex)*2 + 25, int((40-soundindex)*2.5), x)
                self.lastnote = soundindex;
                self.repeated = False;
            elif(soundindex == None):
                drum(50, 100, x);




            self.soundtick += 1;



        self.batch = pyglet.graphics.Batch()

        pointlength = int(len(self.downsampledmap) / 3)

        self.batch.add(pointlength, GL_POINTS, None, ('v3f',self.downsampledmap), ('c4f', (self.colors[0] * pointlength) ))

        self.ticks += 1;
        pyglet.gl.glPointSize(3)
        self.batch.draw()
        pyglet.gl.glPointSize(15)
        self.soundpointbatch.draw();

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

        #print(pyglet.clock.get_fps());



if __name__ == '__main__':
    window = Window(width=854,height=480,caption='Minecraft',resizable=True, vsync = True)
    glClearColor(0,0,0,1)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_CULL_FACE)
    pyglet.app.run()
