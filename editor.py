#!/usr/bin/env python3

import moviepy.editor as mp
import tkinter as tk
from tkinter import filedialog
from tkSliderWidget import Slider
from PIL import Image, ImageTk

windowObjects = {}


def handleFileSelect():
    global windowObjects

    file = selectFile()
    video = loadVideo(file)
    if video is not None:
        videoFrame = video.get_frame(0)
        img = Image.fromarray(videoFrame)
        img = img.resize((1000, 500))
        ph = ImageTk.PhotoImage(img)

        windowObjects["canvas"].create_image(0, 0, image=ph, anchor=tk.NW)
        windowObjects["canvas"].image = ph

        print(video)


def selectFile():
    filetypes = (("MP4 files", "*.mp4"), ("All files", "*.*"))

    filename = filedialog.askopenfilename(
        title="Open a video file", initialdir="/", filetypes=filetypes
    )

    return filename


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
    window.geometry("1280x720")

    fileSelect = tk.Button(window, text="Select File", command=handleFileSelect)
    fileSelect.pack()
    windowObjects["fileSelect"] = fileSelect

    canvas = tk.Canvas(window, width=1000, height=500)
    # color canvas
    canvas.pack()
    windowObjects["canvas"] = canvas

    lengthSlider = Slider(window, 1000, 80, 0, 100, [20, 80], True)
    lengthSlider.pack()
    windowObjects["lengthSlider"] = lengthSlider

    canvas2 = tk.Canvas(window, width=1000, height=200)
    canvas2.pack()
    windowObjects["canvas2"] = canvas2

    volumeDesc = tk.Label(canvas2, text="Volume")
    volumeDesc.pack()
    windowObjects["volumeDesc"] = volumeDesc

    volumeTextBox = tk.Entry(canvas2)
    volumeTextBox.insert(0, "100")
    volumeTextBox.pack()
    windowObjects["volumeTextBox"] = volumeTextBox

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
