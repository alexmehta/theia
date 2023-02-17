from midiutil.MidiFile import MIDIFile
from midi2audio import FluidSynth
import os;

# create your MIDI object

path = "./sounds/midi/piano/"
instrument = 0;
pitchrange = [0,128];

for pitch in range(pitchrange[0], pitchrange[1]):
    
    mf = MIDIFile(1)     # only 1 track
    track = 0   # the only track
    time = 0    # start at the beginning

    mf.addProgramChange(0, 0, 0, instrument)
    mf.addTrackName(track, time, "Theia Sounds")
    mf.addTempo(track, time, 120)

    # add some notes
    channel = 0
    volume = 100

    time = 0             # start on beat 0
    duration = 1         # 1 beat long
    mf.addNote(track, channel, pitch, time, duration, volume)

    # write it to disk
    with open(path + "output.mid", 'wb') as outf:
        mf.writeFile(outf)

    FluidSynth().midi_to_audio(path + 'output.mid', path + str(pitch) + '.mp3')

os.remove(path + "output.mid")
