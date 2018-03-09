# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2018-03-09 21:18:38
# @modify date 2018-03-09 21:18:38
# @desc [hls分片]
import os
import random
import string


class hlsegment(object):
    def __init__(self):
        self.playlist = "playlist.m3u8"

    def segment(self, video, path):
        stream_name = os.path.splitext(video)[0]
        folder_name = ''.join(random.sample(
            string.ascii_letters + string.digits, 16))
        stream_folder = os.path.join(os.getcwd(), path, folder_name)
        stream_list = os.path.join(stream_folder, self.playlist)
        stream_cut = os.path.join(stream_folder, folder_name)
        stream_url = "/{}/{}/{}".format(path, folder_name, self.playlist)
        if not os.path.exists(stream_folder):
            os.mkdir(stream_folder)
        mp4_to_ts = "ffmpeg -y -i {input} -vcodec copy -acodec copy -vbsf h264_mp4toannexb {output}.ts".format(
            input=video, output=stream_name)
        ts_segment = "ffmpeg -i {input}.ts -c copy -map 0 -f segment -segment_list {m3u8} -segment_time 2 {output}_%04d.ts".format(
            input=stream_name, m3u8=stream_list, output=stream_cut)
        os.system(mp4_to_ts)
        os.system(ts_segment)
        os.remove(stream_name + ".ts")
        return stream_url
