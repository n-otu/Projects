"""
6.101 Lab 0:
Audio Processing
"""

import wave
import struct

# No additional imports allowed!


def backwards(sound):
    """
    Returns a new sound containing the samples of the original in reverse
    order, without modifying the input sound.

    Args:
        sound: a dictionary representing the original mono sound

    Returns:
        A new mono sound dictionary with the samples in reversed order
    """
    # reverse every list
    for val in sound.values():
        # specify list to ignore rate value
        # ask about why fixing type stops code from working
        if type(val) == list:
            # make a copy, ok that it's shallow because they're ints
            new_list = val.copy()
            new_list.reverse()
    # make a new dictionary with same key of og rate
    return {"rate": sound["rate"], "samples": new_list}


def mix(sound1, sound2, param):
    """Takes two sounds and a mixing parameter and mixes them together
    for a new sound with the same sampling rate."""

    # mix 2 good sounds
    if ("rate" in sound1 or sound2) is False or (
        sound1["rate"] == sound2["rate"]
    ) is False:
        print("no")
        return None

    rate = sound1["rate"]  # get rate
    sound1 = sound1["samples"]
    sound2 = sound2["samples"]
    if len(sound1) < len(sound2):
        leng = len(sound1)
    elif len(sound2) < len(sound1):
        leng = len(sound2)
    elif len(sound1) == len(sound2):
        leng = len(sound1)
    else:
        return None

    soun = []
    num = 0
    while num <= leng:
        sou2, sou1 = param * sound1[num], sound2[num] * (1 - param)
        soun.append(sou1 + sou2)  # add sounds
        num += 1
        if num == leng:  # end
            break

    return {"rate": rate, "samples": soun}  # return new sound


def echo(sound, num_echoes, delay, scale):
    """
    Compute a new signal consisting of several scaled-down and delayed versions
    of the input sound. Does not modify input sound.

    Args:
        sound: a dictionary representing the original mono sound
        num_echoes: int, the number of additional copies of the sound to add
        delay: float, the amount of seconds each echo should be delayed
    
            scale: float, the amount by which each echo's samples should be scaled

    Returns:
        A new mono sound dictionary resulting from applying the echo effect.
    """

    def combine_func(orig, new, sample_delay, roun):
        """Combine original samples with echos."""

        # add extra zeros for every new echo, WORKS FINE
        for zero in range(sample_delay):
            orig.append(0)

        # NOW COMBINE
        for numb in range(len(new)):
            orig[numb + sample_delay * roun] = orig[numb + sample_delay * roun] + new[numb]

        return orig

    # the number of samples each copy should be delayed by
    sample_delay = round(delay * sound["rate"])

    # first create new copy that doesn't affect original
    new_samples = []
    for inte in sound["samples"]:
        new_samples.append(inte)

    # for every new echo
    for numer in range(num_echoes):
        # create echo list of samples
        echos = []
        for num in sound["samples"]:
            # account for change in scale ^ power with every new echo
            echos.append(num * (scale ** (numer + 1)))
        # now combine each echo with the original sound
        new_samples = combine_func(new_samples, echos, sample_delay, numer + 1)

    new_sound = {"rate": sound["rate"], "samples": new_samples}

    return new_sound


def pan(sound):
    """Achieve panning spatial effect by adjusting samples in
    each channel separately. Returns a new sound dictionary"""

    # create new copies
    new_left = []
    new_right = []

    # get length of samples
    length = len(sound["right"])
    # print(length, 'LENGTH')

    for ind in range(len(sound["left"])):
        formula = 1 - (ind / (length - 1))
        new_left.append(sound["left"][ind] * formula)

    for inde in range(len(sound["right"])):
        formul = inde / (length - 1)
        new_right.append(sound["right"][inde] * formul)

    return {"rate": sound["rate"], "left": new_left, "right": new_right}


def remove_vocals(sound):
    """Removing vocals from sound."""

    # just get the difference at every index and add it to a new list
    mono = []
    for ind in range(len(sound["right"])):
        mono.append(sound["left"][ind] - sound["right"][ind])
    return {"rate": sound["rate"], "samples": mono}


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds


def load_wav(filename, stereo=False):
    """
    Load a file and return a sound dictionary.

    Args:
        filename: string ending in '.wav' representing the sound file
        stereo: bool, by default sound is loaded as mono, if True sound will
            have left and right stereo channels.

    Returns:
        A dictionary representing that sound.
    """
    sound_file = wave.open(filename, "r")
    chan, bd, sr, count, _, _ = sound_file.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    out = {"rate": sr}

    left = []
    right = []
    for i in range(count):
        frame = sound_file.readframes(1)
        if chan == 2:
            left.append(struct.unpack("<h", frame[:2])[0])
            right.append(struct.unpack("<h", frame[2:])[0])
        else:
            datum = struct.unpack("<h", frame)[0]
            left.append(datum)
            right.append(datum)

    if stereo:
        out["left"] = [i / (2**15) for i in left]
        out["right"] = [i / (2**15) for i in right]
    else:
        samples = [(ls + rs) / 2 for ls, rs in zip(left, right)]
        out["samples"] = [i / (2**15) for i in samples]

    return out


def write_wav(sound, filename):
    """
    Save sound to filename location in a WAV format.

    Args:
        sound: a mono or stereo sound dictionary
        filename: a string ending in .WAV representing the file location to
            save the sound in
    """
    outfile = wave.open(filename, "w")

    if "samples" in sound:
        # mono file
        outfile.setparams((1, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = [int(max(-1, min(1, v)) * (2**15 - 1)) for v in sound["samples"]]
    else:
        # stereo
        outfile.setparams((2, 2, sound["rate"], 0, "NONE", "not compressed"))
        out = []
        for l_val, r_val in zip(sound["left"], sound["right"]):
            l_val = int(max(-1, min(1, l_val)) * (2**15 - 1))
            r_val = int(max(-1, min(1, r_val)) * (2**15 - 1))
            out.append(l_val)
            out.append(r_val)

    outfile.writeframes(b"".join(struct.pack("<h", frame) for frame in out))
    outfile.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav("sounds/hello.wav")

    # write_wav(backwards(hello), "hello_reversed.wav")

    # dict_mys = load_wav('mystery.wav')
    # dict_mys_back = backwards(dict)
    # write_wav(dict_mys_back, 'mysterybackwards.wav')

    # water = load_wav('water.wav')
    # synth = load_wav('synth.wav')
    # water_synth = mix(water, synth, 0.2)
    # write_wav(water_synth, 'water_synth.wav')
    # print(round(0.4*8))
    # print(echo({
    #         'rate': 9,
    #         'samples': [1, 2, 3],
    #     }, 2, .6, .7))

    # load_chord = load_wav('chord.wav')
    # echoed_chord = echo(load_chord, 5, .3, .6)
    # write_wav(echoed_chord, 'echoed_chord.wav')
    # car = load_wav("car.wav", stereo=True)
    # car_pan = pan(car)
    # write_wav(car_pan, "car_pan.wav")
    # mountain = load_wav('lookout_mountain.wav', stereo=True)
    # clear_mountain = remove_vocals(mountain)
    # write_wav(clear_mountain, 'clear_mountain.wav')
