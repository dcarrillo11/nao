def play_video(videopath):

    """ 
    #Function for video reescaling
    def rescale_frame(frame, percent):
        width = int(frame.shape[1] * percent/ 100)
        height = int(frame.shape[0] * percent/ 100)
        dim = (width, height)
        return cv.resize(frame, dim, interpolation =cv.INTER_AREA)
    """
    #Load the video
    video = cv.VideoCapture(videopath)
    audio = MediaPlayer(videopath)
    
    #Reproduce the video
    while True:
        ret,frame = video.read() #read a single frame 
        audio_frame, val = audio.get_frame()

        if not ret: #this mean it could not read the frame 
            print("End of video")   
            break
        if val != 'eof' and audio_frame is not None:
            img, t = audio_frame
        #frame = rescale_frame(frame, percent=60) #
        cv.namedWindow('imagen', cv.WND_PROP_FULLSCREEN)
        cv.setWindowProperty('imagen',cv.WND_PROP_FULLSCREEN,
                cv.WINDOW_FULLSCREEN) #Play the video on full-screen
        cv.imshow('imagen', frame)
       
        if cv.waitKey(1) & 0xFF == ord('q'): #Code for ESC key
            break
    

def play_video_2(videopath):

    videomaster = tk.Toplevel()
    #root.geometry("1280x720")
    videomaster.attributes('-fullscreen', True)

    videoplayer = TkinterVideo(master=videomaster, scaled=True)
    videoplayer.load(videopath)
    videoplayer.pack(expand=True, fill="both")

    """ vidcapture = cv.VideoCapture(videopath)
    fps = vidcapture.get(cv.CAP_PROP_FPS)
    totalNoFrames = vidcapture.get(cv.CAP_PROP_FRAME_COUNT)
    duration = int((totalNoFrames / fps) * 1000 + 1000) """

    videomaster.after(200000, videomaster.destroy)
    videoplayer.play() # play the video