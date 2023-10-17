import pydub.playback
from pydub import AudioSegment
import platform
import math

class SplitWavAudioMubin():
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + '/' + filename
        system_info = platform.version()
        if system_info.find('Darwin Kernel') != -1:
            pydub.AudioSegment.converter = '/opt/homebrew/bin/ffmpeg'
        else:
            pydub.AudioSegment.converter = '/usr/bin/ffmpeg'
        # self.audio = AudioSegment.from_mp3(self.filepath)
        self.audio = AudioSegment.from_file(self.filepath)
        self.split_files = []

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_min, to_min, split_filename):
        t1 = from_min * 60 * 1000
        t2 = to_min * 60 * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.folder + '/' + split_filename, format="mp3")

    def multiple_split(self, min_per_split):
        total_mins = math.ceil(self.get_duration() / 60)
        for i in range(0, total_mins, min_per_split):
            split_fn = str(i) + '_' + self.filename
            self.single_split(i, i + min_per_split, split_fn)
            self.split_files.append(split_fn)
            print(str(i) + ' Done')
            if i == total_mins - min_per_split:
                print('All splited successfully')