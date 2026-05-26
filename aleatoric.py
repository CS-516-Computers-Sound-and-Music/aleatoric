from scipy.io import wavfile as wf
from scipy import signal
import sounddevice
import numpy as np
import matplotlib.pyplot as plt

### PARAMS ###
tempo = np.random.randint(low=80, high=160+1)
note_duration = 60/tempo
sample_rate = 48000

volume = lambda x:x/2


def note_to_freq(semitones_away, base_note = 440):
    """ Get the frequency of a note given the number of 
    semitones it is away from the base tone (default: A4-440Hz)
    """
    return base_note* 2**(semitones_away/12)

def generate_sawtooth(note_semitones, root_chord = None, duration=note_duration):
    wave_width = 0.5
    frequency = note_to_freq(note_semitones)

    t = np.linspace(0,duration,int(duration*sample_rate)) #type:ignore
    
    sample = signal.sawtooth(2*np.pi*frequency*t, width=wave_width) #type:ignore

    if root_chord is not None:
        lo =  signal.sawtooth(2*np.pi*note_to_freq(root_chord[0])*t, width=wave_width) #type:ignore
        mid = signal.sawtooth(2*np.pi*note_to_freq(root_chord[1])*t, width=wave_width) #type:ignore
        hi =  signal.sawtooth(2*np.pi*note_to_freq(root_chord[2])*t, width=wave_width) #type:ignore

        sample = 0.6*sample + 0.2*lo + 0.1*mid + 0.1 * hi

    return sample


### LINE STRUCTURES ###

line_structures = [
        "I-IV-ii-V",
        "I-vi-ii-V",
        "I-iii-IV-iv",
        "I-V-ii-V",
        "I-vi-IV-V",
        "IV-I-vi-IV",
        "I-V-vi-I",
        "I-IV-iv-I",
        "IV-V-I-I",
        "vi-IV-I-V"
    ]

roman_map = {"i":1, "ii":2, "iii":3, 
             "iv":4, "v":5, "vi": 6}
def get_line_structure(key, force_struct = None):
    """ Given a key, return the four chords in the line structure in Hz
        minor chords are lowercase
        major chords are upper
    """
    minor_chord = np.array([0,3,7])
    major_chord = np.array([0,4,7])
    
    chord_progression_str = np.random.choice(line_structures) if force_struct is None else force_struct
    chord_progression = chord_progression_str.split("-")

    chords = [minor_chord + (key[roman_map[c.lower()]-1]) if c.islower() 
              else major_chord + (key[roman_map[c.lower()]-1])
              for c in chord_progression]
    
    return chords, chord_progression_str


### SONG STRUCTURES ###

song_structures = ["AABB/CC", "ABAB/CD", "AB/CDDD"]

def get_song_structure(key):
    song_structure = np.random.choice(song_structures)

    verse,refrain = song_structure.split('/')

    A,B,C,D = np.random.choice(line_structures,size=4,replace=False)
    line_dict = {"A":A,"B":B,"C":C,"D":D}
    
    verse_w_lines = [line_dict[line] for line in verse]
    refrain_w_lines = [line_dict[line] for line in refrain]

    return verse_w_lines, refrain_w_lines


### KEY ###

key_choices = ["A3","A3#","B3","C3","C3#","D3","D3#","E3","F3","F3#",'G3',"G3#",
               "A4","A4#","B4","C4","C4#","D4","D4#","E4","F4","F4#",'G4',"G4#",
               "A5","A5#","B5","C5","C5#","D5","D5#","E5","F5","F5#",'G5',"G5#"]

def get_key(force_key=None):
    """ return a random major key from A3-A4 inclusive 
        from A,A#,B,C,C#,D,D#,E,F,F#,G,G#,A
        since A4 is the overall reference, this will return
        each note will be represented as the number of 
        semitones it is down (or up maybe someday) from A4: [-12,0] inclusive
    """
    maj_key = np.array([0,2,2,1,2,2,2])

    # get a random home note, [-12,1) inclusive low end, exclusive high end
    key_note = np.random.randint(low=-12, high=1) if force_key is None else force_key
    scale = [key_note + np.sum(maj_key[:i+1]) for i in range(maj_key.shape[0])]
    return np.array(scale)

def give_em_the_edgar(wave):
    multipliers = np.linspace(0,1,10000)
    for i in range(10000):
        wave[-i] = wave[-i]*multipliers[-i]

    return wave


if __name__=="__main__":
    """"""
    key = get_key()
    print(f'In the key of {key_choices[key[0]+12]} (semitone: {key[0]})')

    verse, refrain = get_song_structure(key)

    verse_semitones = [get_line_structure(key, force_struct=line)[0] for line in verse]
    refrain_semitones = [get_line_structure(key, force_struct=line)[0] for line in refrain]

    all_semitones = np.concatenate((verse_semitones,refrain_semitones), axis=0)
    
    waves = []
    for line in all_semitones:
        root_chord = line[0]
        for chord in line:
            wave = generate_sawtooth(np.random.choice(chord), root_chord=root_chord)
            wave=give_em_the_edgar(wave)
            waves.append(wave)

    song=np.concatenate(waves).reshape(-1)
    sounddevice.play(volume(song), samplerate=sample_rate)
    sounddevice.wait()
