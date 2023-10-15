#!/usr/bin/env python3

import moviepy.editor as mp
import tkinter as tk
from tkinter import filedialog
from tkSliderWidget import Slider
from PIL import Image, ImageTk

windowObjects = {}
loadedVideo = None


def handleFileSelect(event=None):
    global windowObjects, loadedVideo

    file = selectFile()
    loadedVideo = loadVideo(file)
    if loadedVideo is not None:
        windowObjects["videoName"].config(text=file)

        videoFrame = loadedVideo.get_frame(0)
        img = Image.fromarray(videoFrame).resize((1280, 720))
        ph = ImageTk.PhotoImage(img)

        windowObjects["canvas"].create_image(0, 0, image=ph, anchor=tk.NW)
        windowObjects["canvas"].image = ph


def selectFile():
    filetypes = (("MP4 files", "*.mp4"), ("All files", "*.*"))

    filename = filedialog.askopenfilename(
        title="Open a video file", initialdir="/", filetypes=filetypes
    )

    return filename


def saveVideo():
    pass


def loadVideo(filename):
    if filename == "":
        return None

    try:
        videoClip = mp.VideoFileClip(filename)
        return videoClip

    except Exception as e:
        print(e)
        return None


def createWindow():
    global windowObjects
    window = tk.Tk()
    window.title("Video Editor")
    window.geometry("1280x850")
    window.resizable(True, True)

    canvas = tk.Canvas(window, width=1280, height=720)
    canvas.bind("<Button-1>", handleFileSelect)  # on click
    canvas.create_text(640, 360, text="Click to select a video file")
    canvas.pack()
    windowObjects["canvas"] = canvas

    lengthSlider = Slider(window, 1280, 80, 0, 1, [0.2, 0.8], True)
    lengthSlider.pack()
    windowObjects["lengthSlider"] = lengthSlider

    canvas2 = tk.Canvas(window, width=1280, height=50)
    canvas2.pack()
    windowObjects["canvas2"] = canvas2

    volumeDesc = tk.Label(canvas2, text="Volume")
    volumeDesc.pack(side=tk.LEFT)
    windowObjects["volumeDesc"] = volumeDesc

    volumeTextBox = tk.Entry(canvas2)
    volumeTextBox.insert(0, "100")
    volumeTextBox.pack(side=tk.LEFT)
    windowObjects["volumeTextBox"] = volumeTextBox

    videoName = tk.Label(canvas2, text="No video selected")
    videoName.pack(side=tk.LEFT)
    windowObjects["videoName"] = videoName

    saveVideoButton = tk.Button(canvas2, text="Save Video", command=saveVideo)
    saveVideoButton.pack(side=tk.RIGHT)
    windowObjects["saveVideoButton"] = saveVideoButton

    return window


def main():
    window = createWindow()
    window.mainloop()

    """
    print("Starting the program")
    newvideo = mp.VideoFileClip("myvideo.mp4").subclip(50, 60)
    print("Video loaded")
    newvideo.write_videofile("myvideo2.mp4")
    print("Video saved")
    """


if __name__ == "__main__":
    main()
