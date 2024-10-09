import threading
from pylsl import StreamInlet, resolve_stream
import time

class Recorder(threading.Thread):

    columns = ['Time',"FC1", "FC2", "C3", "C1", "C2", "C4", "CP1", "CP2", 'AccX', 'AccY', 'AccZ', 'Gyro1', 'Gyro2', 'Gyro3', 'Battery', 'Counter', 'Validation']
    data_dict = dict((k, []) for k in columns)
    
    def __init__(self, inlet, duration, fs = 250):
        super(Recorder,self).__init__()
        self.inlet = inlet
        self.duration = duration
        self.fs = fs

    def run(self):
        
        finished = False
        while not finished:

            data, timestamp = self.inlet.pull_sample()
            print("got %s at time %s" % (data[0], timestamp))
            #timestamp = datetime.fromtimestamp(psutil.boot_time() + timestamp)
            #The timestamp you get is the seconds since the computer was turned on,
            #so we add to the timestamp the date when the computer was started (psutil.boot_time())

            all_data = [timestamp] + data

            rep = 0
            for key in list(self.data_dict.keys()):
                self.data_dict[key].append(all_data[rep])
                rep = rep + 1
            
            if len(self.data_dict['Time']) >= self.fs*self.duration:
                finished = True

        return self.data_dict
    

streams = resolve_stream()

inlet = StreamInlet(streams[0])

duration = 1

session_recorder = Recorder(inlet,duration)

session_recorder.start()
print("alla vamos")
time.sleep(duration + 0.1)

data = session_recorder.data_dict
print("dict saved")