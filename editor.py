
import os
import sys
import random
import pygame
from moviepy.editor import *

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

moves = arm_setup(15)

# loading video dsa gfg intro video
clip1 = VideoFileClip("./media/alphamini_both_front.mp4")
clip2 = VideoFileClip("./media/alphamini_right_front.mp4")
clip3 = VideoFileClip("./media/alphamini_left_front.mp4")
 
clips = list()

for move in moves:
    if move == "right":
        clips.append(clip3)
    elif move == "left":
        clips.append(clip2)
    else:
        clips.append(clip1)

# concatenating both the clips
final = concatenate_videoclips(clips)
#writing the video into a file / saving the combined video
final.write_videofile("./merged.mp4")
