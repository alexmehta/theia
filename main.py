import math
import numpy as np
import pyrealsense2 as rs
import pygame.midi
import pygame
import time
import json

pygame.init();
pygame.midi.init()
pygame.font.init()
pygame.mixer.init();

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
#config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pc = rs.pointcloud()
pipeline.start(config)


soundsettings = None;
soundfiles = {};

def loadsoundsettings():
    global soundsettings;
    soundsettings = json.load(open("soundsettings.json"));

    if soundsettings["speakgrid"]:
        for classname in soundsettings["classes"]:
            soundfiles[classname] = pygame.mixer.Sound("./sounds/"+classname+".mp3");
loadsoundsettings();




print(soundsettings);


def get_soundindex(distance):

    if not (soundsettings["mindistance"] <= distance <= soundsettings["maxdistance"]): return None;

    return int( soundsettings["magnitude"] * ( (distance - soundsettings["mindistance"]) / (soundsettings["maxdistance"] - soundsettings["mindistance"]) )**soundsettings["smoothen"] )

def get_boundingboxes():
    return [[90,120,90,120, "dog"],[200,190,200,190, "person"],[300,50,300,50, "chair"]] #x1,y1,x2,y2


class Model:

    def __init__(self):

        self.ticks = 0;

        self.endsoundtick = 0;
        self.soundtick= 0;
        self.soundpoint = None;
        self.ticklimiter = 0;
        self.lastnote = None;
        self.repeated = False;

        self.thetamax = 45;

        self.xskip = 40;
        self.yskip = 40;

        self.downsampled = [];
        self.downsampledmap = [];

        self.objectdownsampled = [];
        self.objectdownsampledmap = [];

    def draw(self):

        if(self.ticks % soundsettings["setpointinterval"] == 0 or pygame.key.get_pressed()[pygame.K_SPACE]):


            print("Redraw");

            loadsoundsettings();

            self.ticklimiter = 0;
            self.soundtick= 0;
            self.voicetick = 0;
            self.ticks = 0;

            self.downsampled = [];
            self.downsampledmap = [];

            self.objectdownsampled = [];
            self.objectdownsampledmap = [];

            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            #color_frame = frames.get_color_frame()

            #color_image = np.asanyarray(color_frame.get_data())

            #pc.map_to(color_frame)

            points = np.asanyarray(depth_frame.get_data());

            for x in range(int(resx / self.xskip)-1, -1, -1):
                for y in range(0, int(resy / self.yskip)):
                    depth = depth_frame.get_distance(x * self.xskip, y * self.yskip);


                    foundinbound = False;

                    for j in range(-soundsettings["checkrange"],soundsettings["checkrange"]):

                        if foundinbound: break;

                        for k in range(-soundsettings["checkrange"],soundsettings["checkrange"]):

                            if foundinbound: break;

                            if x * self.xskip + j >= resx or x * self.xskip + j < 0: break;
                            if y * self.yskip + k >= resy or y * self.yskip + k < 0: break;

                            depth = depth_frame.get_distance(x * self.xskip + j, y * self.yskip + k);

                            inbound = get_soundindex(depth) != None;

                            if inbound:
                                self.downsampledmap.append( int(resx / self.xskip) - 1 - x )
                                self.downsampledmap.append( y )
                                self.downsampledmap.append( depth )
                                self.downsampled.append( depth );
                                foundinbound = True;

                    if not foundinbound: self.downsampled.append(0);

            for x in range(0, len(self.downsampled)):
                self.objectdownsampled.append(0);


            objects = get_boundingboxes();

            for object in objects:

                x = (object[0] + object[2])/2;
                y = (object[1] + object[3])/2;

                x = int(x / self.xskip);
                y = int(y / self.yskip);
                index = y + x * int(resy / self.yskip);

                self.objectdownsampled[index] = object[4];
                self.objectdownsampledmap.append(x);
                self.objectdownsampledmap.append(y);
                self.objectdownsampledmap.append(object[4]);



        if( (self.ticks % soundsettings["setpointinterval"]) % soundsettings["soundtickinterval"] == 0 and self.soundtick < len(self.downsampled) ):


            soundindex = get_soundindex(self.downsampled[self.soundtick]);

            y = self.soundtick % (resy / self.yskip);
            x = int(self.soundtick / (resy / self.yskip));

            self.soundpoint = (x, y);


            x = x / ( (resx / self.xskip) - 1)
            x = 128 - int(x * 128);

            if(self.lastnote != None):
                offnote(self.lastnote, 0);


            dorepeat = int(self.soundtick / (resy / self.yskip)) > int( (self.soundtick-1) / (resy / self.yskip))
            if(dorepeat and self.repeated == False):

                self.repeated = True;
                drum(70, 70, x);
                self.soundtick -= 1;

            elif(soundindex != None):

                pitch = soundsettings["startnote"] + soundindex * soundsettings["deltanote"]
                volume = soundsettings["startvolume"] + soundindex * soundsettings["deltavolume"];

                playnote( pitch, volume, x)

                self.lastnote = pitch;
                self.repeated = False;

            elif(soundindex == None):

                drum(60, 20, x);
                self.repeated = False;




            self.soundtick += 1;

            if(self.soundtick == len(self.downsampled)):
                self.endsoundtick = self.ticks % soundsettings["setpointinterval"]

        if(self.soundtick == len(self.downsampled) and
           (self.ticks % soundsettings["setpointinterval"]) % soundsettings["speakingtickinterval"] == 0 and
           self.voicetick < len(self.objectdownsampled) and
           self.ticks % soundsettings["setpointinterval"] > self.endsoundtick + soundsettings["speakingaftergriddelay"] and
           self.ticks % soundsettings["setpointinterval"] > self.ticklimiter):

            y = self.voicetick % (resy / self.yskip);
            x = int(self.voicetick / (resy / self.yskip));

            self.soundpoint = (x, y);


            x = x / ( (resx / self.xskip) - 1)
            x = 128 - int(x * 128);

            dorepeat = int(self.voicetick / (resy / self.yskip)) > int( (self.voicetick-1) / (resy / self.yskip))
            if(dorepeat and self.repeated == False):

                self.repeated = True;
                drum(70, 70, x);
                self.voicetick -= 1;

            elif(self.objectdownsampled[self.voicetick] != 0):

                print("play");

                sound = soundfiles[self.objectdownsampled[self.voicetick]];
                sound.play();
                self.repeated = False;
                self.ticklimiter = self.ticks % soundsettings["setpointinterval"] + soundsettings["speakingdelay"];

            else:

                drum(60, 20, x);
                self.repeated = False;




            self.voicetick += 1;





        s = 16 * 20;

        pygame.draw.rect(surface, (0,255,0), pygame.Rect(0,0,s,int((resy/resx) * s)))



        if(self.soundtick < len(self.downsampled)):
            for i in range(0, int(len(self.downsampledmap)/3)):

                w = (s / (resx / self.xskip));
                x = s - self.downsampledmap[i*3] / (resx / self.xskip) * s - w;
                y = self.downsampledmap[i*3 + 1] / (resx / self.xskip) * s;


                soundindex = get_soundindex(self.downsampledmap[i*3 + 2]);

                color = 255 - soundindex * (255 / soundsettings["magnitude"]);

                if(color < 0): color = 0;
                if(color > 255): color = 255;

                pygame.draw.rect(surface, (color,0,0), pygame.Rect(x,y,w,w));
        else:
            for i in range(0, int(len(self.objectdownsampledmap)/3)):

                w = (s / (resx / self.xskip));
                x = s - self.objectdownsampledmap[i*3] / (resx / self.xskip) * s - w;
                y = self.objectdownsampledmap[i*3 + 1] / (resx / self.xskip) * s;

                color = 255;

                pygame.draw.rect(surface, (color,0,0), pygame.Rect(x,y,w,w));

        if(self.soundpoint != None):

            w = (s / (resx / self.xskip));
            x = s - self.soundpoint[0] / (resx / self.xskip) * s - w;
            y = self.soundpoint[1] / (resx / self.xskip) * s;


            pygame.draw.rect(surface, (255,255,255), pygame.Rect(x,y,w,w));



        self.ticks += 1;

clock = pygame.time.Clock();
surface = pygame.display.set_mode((700,700))
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

    model.draw();

    render_text("FPS: " + str(int(clock.get_fps())), 20, (20,250), (255,255,255));
    render_text("press space to go to next frame", 20, (20,270), (255,255,255));

    objectkeys = list(soundsettings.keys());

    yk = 0;
    yp = 30;
    xk = 330;

    for key in objectkeys:
        render_text(key + ":" + str(soundsettings[key]), 30, (xk,yk), (255,255,255));
        yk += yp;


    render_text("Interval: " + str(model.ticks) + "/" + str(soundsettings["setpointinterval"]), 30, (xk,yk), (255,255,255));


    pygame.display.update()
