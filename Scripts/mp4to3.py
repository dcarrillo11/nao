import moviepy.editor as mp

clip_path = "C:/Users/pc2/Proyecto_Alphamini/Audios/Comienzo.mp4"

clip = mp.VideoFileClip(clip_path)

clip.audio.write_audiofile("C:/Users/pc2/Proyecto_Alphamini/Audios/Comienzo.mp3")