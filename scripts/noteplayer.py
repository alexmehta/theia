import pygame.midi

class NotePlayer():

    def __init__(self, pygame):

        self.muted = False;

        self.channel = pygame.mixer.Channel(0);
        self.channelchoice = 0;


        self.drumsounds = [];
        self.pianosounds = [];


        print("loading piano sounds");

        for i in range(0,127):
            self.drumsounds.append(pygame.mixer.Sound("./sounds/midi/drum/" + str(i) + ".mp3"))
            self.pianosounds.append(pygame.mixer.Sound("./sounds/midi/piano/" + str(i) + ".mp3"))

        print("note sounds loaded");

    def drum(self, pitch, volume, pan):

        if self.muted: return;

        vol1 = pan / 128;
        vol2 = 1 - pan / 128;

        vol1 *= volume / 100;
        vol2 *= volume / 100;

        self.channel.set_volume(vol2, vol1);
        self.channel.play(self.drumsounds[pitch])

        self.iteratechannel();

    def playnote(self, pitch, volume, pan):

        if self.muted: return;

        vol1 = pan / 128;
        vol2 = 1 - pan / 128;

        vol1 *= volume / 100;
        vol2 *= volume / 100;

        self.channel.set_volume(vol2, vol1);
        self.channel.play(self.pianosounds[pitch])

        self.iteratechannel();

    def offnote(self, pitch, volume):

        lastchannel = self.channelchoice - 1;
        if lastchannel < 0: lastchannel = 7;

        pygame.mixer.Channel(lastchannel).set_volume(0,0);
        pygame.mixer.Channel(lastchannel).stop();

    def playfile(self, file, volume, pan):

        if self.muted: return;

        vol1 = pan / 128;
        vol2 = 1 - pan / 128;

        vol1 *= volume / 100;
        vol2 *= volume / 100;

        self.channel.set_volume(vol2, vol1);
        self.channel.play(file)

        self.iteratechannel();

    def iteratechannel(self):

        self.channelchoice+=1;
        self.channelchoice = self.channelchoice % 8;
        self.channel = pygame.mixer.Channel(self.channelchoice);
