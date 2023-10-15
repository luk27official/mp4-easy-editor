#!/usr/bin/env python3

import moviepy.editor as mp
import tkinter as tk
from tkinter import filedialog
from tkSliderWidget import Slider
from PIL import Image, ImageTk
import json
import os
from threading import Thread, Timer

windowObjects = {}
loadedVideo = None
loadedVideoFileName = ""
lastChangedValues = [0, 0]


def handleFileSelect(event=None):
    global windowObjects, loadedVideo, loadedVideoFileName

    file = selectFile()
    loadedVideoFileName = file
    loadedVideo = loadVideo(file)
    if loadedVideo is not None:
        windowObjects["videoName"].config(text=file)

    changeVideoFrame(0)


def selectFile():
    filetypes = (("MP4 files", "*.mp4"), ("All files", "*.*"))

    filename = filedialog.askopenfilename(
        title="Open a video file", initialdir="/", filetypes=filetypes
    )

    return filename


def changeVideoFrame(frameNumber):
    global loadedVideo

    canvas = windowObjects["canvas"]

    if loadedVideo is None:
        return

    videoFrame = loadedVideo.get_frame(frameNumber)
    img = Image.fromarray(videoFrame).resize((1280, 720))
    ph = ImageTk.PhotoImage(img)

    canvas.delete("all")
    canvas.create_image(0, 0, image=ph, anchor=tk.NW)
    canvas.image = ph


def saveVideo(config):
    global loadedVideo

    if loadedVideo is None:
        print("No video loaded.")
        return

    volume = float(windowObjects["volumeTextBox"].get()) / 100
    length = windowObjects["lengthSlider"].getValues()

    print(volume)
    print(length)

    realLength = [loadedVideo.duration * length[0], loadedVideo.duration * length[1]]
    print(realLength)

    Thread(target=saveVideoThreaded, args=(config, volume, realLength)).start()


def saveVideoThreaded(config, volume, length):
    newVideo = loadedVideo.subclip(length[0], length[1])
    newVideo = newVideo.volumex(volume)

    fileNameWithoutExtension = os.path.splitext(loadedVideoFileName)[0]
    newVideo.write_videofile(fileNameWithoutExtension + config["newFileName"])


def loadVideo(filename):
    if filename == "":
        return None

    try:
        videoClip = mp.VideoFileClip(filename)
        return videoClip

    except Exception as e:
        print(e)
        return None


def debounce(func, delay=0.05):
    def debounced(*args, **kwargs):
        debounced.timer = None

        def call_it():
            func(*args, **kwargs)

        if debounced.timer is not None:
            debounced.timer.cancel()
        debounced.timer = Timer(delay, call_it)
        debounced.timer.start()

    return debounced


def handleSliderChange(values):
    global loadedVideo, lastChangedValues

    if loadedVideo is None:
        return

    if values == lastChangedValues:
        return

    changeToStart = values[0] < lastChangedValues[0]

    videoStart = loadedVideo.duration * values[0]
    videoEnd = loadedVideo.duration * values[1]

    windowObjects["videoStartDesc"].config(
        text="Video Start: " + "{:.2f}".format(videoStart) + " s"
    )
    windowObjects["videoEndDesc"].config(
        text="Video End: " + "{:.2f}".format(videoEnd) + " s"
    )

    print(values)

    lastChangedValues = values

    if changeToStart:
        debounce(changeVideoFrame(videoStart))
    else:
        debounce(changeVideoFrame(videoEnd))


def createWindow(config):
    global windowObjects

    if config is None:
        print("Config is not defined. Exiting...")
        return

    window = tk.Tk()
    window.title("Video Editor")
    window.geometry("1280x850")
    window.resizable(False, False)

    canvas = tk.Canvas(window, width=1280, height=720)
    canvas.bind("<Button-1>", handleFileSelect)  # on click
    canvas.create_text(640, 360, text="Click to select a video file")
    canvas.pack()
    windowObjects["canvas"] = canvas

    lengthSlider = Slider(window, 1280, 80, 0, 1, [0.2, 0.8], False)
    lengthSlider.setValueChageCallback(lambda values: handleSliderChange(values))
    lengthSlider.pack()
    windowObjects["lengthSlider"] = lengthSlider

    canvas2 = tk.Canvas(window, width=1280, height=25)
    canvas2.pack()
    windowObjects["canvas2"] = canvas2

    volumeDesc = tk.Label(canvas2, text="Volume")
    volumeDesc.pack(side=tk.LEFT)
    windowObjects["volumeDesc"] = volumeDesc

    volumeTextBox = tk.Entry(canvas2)
    volumeTextBox.insert(0, config["volume"])
    volumeTextBox.pack(side=tk.LEFT)
    windowObjects["volumeTextBox"] = volumeTextBox

    videoName = tk.Label(canvas2, text="No video selected")
    videoName.pack(side=tk.LEFT)
    windowObjects["videoName"] = videoName

    saveVideoPartial = lambda: saveVideo(config)
    saveVideoButton = tk.Button(canvas2, text="Save Video", command=saveVideoPartial)
    saveVideoButton.pack(side=tk.RIGHT)
    windowObjects["saveVideoButton"] = saveVideoButton

    canvas3 = tk.Canvas(window, width=1280, height=25)
    canvas3.pack()
    windowObjects["canvas3"] = canvas3

    videoStartDesc = tk.Label(canvas3, text="Video Start: N/A")
    videoStartDesc.pack(side=tk.LEFT)
    windowObjects["videoStartDesc"] = videoStartDesc

    videoEndDesc = tk.Label(canvas3, text="Video End: N/A")
    videoEndDesc.pack(side=tk.LEFT)
    windowObjects["videoEndDesc"] = videoEndDesc

    return window


def main():
    script_dir = os.path.abspath(os.path.dirname(__file__))
    config = json.load(open(os.path.join(script_dir, "config.json"), "r"))

    window = createWindow(config)
    window.mainloop()


if __name__ == "__main__":
    main()
