#!/usr/bin/env python3

import os
import json
from threading import Thread, Timer
import multiprocessing

import moviepy.editor as mp

import tkinter as tk
from tkinter import filedialog
from tkSliderWidget import Slider
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD

from playsound import playsound


class VideoEditor:
    def __init__(self):
        self.windowObjects = {}
        self.loadedVideo = None
        self.loadedVideoFileName = ""
        self.lastChangedValues = [0, 1]
        self.videoPlaying = False

    def handleFileSelect(self, event=None):
        file = self.selectFile()
        self.processSelectedFile(file)

    def selectFile(self):
        filetypes = (("MP4 files", "*.mp4"), ("All files", "*.*"))

        filename = filedialog.askopenfilename(
            title="Open a video file", initialdir="/", filetypes=filetypes
        )

        return filename

    def processSelectedFile(self, file):
        self.loadedVideoFileName = file
        loadedVideo = self.loadVideo(file)
        if loadedVideo is not None:
            values = self.windowObjects["lengthSlider"].getValues()
            self.handleSliderChange(values)
            self.windowObjects["videoName"].config(text=file)
            self.changeVideoFrame(values[0] * self.loadedVideo.duration)

    def changeVideoFrame(self, frameNumber):
        canvas = self.windowObjects["canvas"]
        self.windowObjects["videoCurrentDesc"].config(
            text="Video Current: " + "{:.2f}".format(frameNumber) + " s"
        )

        if self.loadedVideo is None:
            return

        videoFrame = self.loadedVideo.get_frame(frameNumber)
        img = Image.fromarray(videoFrame).resize((1280, 720))
        ph = ImageTk.PhotoImage(img)

        canvas.create_image(0, 0, image=ph, anchor=tk.NW)
        canvas.image = ph

    def saveVideo(self, config):
        if self.loadedVideo is None:
            print("No video loaded.")
            return

        volume = float(self.windowObjects["volumeTextBox"].get()) / 100
        length = self.windowObjects["lengthSlider"].getValues()

        realLength = [
            self.loadedVideo.duration * length[0],
            self.loadedVideo.duration * length[1],
        ]

        Thread(target=self.saveVideoThreaded, args=(config, volume, realLength)).start()

    def saveVideoThreaded(self, config, volume, length):
        newVideo = self.loadedVideo.subclip(length[0], length[1])
        newVideo = newVideo.volumex(volume)

        fileNameWithoutExtension = os.path.splitext(self.loadedVideoFileName)[0]
        newVideo.write_videofile(fileNameWithoutExtension + config["newFileName"])

    def loadVideo(self, filename):
        if filename == "":
            return None

        try:
            videoClip = mp.VideoFileClip(filename)
            return videoClip

        except Exception as e:
            print(e)
            return None

    def debounce(self, func, delay=0.05):
        def debounced(*args, **kwargs):
            debounced.timer = None

            def call_it():
                func(*args, **kwargs)

            if debounced.timer is not None:
                debounced.timer.cancel()
            debounced.timer = Timer(delay, call_it)
            debounced.timer.start()

        return debounced

    def handleSliderChange(self, values):
        if self.loadedVideo is None:
            return

        changeToStart = values[0] != self.lastChangedValues[0] or (values[0] == 0)

        videoStart = self.loadedVideo.duration * values[0]
        videoEnd = self.loadedVideo.duration * values[1]

        self.windowObjects["videoStartDesc"].config(
            text="Video Start: " + "{:.2f}".format(videoStart) + " s"
        )
        self.windowObjects["videoEndDesc"].config(
            text="Video End: " + "{:.2f}".format(videoEnd) + " s"
        )

        self.lastChangedValues = values

        if changeToStart:
            self.debounce(self.changeVideoFrame(videoStart))
        else:
            self.debounce(self.changeVideoFrame(videoEnd - 1))

    def playAudio(self, start, end):
        audio = self.loadedVideo.audio
        audio = audio.subclip(start, end)
        # play audio
        audio.write_audiofile("temp.mp3")

        return multiprocessing.Process(target=playsound, args=("temp.mp3",))

    def playVideo(self):
        if self.videoPlaying:
            return

        self.videoPlaying = True

        if self.loadedVideo is None:
            return

        videoStart = self.loadedVideo.duration * self.lastChangedValues[0]
        videoEnd = self.loadedVideo.duration * self.lastChangedValues[1]

        player = self.playAudio(videoStart, videoEnd)
        player.start()

        while videoStart < videoEnd:
            if not self.videoPlaying:
                player.terminate()
                break
            self.changeVideoFrame(videoStart)
            videoStart += 0.1

        os.remove("temp.mp3")

    def stopVideo(self):
        self.videoPlaying = False

    def createWindow(self, config):
        if config is None:
            print("Config is not defined. Exiting...")
            return

        window = TkinterDnD.Tk()
        window.title("Video Editor")
        window.geometry("1280x850")
        window.resizable(False, False)

        canvas = tk.Canvas(window, width=1280, height=720)
        canvas.bind("<Button-1>", self.handleFileSelect)  # on click
        canvas.drop_target_register(DND_FILES)
        canvas.dnd_bind(
            "<<Drop>>", lambda e: self.processSelectedFile(e.data)
        )  # on drag and drop
        canvas.create_text(640, 360, text="Click to select a video file")
        canvas.pack()
        self.windowObjects["canvas"] = canvas

        lengthSlider = Slider(window, 1280, 80, 0, 1, [0, 1], False)
        lengthSlider.setValueChageCallback(
            lambda values: self.handleSliderChange(values)
        )
        lengthSlider.pack()
        self.windowObjects["lengthSlider"] = lengthSlider

        canvas2 = tk.Canvas(window, width=1280, height=25)
        canvas2.pack()
        self.windowObjects["canvas2"] = canvas2

        volumeDesc = tk.Label(canvas2, text="Volume")
        volumeDesc.pack(side=tk.LEFT)
        self.windowObjects["volumeDesc"] = volumeDesc

        volumeTextBox = tk.Entry(canvas2)
        volumeTextBox.insert(0, config["volume"])
        volumeTextBox.pack(side=tk.LEFT)
        self.windowObjects["volumeTextBox"] = volumeTextBox

        videoName = tk.Label(canvas2, text="No video selected")
        videoName.pack(side=tk.LEFT)
        self.windowObjects["videoName"] = videoName

        playVideoThreaded = lambda: Thread(target=self.playVideo).start()
        videoPlayBtn = tk.Button(canvas2, text="Play Video", command=playVideoThreaded)
        videoPlayBtn.pack(side=tk.RIGHT)
        self.windowObjects["videoPlayBtn"] = videoPlayBtn

        stopVideoBtn = tk.Button(canvas2, text="Stop Video", command=self.stopVideo)
        stopVideoBtn.pack(side=tk.RIGHT)
        self.windowObjects["stopVideoBtn"] = stopVideoBtn

        saveVideoPartial = lambda: self.saveVideo(config)
        saveVideoButton = tk.Button(
            canvas2, text="Save Video", command=saveVideoPartial
        )
        saveVideoButton.pack(side=tk.RIGHT)
        self.windowObjects["saveVideoButton"] = saveVideoButton

        canvas3 = tk.Canvas(window, width=1280, height=25)
        canvas3.pack()
        self.windowObjects["canvas3"] = canvas3

        videoStartDesc = tk.Label(canvas3, text="Video Start: N/A")
        videoStartDesc.pack(side=tk.LEFT)
        self.windowObjects["videoStartDesc"] = videoStartDesc

        videoEndDesc = tk.Label(canvas3, text="Video End: N/A")
        videoEndDesc.pack(side=tk.LEFT)
        self.windowObjects["videoEndDesc"] = videoEndDesc

        videoCurrentDesc = tk.Label(canvas3, text="Video Current: N/A")
        videoCurrentDesc.pack(side=tk.LEFT)
        self.windowObjects["videoCurrentDesc"] = videoCurrentDesc

        return window

    def main(self):
        script_dir = os.path.abspath(os.path.dirname(__file__))
        config = json.load(open(os.path.join(script_dir, "config.json"), "r"))

        window = self.createWindow(config)
        window.mainloop()


if __name__ == "__main__":
    editor = VideoEditor()
    editor.main()
