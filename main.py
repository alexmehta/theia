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
import pygame
import time

pygame.midi.init()
pygame.init();
pygame.font.init()

my_font = pygame.font.SysFont('Comic Sans MS', 30)

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


mindistance = 0.3;
maxdistance = 5.3
magnitude = 40;
smoothen = 0.65;

def get_soundindex(distance):

    if not (mindistance <= distance <= maxdistance): return None;

    return int( magnitude * ( (distance - mindistance) / (maxdistance - mindistance) )**smoothen )




class Model:

    def __init__(self):

        self.ticks = 0;
        self.setpointinterval = 4000;

        self.soundtick= 0;
        self.soundtickinterval = 5;
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

        pyglet.gl.glPointSize(3)

    def draw(self):

        if(self.ticks % self.setpointinterval == 0 or pygame.key.get_pressed()[pygame.K_SPACE]):


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
                        self.downsampledmap.append( x )
                        self.downsampledmap.append( y )
                        self.downsampledmap.append( depth )


        if( (self.ticks % self.setpointinterval) % self.soundtickinterval == 0 and self.soundtick < len(self.downsampled) ):


            soundindex = get_soundindex(self.downsampled[self.soundtick]);

            y = self.soundtick % (resy / self.yskip);
            x = int(self.soundtick / (resy / self.yskip));

            self.soundpoint = (x, y);


            x = x / ( (resx / self.xskip) - 1)
            x = 128 - int(x * 128);

            if(self.lastnote != None):
                offnote(self.lastnote, 128);


            dorepeat = int(self.soundtick / (resy / self.yskip)) > int( (self.soundtick-1) / (resy / self.yskip))
            if(dorepeat and self.repeated == False):
                self.repeated = True;
                drum(70, 30, x);
                self.soundtick -= 1;
            elif(soundindex != None):



                playnote( (40-soundindex)*2 + 25, int((40-soundindex)*2) + 20, x)
                self.lastnote = soundindex;
                self.repeated = False;
            elif(soundindex == None):
                #drum(50, 100, x);
                1;




            self.soundtick += 1;




        s = 16 * 20;

        pygame.draw.rect(surface, (0,255,0), pygame.Rect(0,0,s,int((resy/resx) * s)))


        for i in range(0, int(len(self.downsampledmap)/3)):

            w = (s / (resx / self.xskip));
            x = s - self.downsampledmap[i*3] / (resx / self.xskip) * s - w;
            y = self.downsampledmap[i*3 + 1] / (resx / self.xskip) * s;


            color = (self.downsampledmap[i*3 + 2] - mindistance) * 255 / (maxdistance)
            color = 255 - int(color);

            pygame.draw.rect(surface, (color,0,0), pygame.Rect(x,y,w,w));

        if(self.soundpoint != None):

            x = s - self.soundpoint[0] / (resx / self.xskip) * s - w;
            y = self.soundpoint[1] / (resx / self.xskip) * s;
            w = (s / (resx / self.xskip));

            pygame.draw.rect(surface, (255,255,255), pygame.Rect(x,y,w,w));



        self.ticks += 1;

clock = pygame.time.Clock();

surface = pygame.display.set_mode((400,300))

model = Model();


def render_text(string, fontsize, pos, col):
    text_surface = my_font.render(string, False, col)

    w = text_surface.get_width() * (fontsize / text_surface.get_height());

    text_surface = pygame.transform.scale(text_surface, (w, fontsize) );

    surface.blit(text_surface, pos)

while True:

    clock.tick(60)

    surface.fill( (0,0,0) );


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    print(clock.get_fps())

    model.draw();

    render_text("FPS: " + str(int(clock.get_fps())), 20, (20,250), (255,255,255));
    render_text("press space to go to next frame", 20, (20,270), (255,255,255));
    pygame.display.update()
