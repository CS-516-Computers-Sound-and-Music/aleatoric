# Aleatoric
## Shane Drew

This project implements the core funcitonality of the assignment:
- Choose 1 of 3 random song structures: "AABB/CC", "ABAB/CD", "AB/CDDD".
- Choose 3 or 4 of 10 random line structures depending on the song structure chosen, where no line repeats between A, B, C or D: 
    - "I-IV-ii-V",
    - "I-vi-ii-V",
    - "I-iii-IV-iv",
    - "I-V-ii-V",
    - "I-vi-IV-V",
    - "IV-I-vi-IV",
    - "I-V-vi-I",
    - "I-IV-iv-I",
    - "IV-V-I-I",
    - "vi-IV-I-V"
- __Key:__ pick a major random key in [A3,A4]
- __Tempo:__ pick a random tempo in [80,160], with 4 beats per measure and 16 beats per line (common time)
- __Melody:__ Choose a random note from the chord described by the progression of each line w.p. 0.8, otherwise a random note (accidental) from the key. 
- __Performance:__ with the `--output <FILENAME.wav>` flag, the song is saved to FILENAME.wav. Otherwise, the performance is played outloud.

As well as some additional requirements:
- __Bass:__ With the `--bass` flag, the root note of the first chord is dropped 2 octaves and played throughout the measure as the bass note. 
- __Harmony:__ I created a few ways to break up the measure in `get_rhythm`, randomly permuted them, and then changed the duration of the respective note based on the ratio of its length to a quarter note. 


For this project, I created a series of helper methods, that approximately constitute a pipeline. One note that I have about my 'architecture' is that for some methods I do a decent job of splitting work into independent functions, like in `note_to_freq`, but other functions like `generate_sawtooth` became overload. Initially, I intended `generate_sawtooth` to only take in a note's semitone-offset from A4 and a duration and output the corresponding saw_tooth wave. As I augmented the code, this function became the easiest place to add harmony and bass. Another todo that would be a good way to refactor this code would be to move lines 207-227 into their own `make_song` function. 

