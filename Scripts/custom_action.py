#Librerías
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt 
import asyncio
import time
import logging
import mini.mini_sdk as MiniSdk
from mini.apis import *
from mini.apis.api_action import PlayCustomAction
from mini.dns.dns_browser import WiFiDevice
from mini.apis.base_api import MiniApiResultType
from mini.apis.api_behavior import StartBehavior, ControlBehaviorResponse, StopBehavior
from mini.apis.api_expression import ControlMouthLamp, ControlMouthResponse, PlayExpression, PlayExpressionResponse, SetMouthLamp, SetMouthLampResponse, MouthLampColor, MouthLampMode
from mini.apis.test_connect import test_connect, shutdown, test_get_device_by_name, test_play_action, get_action_list, get_custom_action_list
import random
import tkinter as tk
from datetime import date, datetime
import mne
from mne.channels import read_layout
from mne.time_frequency import psd_array_welch, tfr_multitaper
from mne.stats import permutation_cluster_1samp_test as pcluster_test
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from scipy import signal
from scipy.signal import butter, lfilter, lfilter_zi, iirnotch, freqz, filtfilt
import argparse
import psutil
import pyautogui
from pylsl import StreamInlet, resolve_stream
from pydub import AudioSegment
from pydub.playback import play

async def play_custom_action(accion):
    """Execute an action demo

    Control the robot to perform a named local (built-in/custom) action and wait for a response from the result of the action

    The name of the action can be obtained from the GetActionList.

    #PlayActionResponse.isSuccess : whether it succeeds or not

    #PlayActionResponse.resultCode : Return Code

    """
    #random_short3, random_short4
    #face_011, face_015
    #los dos brazos: 017, face_036, random_short5, hug_avatar
    # action_name: Action file name, get action supported by robot via GetActionList.
    block: PlayCustomAction = PlayCustomAction(action_name=accion) #derecho
    # response: PlayActionResponse
    (resultType, response) = await block.execute()

    print(f'test_play_action result:{response}')

MiniSdk.set_robot_type(MiniSdk.RobotType.EDU) #tipo de robot
#Encontrar robot (device) en la red WiFi:
device: WiFiDevice = asyncio.get_event_loop().run_until_complete(test_get_device_by_name())
if device: #Si lo encuentra, se conecta
    asyncio.get_event_loop().run_until_complete(test_connect(device))
    asyncio.get_event_loop().run_until_complete(play_custom_action('bothup'))
