#!/usr/bin/env python3

import moviepy.editor as mp
import tkinter as tk


def main():
    window = tk.Tk()
    window.title("Video Editor")
    window.geometry("400x400")
    window.mainloop()

    print("Starting the program")
    newvideo = mp.VideoFileClip("myvideo.mp4").subclip(50, 60)
    print("Video loaded")
    newvideo.write_videofile("myvideo2.mp4")
    print("Video saved")

    pass


if __name__ == "__main__":
    main()
