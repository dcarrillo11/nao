
import threading

class Recorder(threading.Thread):

    columns = ['Time','FC1','FC2','C3','C1','C2','C4','CP1','CP2']
    data_dict = dict((k, []) for k in columns)
    
    def __init__(self, duration = 10, fs = 250):
        super(Recorder,self).__init__()
        self.duration = duration
        self.fs = fs

        columns = ['Time','FC1','FC2','C3','C1','C2','C4','CP1','CP2']
        self.data_dict = dict((k, []) for k in columns)

    def run(self):
        
        finished = False
        while not finished:

            data = 11
            #print("got %s at time %s" % (data[0], timestamp))
            #timestamp = datetime.fromtimestamp(psutil.boot_time() + timestamp)
            #The timestamp you get is the seconds since the computer was turned on,
            #so we add to the timestamp the date when the computer was started (psutil.boot_time())

            for key in list(self.data_dict.keys()):
                self.data_dict[key].append(data)
            
            if len(self.data_dict['Time']) >= self.duration:
                finished = True

        return

objeto = Recorder()

print(objeto.data_dict)

objeto.start()

print(objeto.data_dict)

del objeto

objeto.start()

print(objeto.data_dict)