import pygame.midi

class NotePlayer():

    def __init__(self, pygame):
        pygame.midi.init()
        self.output = output = pygame.midi.Output(0)
        self.muted = False;

    def drum(self, pitch, volume, pan):

        if self.muted: return;

        self.output.write_short(192, 117)
        self.output.write_short(176, 10, pan)
        self.output.write_short(0x90, pitch, volume)
        self.output.write_short(192, 0)

    def playnote(self, pitch, volume, pan):

        if self.muted: return;

        self.output.write_short(176, 10, pan)
        self.output.write_short(0x90, pitch, volume)

    def offnote(self, pitch, volume):
        self.output.write_short(128, pitch, volume)
