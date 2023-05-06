from pydub import AudioSegment
import pywinauto
import glob
import time
import struct
import math
import os
import wave
from scipy import fromstring, int16
import librosa

import soundfile as sf
import speech_recognition as sr
from pykakasi import kakasi

kakasi = kakasi()
kakasi.setMode('J', 'H') #漢字からひらがなに変換
kakasi.setMode("K", "H") #カタカナからひらがなに変換
conv = kakasi.getConverter()
# mp3ファイルの読み込み
def Cat(file,save_file):
    sound = AudioSegment.from_file(file, format=file.split(".")[-1])
    sound.export("tmp.wav", format="wav")

    y, sr = librosa.core.load("tmp.wav", sr=48000, mono=True) # 22050Hz、モノラルで読み込み
    sf.write("tmp.wav", y, sr, subtype="PCM_16") #16bitで書き込み

    # 音声ファイルのパスを指定する
    audio_file = AudioSegment.from_file("tmp.wav", format="wav")

    # 音声を一定時間ごとに分割する
    size = 200
    split_audio =list(audio_file[::size])

    # 音量が一定以上の部分を取得する
    threshold = -30
    start_trim = None 
    end_trim = 0
    end_point = 0
    count = 0
    end_flag = True
    while  end_flag:
        for i, chunk in enumerate(split_audio[end_point:],end_point):
            if chunk.dBFS > threshold:
                start_trim = i * size
                end_trim = None
                for j, chunk in enumerate(split_audio[i+1:],i + 1):
                    if chunk.dBFS < threshold:
                        end_trim =  (j+1) * size
                        end_point = j
                        break
                if end_trim == None:
                    end_trim = len(audio_file)
                print(i)
                print(j)
                print("--------")
                if j-i < 10:
                    break
                # 一定の音が鳴っている部分を切り出す
                if start_trim is None and end_trim is None:
                    trimmed_audio = audio_file
                else:
                    trimmed_audio = audio_file[start_trim:end_trim]

                # 切り出した音声を保存する
                trimmed_audio.export(save_file +"_" + str(count) + ".wav", format="wav")
                count =  count + 1
                break
            
            if i+1 >= len(split_audio):
                end_flag = False

def Rec(wav_folder):
    files = glob.glob(wav_folder + "/*.wav")
    r = sr.Recognizer()

    
    for file_ in files:
        print(file_)
        try:
            with sr.AudioFile(file_) as source:
                audio = r.record(source)
            
            text = r.recognize_google(audio, language='ja-JP')

            print(text)
            text = text.replace(" ", "")

            text = conv.do(text)
            print(text)
            f_w = open(file_.replace("wav", "txt"), 'w', encoding='utf-8')
            f_w.write(text)
            f_w.close()
        except:
            print("remove " + file_)
            os.remove(file_)
            pass
        time.sleep(2)


def main(file,wav_savefolder,text_savefolder):

    
    files = glob.glob(file)

    try:
        os.makedirs(wav_savefolder)
    except:
        pass
    try:
        os.makedirs(text_savefolder)
    except:
        pass
    for i,file in enumerate(files): 
        Cat(file,wav_savefolder + "/data" + str(i))
    Rec(wav_savefolder)
    
if __name__ == "__main__":
    main("F:/VRchat/ボイス/hiroyuki/*.mp3","./output/hiroyuki/wav","./output/hiroyuki/txt")
