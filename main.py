import math
import numpy as np
import pyrealsense2 as rs
import pygame.midi
import pygame
import time
import json

pygame.midi.init()
pygame.init()
pygame.font.init()

my_font = pygame.font.SysFont('Comic Sans MS', 30)
output = pygame.midi.Output(0)

def drum(pitch, volume, pan):
    output.write_short(192, 117)
    output.write_short(176, 10, pan)
    output.write_short(0x90, pitch, volume)
    output.write_short(192, 0)

def playnote(pitch, volume, pan):

    output.write_short(176, 10, pan)
    output.write_short(0x90, pitch, volume)

def offnote(pitch, volume):
    output.write_short(128, pitch, volume)


pipeline = rs.pipeline()
config = rs.config()

resx = 640
resy = 480




config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
#config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pc = rs.pointcloud()
pipeline.start(config)

print(rs.stream.depth)

mindistance = 0.3
maxdistance = 5.3
magnitude = 30
smoothen = 0.8

startnote = 96
deltanote = -2

startvolume = 100
deltavolume = 0

soundsettings = None

def loadsoundsettings():
    global soundsettings
    soundsettings = json.load(open("soundsettings.json"))

loadsoundsettings()




print(soundsettings)


def get_soundindex(distance):

    if not (soundsettings["mindistance"] <= distance <= soundsettings["maxdistance"]): return None

    return int( soundsettings["magnitude"] * ( (distance - soundsettings["mindistance"]) / (soundsettings["maxdistance"] - soundsettings["mindistance"]) )**soundsettings["smoothen"] )




class Model:

    def __init__(self):

        self.ticks = 0

        self.soundtick= 0
        self.soundpoint = None
        self.lastnote = None
        self.repeated = False

        self.thetamax = 45

        self.xskip = 40
        self.yskip = 40

        self.downsampled = []

        self.downsampledmap = []

    def draw(self):

        if(self.ticks % soundsettings["setpointinterval"] == 0 or pygame.key.get_pressed()[pygame.K_SPACE]):


            print("Redraw")

            loadsoundsettings()

            self.soundtick= 0
            self.ticks = 0

            self.downsampled = []
            self.downsampledmap = []

            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            #color_frame = frames.get_color_frame()

            #color_image = np.asanyarray(color_frame.get_data())

            #pc.map_to(color_frame)

            points = np.asanyarray(depth_frame.get_data())

            for x in range(0, int(resx / self.xskip)):
                for y in range(0, int(resy / self.yskip)):
                    depth = depth_frame.get_distance(x * self.xskip, y * self.yskip)
                    self.downsampled.append( depth )


                    inbound = get_soundindex(depth) != None

                    if inbound:
                        self.downsampledmap.append( x )
                        self.downsampledmap.append( y )
                        self.downsampledmap.append( depth )


        if( (self.ticks % soundsettings["setpointinterval"]) % soundsettings["soundtickinterval"] == 0 and self.soundtick < len(self.downsampled) ):


            soundindex = get_soundindex(self.downsampled[self.soundtick])

            y = self.soundtick % (resy / self.yskip)
            x = int(self.soundtick / (resy / self.yskip))

            self.soundpoint = (x, y)


            x = x / ( (resx / self.xskip) - 1)
            x = 128 - int(x * 128)

            if(self.lastnote != None):
                offnote(self.lastnote, 0)


            dorepeat = int(self.soundtick / (resy / self.yskip)) > int( (self.soundtick-1) / (resy / self.yskip))
            if(dorepeat and self.repeated == False):

                self.repeated = True
                drum(70, 70, x)
                self.soundtick -= 1

            elif(soundindex != None):

                pitch = soundsettings["startnote"] + soundindex * soundsettings["deltanote"]
                volume = soundsettings["startvolume"] + soundindex * soundsettings["deltavolume"]

                playnote( pitch, volume, x)

                self.lastnote = pitch
                self.repeated = False

            elif(soundindex == None):

                drum(60, 20, x)
                self.repeated = False




            self.soundtick += 1




        s = 16 * 20

        pygame.draw.rect(surface, (0,255,0), pygame.Rect(0,0,s,int((resy/resx) * s)))


        for i in range(0, int(len(self.downsampledmap)/3)):

            w = (s / (resx / self.xskip))
            x = s - self.downsampledmap[i*3] / (resx / self.xskip) * s - w
            y = self.downsampledmap[i*3 + 1] / (resx / self.xskip) * s


            color = (self.downsampledmap[i*3 + 2] - mindistance) * 255 / (maxdistance)
            color = 255 - int(color)

            pygame.draw.rect(surface, (color,0,0), pygame.Rect(x,y,w,w))

        if(self.soundpoint != None):

            x = s - self.soundpoint[0] / (resx / self.xskip) * s - w
            y = self.soundpoint[1] / (resx / self.xskip) * s
            w = (s / (resx / self.xskip))

            pygame.draw.rect(surface, (255,255,255), pygame.Rect(x,y,w,w))



        self.ticks += 1

clock = pygame.time.Clock()
surface = pygame.display.set_mode((700,700))
model = Model()


def render_text(string, fontsize, pos, col):
    text_surface = my_font.render(string, False, col)

    w = text_surface.get_width() * (fontsize / text_surface.get_height())

    text_surface = pygame.transform.scale(text_surface, (w, fontsize) )

    surface.blit(text_surface, pos)

while True:

    clock.tick(60)

    surface.fill( (0,0,0) )


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    model.draw()

    render_text("FPS: " + str(int(clock.get_fps())), 20, (20,250), (255,255,255))
    render_text("press space to go to next frame", 20, (20,270), (255,255,255))

    objectkeys = list(soundsettings.keys())

    yk = 0
    yp = 30
    xk = 330

    for key in objectkeys:
        render_text(key + ":" + str(soundsettings[key]), 30, (xk,yk), (255,255,255))
        yk += yp


    render_text("Interval: " + str(model.ticks) + "/" + str(soundsettings["setpointinterval"]), 30, (xk,yk), (255,255,255))


    pygame.display.update()
