
import os
import sys
import random
import pygame
from moviepy.editor import VideoFileClip, concatenate_videoclips
from tkinter import messagebox

def arm_setup(n_rep, random_order = True):
    movements = list()

    # Agregamos "izquierdo", "derecho" y "ambos" 
    for rep in range(n_rep):
        if rep < (n_rep/3):
            movements.append("left")
        elif rep >=(n_rep/3) and rep<((2*n_rep)/3):
            movements.append("right")
        else:
            movements.append("both")
    
    if random_order == True: # Mezclamos aleatoriamente la lista
        random.shuffle(movements)
    
    return movements

""" def clip_extender(input, output, time, duration):

    clip = VideoFileClip(input)

    freeze_frame = clip.to_ImageClip(time, duration = duration)

    new_clip = concatenate_videoclips([clip, freeze_frame])

    new_clip.write_videofile(output) """


def vrmaker(moves):
    # loading video dsa gfg intro video
    clip0 = VideoFileClip("./Media/Comienzo_detalle_vr.mp4",target_resolution=(2160,2160))
    clip1 = VideoFileClip("./Media/right_vr_injected.mp4")
    clip2 = VideoFileClip("./Media/left_vr_injected.mp4")
    clip3 = VideoFileClip("./Media/both_vr_injected.mp4")
    clip4 = VideoFileClip("./Media/Fin_vr.mp4", target_resolution=(2160,2160))

    clips = list()

    clips.append(clip0)
    clips.append(clip0.to_ImageClip(0, duration = 10))

    for move in moves:

        if move == "right":
            clips.append(clip1)
            clips.append(clip1.to_ImageClip(0, duration = 5))
        elif move == "left":
            clips.append(clip2)
            clips.append(clip3.to_ImageClip(0, duration = 5))
        else:
            clips.append(clip3)
            clips.append(clip3.to_ImageClip(0, duration = 5))

    clips.append(clip4)

    # concatenating the clips
    final = concatenate_videoclips(clips)
    #writing the video into a file / saving the combined video
    final.write_videofile("./Media/merged.mp4")

def main():
    pass

if __name__ == '__main__':
    moves = arm_setup(15)
    vrmaker(moves)

