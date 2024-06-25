import asyncio
import logging

import mini.mini_sdk as MiniSdk
from mini.apis import *
from mini.apis.api_action import PlayAction, PlayCustomAction
from mini.dns.dns_browser import WiFiDevice
from mini.apis.base_api import MiniApiResultType
from mini.apis import errors
from mini.apis.api_behavior import StartBehavior, ControlBehaviorResponse, StopBehavior
from mini.apis.api_expression import ControlMouthLamp, ControlMouthResponse
from mini.apis.api_expression import PlayExpression, PlayExpressionResponse
from mini.apis.api_expression import SetMouthLamp, SetMouthLampResponse, MouthLampColor, MouthLampMode
from mini.apis.base_api import MiniApiResultType
from mini.dns.dns_browser import WiFiDevice


# The default log level is Warning, set to INFO.
MiniSdk.set_log_level(logging.INFO)

async def test_connect(dev: WiFiDevice) -> bool:
    """Connect the device
    Connect the specified device
    Args:
        dev (WiFiDevice): Specified device object WiFiDevice
    Returns:
        bool: Whether the connection is successful
    """
    return await MiniSdk.connect(dev)

# Disconnect and release resources
async def shutdown():
    """Disconnect and release resources
    Disconnect the currently connected device and release resources
    """
    await MiniSdk.quit_program()
    await MiniSdk.release()

#Change the serial number for your Alpha Mini on the MiniSdk.get_device_by name ("s/n", 10)
async def test_get_device_by_name():
    """Search for devices based on the suffix of the robot serial number
    To search for the robot with the specified serial number (behind the robot's butt), you can just enter the tail character of the serial number, any length, it is recommended that more than 5 characters can be matched accurately, and the timeout is 10 seconds
    Returns:
        WiFiDevice: Contains robot name, ip, port and other information
    """
    result: WiFiDevice = await MiniSdk.get_device_by_name("00075", 10)
    print(f"test_get_device_by_name result:{result}")
    return result

async def test_start_run_program():
    """Enter programming mode 
    Make the robot enter the programming mode, wait for the response result, and delay 6 seconds, let the robot finish "Enter the programming mode"
    Returns:
        None:
    """
    await MiniSdk.enter_program()


# Test the eyes to make a face
async def test_play_expression():
    """Test play expressions

    Let the bot play a built-in emoticon called "codemao1" and wait for the reply results!

    #PlayExpressionResponse.isSuccess : Success or not

    #PlayExpressionResponse.resultCode : Return Code

    """
    block: PlayExpression = PlayExpression(express_name="codemao1")
    # response: PlayExpressionResponse
    (resultType, response) = await block.execute()

    print(f'test_play_expression result: {response}')


# Test, make the robot dance/stop dancing
async def test_control_behavior():
    """test control expressivity

    Ask the robot to start a dance called "dance_0004" and wait for the response.

    """
    # control_type: START, STOP
    block: StartBehavior = StartBehavior(name="face_001a")
    # response ControlBehaviorResponse
    (resultType, response) = await block.execute()

    print(f'test_control_behavior result: {response}')
    print(
        'resultCode = {0}, error = {1}'.format(response.resultCode, errors.get_express_error_str(response.resultCode)))


# Test, set the mouth light to green Always on
async def test_set_mouth_lamp():
    # mode: mouthlamp mode, 0: normal mode, 1: breath mode

    # color: mouth light color, 1: red, 2: green 

    # duration: duration in milliseconds, -1 means always on.

    # breath_duration: duration of a blink in milliseconds

    """Test Set Mouth Light

    Set the robot's mouth light to normal mode, green and always on for 3s, and wait for the reply result.

    When mode=NORMAL, the duration parameter works, indicating how long it will be always on.

    When mode=BREATH, the breath_duration parameter works, indicating how often to breathe

    #SetMouthLampResponse.isSuccess : Success or Not

    #SetMouthLampResponse.resultCode : return code

    """

    block: SetMouthLamp = SetMouthLamp(color=MouthLampColor.GREEN, mode=MouthLampMode.NORMAL,
                                       duration=3000, breath_duration=1000)
    # response:SetMouthLampResponse
    (resultType, response) = await block.execute()

    print(f'test_set_mouth_lamp result: {response}')


# Test, switch mouth light
async def test_control_mouth_lamp():
    """test_control_mouth_lamp

    Have the robot turn off its mouth light and wait for the results.

    #ControlMouthResponse.isSuccess : whether it succeeds or not

    #ControlMouthResponse.resultCode : return code

    """
    # is_open: True,False
    # response :ControlMouthResponse
    (resultType, response) = await ControlMouthLamp(is_open=False).execute()

    print(f'test_control_mouth_lamp result: {response}')

async def get_action_list() -> list:
    """Get action list

    Get the list of actions built into the robot system, and wait for the reply result

    Returns:
        []: Action list
    """
    from mini.apis.api_action import GetActionList
    from mini import RobotActionType
    block: GetActionList = GetActionList(True, RobotActionType.INNER)
    (resultType, response) = await block.execute()
    if resultType == MiniApiResultType.Success and response.isSuccess:
        return response.actionList
    else:
        return []
    
#PLAY ACTION
async def test_play_action(accion):
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
    block: PlayAction = PlayAction(action_name=accion) #derecho
    # response: PlayActionResponse
    (resultType, response) = await block.execute()

    print(f'test_play_action result:{response}')

async def test_play_action_2():
    """Execute an action demo

    Control the robot to perform a named local (built-in/custom) action and wait for a response from the result of the action

    The name of the action can be obtained from the GetActionList.

    #PlayActionResponse.isSuccess : whether it succeeds or not

    #PlayActionResponse.resultCode : Return Code

    """
    # action_name: Action file name, get action supported by robot via GetActionList.
    block: PlayAction = PlayAction(action_name='random_short4')
    # response: PlayActionResponse
    (resultType, response) = await block.execute()

    print(f'test_play_action_2 result:{response}')



async def test_play_action_3():
    """Execute an action demo

    Control the robot to perform a named local (built-in/custom) action and wait for a response from the result of the action

    The name of the action can be obtained from the GetActionList.

    #PlayActionResponse.isSuccess : whether it succeeds or not

    #PlayActionResponse.resultCode : Return Code

    """
    # action_name: Action file name, get action supported by robot via GetActionList.
    block: PlayAction = PlayAction(action_name='face_011')
    # response: PlayActionResponse
    (resultType, response) = await block.execute()

    print(f'test_play_action_3 result:{response}')




async def test_play_action_4():
    """Execute an action demo

    Control the robot to perform a named local (built-in/custom) action and wait for a response from the result of the action

    The name of the action can be obtained from the GetActionList.

    #PlayActionResponse.isSuccess : whether it succeeds or not

    #PlayActionResponse.resultCode : Return Code

    """
    # action_name: Action file name, get action supported by robot via GetActionList.
    block: PlayAction = PlayAction(action_name='face_015')
    # response: PlayActionResponse
    (resultType, response) = await block.execute()

    print(f'test_play_action_4 result:{response}')


async def get_custom_action_list() -> list:
    """Get a list of custom actions

    Get the action list under the robot/sdcard/customize/actions and wait for the reply result

    Returns:
        []: Custom action list
    """

    from mini.apis.api_action import GetActionList
    from mini import RobotActionType
    block: GetActionList = GetActionList(True, RobotActionType.INNER)
    (resultType, response) = await block.execute()
    if resultType == MiniApiResultType.Success and response.isSuccess:
        return response.actionList
    else:
        return []

if __name__ == '__main__':
    MiniSdk.set_robot_type(MiniSdk.RobotType.EDU)
    device: WiFiDevice = asyncio.get_event_loop().run_until_complete(test_get_device_by_name())
    if device:
        asyncio.get_event_loop().run_until_complete(test_connect(device))
        asyncio.get_event_loop().run_until_complete(test_start_run_program())
        asyncio.get_event_loop().run_until_complete(test_play_action())
        asyncio.get_event_loop().run_until_complete(test_play_action_2())
        asyncio.get_event_loop().run_until_complete(shutdown())