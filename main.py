import pyrealsense2 as rs
import pygame.midi
import pygame
import json
import sys

from drawnotes import NoteDrawer
from noteplayer import NotePlayer
from downsampled import GenerateDownsampled
from objectdownsampled import GenerateObjectDownsampled
from get_soundindex import get_soundindex
from get_boundingboxes import get_boundingboxes
from yolo import Yolo

pygame.init()
pygame.midi.init()
pygame.font.init()
pygame.mixer.init()

my_font = pygame.font.SysFont('Arial', 30)

pipeline = rs.pipeline()
config = rs.config()

resx = 640
resy = 480


config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
pc = rs.pointcloud()
pipeline.start(config)


soundsettings = None
soundfiles = {}

def loadsoundsettings():
    global soundsettings
    soundsettings = json.load(open("soundsettings.json"))

    if soundsettings["speakgrid"]:
        for classname in soundsettings["classes"]:
            soundfiles[classname] = pygame.mixer.Sound("./sounds/"+classname+".mp3")
loadsoundsettings()



class Model:

    def __init__(self):

        self.ticks = 0

        self.yolo_reader = Yolo()
        self.endsoundtick = 0
        self.soundtick= 0
        self.soundpoint = None
        self.ticklimiter = 0
        self.lastnote = None
        self.repeated = False

        self.xskip = 40
        self.yskip = 40

        self.sx = int(resx / self.xskip)
        self.sy = int(resy / self.yskip)

        self.generate_downsampled = GenerateDownsampled(self.xskip, self.yskip, resx, resy, soundsettings)
        self.generate_object_downsampled = GenerateObjectDownsampled(self.xskip, self.yskip, resx, resy)
        self.note_drawer = NoteDrawer(pygame, surface, 320, 240, self.sx, self.sy)
        self.note_player = NotePlayer(pygame)


    def draw(self):

        checkquit()

        if(self.ticks % soundsettings["setpointinterval"] == 0 or pygame.key.get_pressed()[pygame.K_SPACE]):

            loadsoundsettings()

            self.ticklimiter = 0
            self.soundtick= 0
            if(not soundsettings["notegrid"]): self.soundtick = 99999
            self.voicetick = 0
            if(not soundsettings["speakgrid"]): self.voicetick = 99999
            self.ticks = 0
            self.soundpoint = (0, 0)
            self.endsoundtick = 0

            self.downsampled = []
            self.downsampledmap = []

            self.objectdownsampled = []
            self.objectdownsampledmap = []

            frames = pipeline.wait_for_frames()
            self.depth_frame = frames.get_depth_frame()
            self.color_frame = frames.get_color_frame()
            self.downsampled, self.downsampledmap = self.generate_downsampled.generate(self.depth_frame, soundsettings["checkrange"], soundsettings["checkskip"])
            self.objectdownsampled, self.objectdownsampledmap = self.generate_object_downsampled.generate(get_boundingboxes(self.yolo_reader,self.color_frame))
            self.note_drawer.convert_image(self.color_frame, 320, 240)


        if( (self.ticks % soundsettings["setpointinterval"]) % soundsettings["soundtickinterval"] == 0 
           and self.soundtick < len(self.downsampled)
             and
        self.ticks % soundsettings["setpointinterval"] > self.ticklimiter):

            soundindex = get_soundindex(self.downsampled[self.soundtick], soundsettings)

            y = self.soundtick % self.sy
            x = int(self.soundtick / self.sy)

            self.soundpoint = (x, y)

            pan = x / ( self.sx - 1)
            pan = int(pan * 128)

            if(self.lastnote != None):
                self.note_player.offnote(self.lastnote, 0)

            dorepeat = int(self.soundtick / self.sy) > int( (self.soundtick-1) / self.sy)
            if(dorepeat and self.repeated == False):

                self.repeated = True
                self.note_player.drum(70, 80, pan)
                self.soundtick -= 1
                self.ticklimiter = self.ticks % soundsettings["setpointinterval"] + soundsettings["notecolumndelay"]

            elif(soundindex != None):

                pitch = soundsettings["startnote"] + soundindex * soundsettings["deltanote"]
                volume = soundsettings["startvolume"] + soundindex * soundsettings["deltavolume"]

                self.note_player.playnote( pitch, volume, pan)

                self.lastnote = pitch
                self.repeated = False

            elif(soundindex == None):

                self.note_player.drum(60, 50, pan)
                self.repeated = False

            self.soundtick += 1

            if(self.soundtick == len(self.downsampled)):
                self.endsoundtick = self.ticks % soundsettings["setpointinterval"]

        if(self.soundtick >= len(self.downsampled) and
           (self.ticks % soundsettings["setpointinterval"]) % soundsettings["speakingtickinterval"] == 0 and
           self.voicetick < len(self.objectdownsampled) and
           self.ticks % soundsettings["setpointinterval"] > self.endsoundtick + soundsettings["speakingaftergriddelay"] and
           self.ticks % soundsettings["setpointinterval"] > self.ticklimiter):

            self.soundtick  = 99999

            y = self.voicetick % self.sy
            x = int(self.voicetick / self.sy)

            self.soundpoint = (x, y)

            pan = x / ( self.sx - 1)
            pan = int(pan * 128)

            dorepeat = int(self.voicetick / self.sy) > int( (self.voicetick-1) / self.sy)
            if dorepeat and self.repeated == False:

                self.repeated = True
                self.note_player.drum(70, 80, pan)
                self.voicetick -= 1
                self.ticklimiter = self.ticks % soundsettings["setpointinterval"] + soundsettings["speakingcolumndelay"]

            elif self.objectdownsampled[self.voicetick] != 0:

                sound = soundfiles[self.objectdownsampled[self.voicetick]]
                sound.play()
                self.repeated = False
                self.ticklimiter = self.ticks % soundsettings["setpointinterval"] + soundsettings["speakingdelay"]

            else:
                self.note_player.drum(60, 20, pan)
                self.repeated = False

            self.voicetick += 1

        if self.soundtick <= len(self.downsampled):
            self.note_drawer.draw_notes(self.downsampledmap, soundsettings["maxdistance"], soundsettings["mindistance"], 0, 255, 20, 20)
        else:
            self.note_drawer.draw_objects(self.objectdownsampledmap, 20, 20)

        self.note_drawer.draw_image(360, 20)


        self.note_drawer.draw_soundpoint(self.soundpoint, 20, 20)

        self.ticks += 1

clock = pygame.time.Clock()
surface = pygame.display.set_mode((700,450))
model = Model()


def render_text(string, fontsize, pos, col):
    text_surface = my_font.render(string, False, col)

    w = text_surface.get_width() * (fontsize / text_surface.get_height())

    text_surface = pygame.transform.scale(text_surface, (w, fontsize) )

    surface.blit(text_surface, pos)

def checkquit():

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True
        elif event.type == pygame.QUIT:
            return True


while True:
    clock.tick(60)
    surface.fill((0,0,0))
    if(checkquit()):
        break
    model.draw()
    render_text("FPS: " + str(int(clock.get_fps())), 20, (20,270), (255,255,255))
    render_text("press space to go to next frame", 20, (20,290), (255,255,255))
    objectkeys = list(soundsettings.keys())
    render_text("Interval: " + str(model.ticks) + "/" + str(soundsettings["setpointinterval"]), 30, (20,315), (255,255,255))
    pygame.display.update()
sys.exit(1)
