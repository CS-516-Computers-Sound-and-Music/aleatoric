from scipy.io import wavfile as wf
import sounddevice
import numpy as np
import matplotlib.pyplot as plt

song_structures = [
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

def note_to_freq(semitones_away, base_note = 440):
    """ Get the frequency of a note given the number of 
    semitones it is away from the base tone (default: A4-440Hz)
    """
    return base_note* 2**(semitones_away/12)

roman_map = {"i":1, "ii":2, "iii":3, 
             "iv":4, "v":5, "vi": 6}
def get_song_structure(key):
    """ Given a key, return the four chords in the song structure in Hz
        minor chords are lowercase
        major chords are upper
    """
    minor_chord = np.array([0,3,7])
    major_chord = np.array([0,4,7])
    
    chord_progression = np.random.choice(song_structures).split("-")
    chords = [minor_chord + key[roman_map[c.lower()]] if c.islower() 
              else major_chord + key[roman_map[c.lower()]]
              for c in chord_progression]
    
    return chords



def get_key():
    """ return a random major key from A3-A4 inclusive 
        from A,A#,B,C,C#,D,D#,E,F,F#,G,G#,A
        since A4 is the overall reference, this will return
        each note will be represented as the number of 
        semitones it is down (or up maybe someday) from A4: [-12,0] inclusive
    """
    maj_key = np.array([0,2,2,1,2,2,2])

    # get a random home note, [-12,1) inclusive low end, exclusive high end
    key_note = np.random.randint(low=-12, high=1)
    scale = [key_note + np.sum(maj_key[:i+1]) for i in range(maj_key.shape[0])]
    return np.array(scale)


def main():
    """Sine Wave
        Channels per frame: 1 (mono)
        Sample format: 16 bit signed (values in the range -32767..32767)
        Amplitude: ¼ maximum possible 16-bit amplitude (values in the range -8192..8192)
        Duration: one second
        Frequency: 440Hz (440 cycles per second)
        Sample Rate: 48000 samples per second
    """
    amplitude = 8192
    frequency = 440
    sample_rate = 48000

    sin_x = np.linspace(0,1,sample_rate)
    sin_y = amplitude * np.sin(2*np.pi*frequency*sin_x)

    # save to sine.wav
    
    wf.write("sine.wav", sample_rate, sin_y)

    # note: worst sound I've ever heard, so loud
    """
    Fixing loudness on replay: dividing the entire thing by a constant (large to make it a lot less loud)
    The raw sound was blowing out my speakers, so it didn't even sound like middle A (much higher than)
    The volumne control of 100 000 sounds like A and doesn't hurt

    So, what I've found is that, even through quicktime, the amplitude bypasses my computer's volume 
    controls.
    """
    vol_control = 10000 # much better
    sounddevice.play(sin_y/vol_control, samplerate=sample_rate)
    sounddevice.wait()
    
    """Clipped Sine Wave
    half amplitude wave clipped at +/- 8192
    """
    max_amp = 8192

    clipped_y = sin_y*2
    clipped_y[clipped_y>max_amp] = max_amp
    clipped_y[clipped_y<-max_amp] = -max_amp

    # write to clipped.wav
    wf.write("clipped.wav", sample_rate, clipped_y)

    # play it back
    sounddevice.play(clipped_y/vol_control, samplerate=sample_rate)
    sounddevice.wait()


    # Show the two waves
    stop = 200
    plt.plot(sin_x[:stop], sin_y[:stop], label='Sine Wave')
    plt.plot(sin_x[:stop], sin_y[:stop]*2, c='orange',linestyle='dashed')
    plt.plot(sin_x[:stop], clipped_y[:stop], c='orange', label='Clipped Sine Wave')

    plt.title(f"{frequency}Hz Sine Waves")
    plt.legend()
    plt.show()

if __name__=="__main__":
    """"""
    key = get_key()
    print(key)
    print(get_song_structure(key))
