from scipy.io import wavfile as wf
from scipy import signal
import sounddevice
import numpy as np
import matplotlib.pyplot as plt
import argparse

### PARAMS ###
tempo = np.random.randint(low=80, high=160+1)
note_duration = 60/tempo
sample_rate = 48000

### MAKING A WAVE ###

def note_to_freq(semitones_away, base_note = 440):
    """ Get the frequency of a note given the number of 
    semitones it is away from the base tone (default: A4-440Hz)
    """
    return base_note* 2**(semitones_away/12)

def generate_sawtooth(key,
                      chord_semitones, 
                      bass_root = None, 
                      duration=note_duration, 
                      add_harmony=False):
    wave_width = 0.9

    note_semitone = np.random.choice(chord_semitones)

    t = np.linspace(0,duration,int(duration*sample_rate)) #type:ignore
    
    # Generate a frequency from the chosen note_semitone in chord w.p. 0.8, else another accidental from they key
    frequency = note_to_freq(note_semitone if np.random.random()<=0.8 else np.random.choice(key))
    sample = signal.sawtooth(2*np.pi*frequency*t, width=wave_width) #type:ignore

    if add_harmony:
        melody_chord_index = np.where(chord_semitones == note_semitone)[0][0]
        if melody_chord_index == 0:
            harmony_semitone = chord_semitones[-1]-12
        else:
            harmony_semitone = chord_semitones[melody_chord_index-1]
        harmony =  signal.sawtooth(2*np.pi*note_to_freq(harmony_semitone)*t, width=wave_width) #type:ignore
        sample = 0.5*sample + 0.5*harmony


    if bass_root is not None:
        # Takes the bass note, drops it two octaves (-24 semitones)
        bass =  signal.sawtooth(2*np.pi*note_to_freq(bass_root-24)*t, width=0.5) #type:ignore

        sample = 0.4*sample + 0.6*bass

    return sample


### RHYTHM ###

def get_rhythm():
    # notes are tied to quarter notes, so rhythms will be scaled in terms of that
    rhythms = np.array([[1/4, 1/4, 1/4, 1/4], # normal, all quarter notes
            [1/2, 1/4, 1/8, 1/8],
            [3/4, 1/12, 1/12, 1/12],
            [1/3,1/3,1/6,1/6]
    ])
    rhythms = rhythms*4 # so that each fraction represents the fraction of a quarter note to use
    i,j = np.random.choice(range(len(rhythms)),2) # allowing them to be the same
    verse = np.random.permutation(rhythms[i])
    refrain = np.random.permutation(rhythms[j])
    return verse,refrain

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

    return verse_w_lines, refrain_w_lines, song_structure


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

### PLAYING THE SONG ###

volume = lambda x:x/2

def give_em_the_edgar(wave, fade_length=100):
    fade_in = np.linspace(0.0,1.0,fade_length)
    fade = np.linspace(1.0,0.0,fade_length)
    bowl = np.ones(wave.shape[0] - 2*fade_length)

    mask = np.concatenate((fade_in,bowl,fade))

    return wave * mask

### MAIN ###

def semitones_to_string(semitones):
    note_string = []
    for line in semitones:
        for s in line:
            diff = s[1]-s[0]
            note_string.append(f'{key_choices[s[0]+12]}{'Maj'if diff==4 else 'Min'}')
    return ", ".join(note_string)

def rhythm_to_string(rhythm):
    rhythm_string = []
    for note in rhythm:
        rhythm_string.append(f'{note/4:.2f}') # because everything just scales a quarter note
    return ", ".join(rhythm_string)

def main(save_file=None, add_bass=False, play_chord=False, add_harmony=False, modify_rhythm=False):
    key = get_key()
    print(f'In the key of {key_choices[key[0]+12]} (semitone: {key[0]})')

    verse, refrain, structure_string = get_song_structure(key)

    print(f'Song structure: {structure_string}')
    print(f'\tVerse:')
    for line in verse:
        print(f'\t\t{line}')
    print(f'\tRefrain:')
    for line in refrain:
        print(f'\t\t{line}')

    verse_semitones = [get_line_structure(key, force_struct=line)[0] for line in verse]
    refrain_semitones = [get_line_structure(key, force_struct=line)[0] for line in refrain]

    print(f'Melody:')
    print(f'\tVerse: {semitones_to_string(verse_semitones)}')
    print(f'\tRefrain: {semitones_to_string(refrain_semitones)}')

    print(f'Bass {"\u2713" if add_bass else 'X'}')
    print(f'Harmony {"\u2713" if add_harmony else 'X'}')
    print(f'Rhythm {"\u2713" if modify_rhythm else 'X'}')
    
    waves = []
    if modify_rhythm:
        verse_durations, ref_durations = get_rhythm()
    else:
        verse_durations, ref_durations = [1,1,1,1],[1,1,1,1]

    print(f'\nRhythm:')
    print(f'\tVerse: {rhythm_to_string(verse_durations)}')
    print(f'\tRefrain: {rhythm_to_string(ref_durations)}')

    for line in verse_semitones:
        bass_root = None if not add_bass else line[0][0]
        for chord,duration in zip(line,verse_durations):
            wave = generate_sawtooth(key, 
                                     chord, 
                                     bass_root=bass_root, 
                                     add_harmony=add_harmony,
                                     duration=duration*note_duration)
            wave=give_em_the_edgar(wave)
            waves.append(wave)

    for line in refrain_semitones:
        bass_root = None if not add_bass else line[0][0]
        for chord,duration in zip(line,ref_durations):
            wave = generate_sawtooth(key, 
                                     chord, 
                                     bass_root=bass_root, 
                                     add_harmony=add_harmony,
                                     duration=duration*note_duration)
            wave=give_em_the_edgar(wave)
            waves.append(wave)

    song=np.concatenate(waves).reshape(-1)
    song=np.concatenate([song,song])
    if save_file is None: 
        # Play the song out loud and do not save
        sounddevice.play(volume(song), samplerate=sample_rate)
        sounddevice.wait()
    else:
        # Save a .wav file under FILENAME.wav
        wf.write(save_file, sample_rate, song)


if __name__=="__main__":
    """"""
    parser = argparse.ArgumentParser(
                    prog='Aleotoric Music',
                    description='Generates a short aleatorically generated song',
                    epilog='Code by Shane :)')
    
    parser.add_argument('--bass', action='store_true', help="For each measure, play the chord root as a whole note two octaves lower. For example, if the chord is C the root is C4, so the bass would be C2")
    parser.add_argument('--harmony', action='store_true', help="For each melody note, also play the closest chord note below. For example, if the chord is C and the melody note is E4, also play C4.")
    parser.add_argument('--rhythm', action='store_true', help="Instead of eighth notes, pick a random note pattern for the verse, and another for the chorus. Use the same pattern for each line of the verse, and for each line of the chorus.")
    parser.add_argument('--drums', action='store_true', help="Add a drum track using white noise. Pick a one-measure rhythm, then use that for every measure in the song.")
    parser.add_argument('-o','--output', help="Instead of playing the song out loud, write the performance to FILENAME.wav as a WAV file: mono 48000sps 16-bit.")
    args = parser.parse_args()
    
    main(save_file = args.output, add_bass = args.bass, add_harmony=args.harmony, modify_rhythm=args.rhythm)
    
