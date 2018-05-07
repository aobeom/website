# -*- coding: utf-8 -*-
# @author AoBeom
# @create date 2018-03-09 21:18:38
# @modify date 2018-05-07 22:11:29
# @desc [hls分片]
import os
import random
import string


class hlsegment(object):
    def __init__(self):
        self.playlist = "playlist.m3u8"

    def segment(self, video, path):
        mainpath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        savepath = os.path.join(mainpath, path)
        # video2ts
        stream_ts = os.path.splitext(video)[0] + ".ts"
        mp4_to_ts = "ffmpeg -y -i {input} -vcodec copy -acodec copy -vbsf h264_mp4toannexb {output}".format(
            input=video, output=stream_ts)
        # hls cut
        hls_save_name = ''.join(random.sample(
            string.ascii_letters + string.digits, 16))
        hls_save_path = os.path.join(savepath, hls_save_name)
        if not os.path.exists(hls_save_path):
            os.mkdir(hls_save_path)
        hls_m3u8 = os.path.join(hls_save_path, self.playlist)
        hls_out_name = os.path.join(hls_save_path, hls_save_name)
        hls_url = "/{}/{}/{}".format(path, hls_save_name, self.playlist)
        ts_segment = "ffmpeg -i {input} -c copy -map 0 -f segment -segment_list {m3u8} -segment_time 2 {output}_%04d.ts".format(
            input=stream_ts, m3u8=hls_m3u8, output=hls_out_name)
        os.system(mp4_to_ts)
        os.system(ts_segment)
        os.remove(video)
        os.remove(stream_ts)
        return hls_url
