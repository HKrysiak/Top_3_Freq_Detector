
#Test
import pyaudio
import numpy as np
from numpy import zeros,linspace,short,fromstring,hstack,transpose,log, ndarray
from scipy import fft
from time import sleep
import time
import piplates.DAQC2plate as DAQC2

RANGE = 1 # +/- x Hz

global button_pressed
button_pressed=0
global which1
whcih1=[]
global top
top=[[0,0,0],[0,0,0],[0,0,0]]
freq=[[0,0,0],[0,0,0],[0,0,0]]
matched_freq=[0,0,0]

# Set up audio sampler -
NUM_SAMPLES = 6144
SAMPLING_RATE = 48000
pa = pyaudio.PyAudio()
_stream = pa.open(format=pyaudio.paInt16,
                  channels=1, rate=SAMPLING_RATE,
                  input=True,
                  frames_per_buffer=NUM_SAMPLES)

print("Frequency detector working. Press CTRL-C to quit.")


def get_audio(): #Initiates audio stream and stores top 3 frequencies to top[]
    for i in range (0,3):
        while _stream.get_read_available()< NUM_SAMPLES: sleep(0.005)
        audio_data  = fromstring(_stream.read(
             _stream.get_read_available(),exception_on_overflow=False), dtype=short)[-NUM_SAMPLES:]

        # Each data point is a signed 16 bit number, so we can normalize by dividing 32*1024
        normalized_data = audio_data / 32768.0
        global intensity
        intensity = abs(fft(normalized_data))[:NUM_SAMPLES/2]
        frequencies = linspace(0.0, float(SAMPLING_RATE)/2, num=NUM_SAMPLES/2)

        # use quadratic interpolation around the max
        global which1
        which1 = np.argpartition(intensity, -3)[-3:]
        which1.sort()
        #print "Top 3 in whcih pass: ",i, which1
        top[i]=[x for x in which1]
    #print "top", top
    return


def convert_freq(): #Converts top 3 frequencies from normalized values and stores in freq[]
    for i in range (0,3):
        for j in range (0,3):
            if top[i][j] != len(intensity)-1:
                y0,y1,y2 = log(intensity[top[i][j]-1:top[i][j]+2:])
                x1 = (y2 - y0) * .5 / (2 * y1 - y2 - y0)
                # find the frequency and output it
                freq[i][j]= (top[i][j]+x1)*SAMPLING_RATE/NUM_SAMPLES
            else:
                freq[i][j]= top[i][j]*SAMPLING_RATE/NUM_SAMPLES
    #print "freq:\n", freq
    return

def compare(): #Compares top 3 frequencies for 3 samples and prints as integers in matched_freq[]
    for i in range(0,3):
        if (freq[i][0] <= freq[i][1]+RANGE and freq[i][1] >= freq[i][1]-RANGE \
            and freq[i][2] <= freq[i][2]+RANGE and freq[i][2] >= freq[i][2]-RANGE):

            global matched_frequency
            matched_freq[i] = int(freq[0][i])
            #print "The natural frequencies are:  ", freq
            filename = time.strftime("%m_%d_%y")
            f=open(filename + "_Frequency_Data.txt", "a+")
            f.write("The natural frequencies are:  " % freq)
        else:
            print "Frequency didn't match for 3 consecutive recordings"
    print "Matching", matched_freq
    return

def button():
    if DAQC2.getDINbit(0,0) == 0:
        global button_pressed
        button_pressed = 1
        #print button_pressed
        print "Button Pressed"
        DAQC2.setDOUTbit(0,0)
        sleep(0.02)
        DAQC2.clrDOUTbit(0,0)
        sleep(0.2)
        return()

sleep(0.1)
run = None
while not run:
    button()
    if button_pressed == 1:
        get_audio()
        convert_freq()
        compare()
        button_pressed = 0
