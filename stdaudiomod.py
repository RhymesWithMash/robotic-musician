"""
stdaudio.py

The stdaudio module defines functions related to audio.
"""

#-----------------------------------------------------------------------

import os
import sys
import numpy
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import matplotlib.pyplot as plt  # <-- added for waveform plotting
def plot_waveform(samples, fs=_SAMPLES_PER_SECOND, zoom_ms=10):
    """
    Plot the waveform of the given samples array.

    samples: list or ndarray of floats in range [-1.0, 1.0]
    fs: sample rate in Hz
    zoom_ms: how many milliseconds to show on the x-axis
    """
    y = numpy.array(samples)
    t = numpy.arange(len(y)) / float(fs)
    plt.figure()
    plt.plot(t, y)
    plt.xlim(0, zoom_ms / 1000.0)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title(f'Waveform ({zoom_ms} ms)')
    plt.show()
        plot_waveform(notes)         # <-- added: plot each note
        playSamples(notes)
    wait()

    stdio.writeln('Creating and playing in one large chunk...')
    sps = _SAMPLES_PER_SECOND
    notes = []
    inStream = instream.InStream('looney.txt')
    while not inStream.isEmpty():
        pitch = inStream.readInt()
        duration = inStream.readFloat()
        hz = 440 * math.pow(2, pitch / 12.0)
        N = int(sps * duration)
        for i in range(N+1):
            notes.append(math.sin(2*math.pi * i * hz / sps))
    plot_waveform(notes, zoom_ms=100)  # <-- added: plot the entire sequence (first 100 ms)
    playSamples(notes)
    wait()

    stdio.writeln('Saving...')
    save('looney', notes)

    stdio.writeln('Reading...')
    notes = read('looney')

    stdio.writeln('Playing an array...')
    playSamples(notes)
    wait()

    stdio.writeln('Playing a file...')
    playFile('looney')
    wait()

    os.remove('looney.wav')
    os.remove('looney.txt')

if __name__ == '__main__':
    _main()