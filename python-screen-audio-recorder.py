from PIL import ImageGrab
import numpy as np
import cv2
from win32api import GetSystemMetrics
import PySimpleGUI as sg
import pyaudio
import wave
import ffmpeg
import time

chunk = 10240
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record at 44100 samples per second
p = pyaudio.PyAudio()  # Create an interface to PortAudio
stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)
audioFrames = []  # Initialize array to store frames

width = GetSystemMetrics(0)
height = GetSystemMetrics(1)

def mergeFiles():
    video_stream = ffmpeg.input('output/temp_video.avi')
    audio_stream = ffmpeg.input('output/temp_audio.wav')
    ffmpeg.output(audio_stream, video_stream, 'output/final.mp4').run(overwrite_output=True, cmd=r'C:\FFmpeg\bin\ffmpeg.exe')

def main():

    sg.theme('DarkBrown1')

    layout = [
        [sg.Text("Screen Recorder")],
        [sg.Text(size=(10, 1), font=('Helvetica', 18), justification='center', key='-OUTPUT-')],
        [sg.Button("Start/Stop", focus=True), sg.Button("Exit")]
    ]

    window = sg.Window("Demo", layout, location=(width-275,height-200), grab_anywhere=True,
                       keep_on_top=True, font='_ 18', no_titlebar=True, element_justification='c')

    counter = 0

    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')

    recording = False
    print('Program Started')

    while True:
        event, values = window.read(timeout=10)

        if event == sg.WIN_CLOSED or event == 'Exit':
            #recording = False
            print('Exiting..')
            return
        elif event == 'Start/Stop':
            if recording:
                print('Recording Stopped')
                recording = False

                # Stop and close the stream
                stream.stop_stream()
                stream.close()
                # Terminate the PortAudio interface
                p.terminate()

                # Save the recorded data as a WAV file
                wf = wave.open('output/temp_audio.wav', 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(sample_format))
                wf.setframerate(fs)
                wf.writeframes(b''.join(audioFrames))
                wf.close()

                time.sleep(3)

                mergeFiles()

            else:
                print('Recording Started')
                recording = True
                outputVideo = cv2.VideoWriter('output/temp_video.avi', fourcc, 10, (width, height))

        if recording:
            data = stream.read(chunk)
            audioFrames.append(data)

            window['-OUTPUT-'].update(
                '{:02d}:{:02d}.{:02d}'.format((counter // 100) // 60, (counter // 100) % 60, counter % 100, (counter % 100) % 100))
            counter += 1

            srcSettings = ImageGrab.grab('', True, False, None)
            settingsArray = np.array(srcSettings)
            frame = cv2.cvtColor(settingsArray, cv2.COLOR_BGR2RGB)
            outputVideo.write(frame)
            cv2.waitKey(20)

    outputVideo.release()
    cv2.destroyAllWindows()
main()
