"""
Created on 24/01/2025

 this document contains basic 8bit sound effects

@author: Lennert
"""
# IMPORTS
# import winsound             # for annoying 8bit beep sounds
import time                 # for rests in music

# GLOBALS
sound_condition = True

initialize_sounds = True # when true packs setup_note_collection
octave_index = -1
note_index = -1
note_duration = 1

sound_testing = False

octaves = (0, 1, 2, 3, 4, 5, 6, 7, 8)

# notes Belgian notation (words)
C_gr_notes_words = ("do", "re", "mi", "fa", "sol", "la", "si")
notes_with_sharp_words = ("do", "do+", "re", "re+", "mi", "fa", "fa+", "sol", "sol+", "la", "la+", "si")
notes_with_flat_words = ("do", "re-", "re", "mi-", "mi", "fa", "sol-", "sol", "la-", "la", "si-", "si")

# » kruisen
sharp_notes_words = ("do+", "re+", "fa+", "sol+", "la+")
extra_sharp_notes_words = ("mi+", "si+")
# mi+ == fa
# si+ == do

sharp_tonality_tuple_words = ("fa+", "do+", "sol+", "re+", "la+", "mi+", "si+")


# » mollen
flat_notes_words = ()
extra_flat_notes_words = ()
# do- == si
# fa- == mi

flat_tonality_tuple_words = ("si-", "mi-", "la-", "re-", "sol-", "do-", "fa-")




# notes International notation (letters)
C_gr_notes_letters = ("c", "d", "e", "f", "g", "a", "b")
notes_with_sharp_letters = ("c", "c+", "d", "d+", "e", "f", "f+", "g", "g+", "a", "a+", "b")
notes_with_flat_letters = ("c", "d-", "d", "e-", "e", "f", "g-", "g", "a-", "a", "b-", "b")


# » sharp
sharp_notes_letters= ("c+", "d+", "f+", "g+", "a+")
extra_sharp_notes_letters = ("e+", "b+")
# e+ == f
# b+ == c

sharp_tonality_tuple_letters = ("a+", "c+", "g+", "d+", "a+", "e+", "b+")


# » flat
flat_notes_letters = ("d-", "e-", "g-", "a-", "b-")
extra_flat_notes_letters = ("c-", "f-")
# c- == b
# f- == e

flat_tonality_tuple_letters = ("b-", "e-", "a-", "d-", "g-", "c-", "f-")



#
# flat_tonality = int
#
# sharp_tonality = int


# temp until I understand python dictionaries
sound_dictionary = (
    # C     |   C+    |   D     |   D+    |   E     |   F     |   F+    |   G     |   G+    |   A  |   A+    |   B
    (16.35  , 17.32   , 18.35   , 19.45   , 20.6    , 21.83   , 23.12   , 24.5    , 25.96   , 27.5 , 29.17   , 30.87),   # 0
    (32.7   , 34.65   , 36.71   , 38.89   , 41.2    , 43.65   , 46.25   , 49      , 51.91   , 55   , 58.27   , 61.74),   # 1
    (65.41  , 69.3    , 73.42   , 77.78   , 82.41   , 87.31   , 92.5    , 98      , 103.83  , 110  , 116.54  , 123.47),  # 2
    (130.81 , 138.59  , 146.83  , 155.56  , 164.81  , 174.61  , 185     , 196     , 207.65  , 220  , 233.08  , 246.94),  # 3
    (261.63 , 261.63  , 293.66  , 311.13  , 329.63  , 349.23  , 369.99  , 392     , 415.3   , 440  , 466.16  , 493.88),  # 4
    (523.25 , 554.37  , 587.33  , 622.25  , 659.25  , 698.46  , 739.99  , 783.99  , 830.61  , 880  , 932.33  , 987.77),  # 5
    (1046.5 , 1108.75 , 1174.66 , 1244.51 , 1318.51 , 1396.91 , 1479.98 , 1567.98 , 1661.22 , 1760 , 1864.66 , 1975.53), # 6
    (2093   , 2217.46 , 2349.32 , 2489    , 2637    , 2793.83 , 2959.96 , 3135.96 , 3322.44 , 3520 , 3729.31 , 3951),    # 7
    (4186   , 4434.92 , 4698.63 , 4978    , 5274    , 5587.65 , 5919.91 , 6271.93 , 6644.88 , 7040 , 7458.62 , 7902.13)  # 8
)

def sound_bitsound(frequency: int = 2500, duration: int = 100):
    """
    plays a 8bit sound,
    Do not use long durations in gameplay, no long durations where smooth frame rate is important, only use long durations this in menus ....
    Beware that it will SLOW down the ENGINE very badly.

    :param frequency: the frequency of the sound

    :param duration: the duration of the sound, slows your engine down.

    :return: 8 Bit sound
    """
    if sound_condition:
        pass
        # winsound.Beep(frequency, duration)
    pass

def play_note(note: str, octave: int = 4, note_value: int or str = 1, bpm: int = 60, time_signature: tuple = (1, 1)):
    """
    let a note sound for a sertain time

    :param note: the name of the note you want to hear

    :param octave: the octave height of the note
    0 to 8, low to high

    :param note_value: the note_value, determens the lenght of a note

    :param bpm: beats per minute
    :param: time_signature: the time signature of the partiture tuple consists of 2 variables
    first input: amount of times 1 note value is in 1 single metre
    second input: the actual note value
    dutch translation for time signature is 'maatsoort'

    :return: a beep sound of your note, with the perfect timing
    """
    # GLOBALS
    global note_index, octave_index, note_duration

    # LOCALS
    note_collection = notes_with_sharp_letters
    note_letter = ""
    note_sign = "" # note is sharp / flat, will become: - or = or +

    # CONTROL
    note = note.lower().strip()
    # CHECKPOINT, make note so that if you build it up strictly correct as displayed, you don't have to full any other parameters in, because it is annoying

    # direction «» bpm
    # » duration per minute
    duration = (1 / bpm)
    # » duration per millisecond
    duration *= 60000
    # » rounding duration to avoid errors
    duration = round(duration, 0)
    # ¬ timing will not be exact, there is compression on it

    # note value
    if type(note_value) == int:
        if note_value == 0:
            print("error, note value cannot be 0")
        else: note_duration = 1 / note_value
    elif type(note_value) == str and note_value.endswith("."):
        # when . in total
        if note_value.count(".") == 1 and not bool(note_value.count(":")):
            note_duration = 1 / int(note_value[0]) * 1.5
        # when .. in total
        elif note_value.count(".") == 2:
            note_value.split(".")
            note_duration = 1 / int(note_value[0]) * 1.75
        # when : ==> .. in total, but split on :
        elif bool(note_value.count(":")):
            note_value.split(":")
            note_duration = 1 / int(note_value[0]) * 1.75
    else: note_duration = 1

    # final form of duration
    duration = duration * note_duration / (time_signature[0] / time_signature[1])

    # FUNCTIONS
    if not octave in octaves: print("error, invalid octave")

    # find the correct duration
    #
    # while octave_index != octave: # temp add here control to make sure that no error when user gives wrong input value
    #     octave_index += 1

    # TONE
    if note in ("do", "si+", "si#", "b+", "b#"):                       note = "c"
    if note in ("do+", "do#", "re-", "reb", "d-", "db"):               note = "c+"
    if note == "re":                                                   note = "d"
    if note in ("re+", "re#", "mi-", "mib", "e-", "eb"):               note = "d+"

    if note in ("mi", "fa-", "fab", "f-", "fb"):                       note = "e"
    if note in ("fa", "mi+", "mi#", "e+", "e#"):                       note = "f"
    if note in ("fa+", "fa#", "sol-", "solb", "f+", "f#", "g-", "gb"): note = "f+"
    if note == "sol":                                                  note = "g"

    if note in ("sol+", "sol#", "la-", "lab", "g+", "g#", "a-", "ab"): note = "g+"
    if note == "la":                                                   note = "a"
    if note in ("la+", "la#", "si-", "sib", "a+", "a#", "b-", "bb"):   note = "a+"
    if note in ("si", "do-", "dob", "c-", "cb"):                       note = "b"

    # after that, get note
    if note == "c":  note_index = 0
    if note == "c+": note_index = 1
    if note == "d":  note_index = 2
    if note == "d+": note_index = 3

    if note == "e":  note_index = 4
    if note == "f":  note_index = 5
    if note == "f+": note_index = 6
    if note == "g":  note_index = 7

    if note == "g+": note_index = 8
    if note == "a":  note_index = 9
    if note == "a+": note_index = 10
    if note == "b":  note_index = 11

    # sends annoying sound through your ear
    frequentie = int(round(sound_dictionary[octave][note_index]))
    pass
    # winsound.Beep(frequentie, int(round(duration, 0)))

def bitsound_note_test():
    """
    plays 'Broeder Jacob', for testing, I kept it, cause why not filling more memory space up
    If you ask, why this song, it is because there does not excist any other song that is as easy to code / play as this thing.

    :return: easy test music.
    """
    if sound_testing:
        tone_height = 5
        speed = 30
        signature = (4, 4)

        for index in range(2):
            # maat 1 & 2
            play_note("do", tone_height, 4, speed, signature)
            play_note("re", tone_height, 4, speed, signature)
            play_note("mi", tone_height, 4, speed, signature)
            play_note("do", tone_height, 4, speed, signature)

        for index in range(2):
            # maat 3 & 4
            play_note("mi", tone_height, 4, speed, signature)
            play_note("fa", tone_height, 4, speed, signature)
            play_note("sol", tone_height, 2, speed, signature)

        for index in range(2):
            # maat 5 & 6
            play_note("sol", tone_height, 8, speed, signature)
            play_note("la", tone_height, 8, speed, signature)
            play_note("sol", tone_height, 8, speed, signature)
            play_note("fa", tone_height, 8, speed, signature)
            play_note("mi", tone_height, 4, speed, signature)
            play_note("do", tone_height, 4, speed, signature)

        for index in range(2):
            # maat 7 & 8
            play_note("do", tone_height, 4, speed, signature)
            play_note("sol", 4, 4, speed, signature)
            play_note("do", tone_height, 2, speed, signature)

bitsound_note_test()