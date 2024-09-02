import random
import collections
import contextlib
import functools
import math
import operator
import numpy as np
import time

from itertools import groupby

def arm_setup(n_rep):
    movements = list()

    # Agregamos "izquierdo", "derecho" y "ambos" 
    for rep in range(n_rep):
        if rep < (n_rep/3):
            movements.append("left")
        elif rep >=(n_rep/3) and rep<((2*n_rep)/3):
            movements.append("right")
        else:
            movements.append("both")
    
    while True:
        # Shuffle the list randomly
        random.shuffle(movements)

        # Check if the list meets the constraint of no more than two consecutive elements of the same type
        valid = True
        for i in range(len(movements) - 2):
            if movements[i] == movements[i+1] == movements[i+2]:
                valid = False
                break
        if valid:
            return movements

def main():

    start_time = time.time()
    movs = arm_setup(15)
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Generated List: {movs}")
    print(f"Execution Time: {execution_time} seconds")

if __name__ == '__main__':
    main()
