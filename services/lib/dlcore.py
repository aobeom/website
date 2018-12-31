# -*- coding: UTF-8 -*-
# @author AoBeom
# @create date 2017-12-25 04:49:59
# @modify date 2018-12-31 10:57:44
# @desc [HLS downloader]
import binascii
import os
import sys
import re
import shutil
import time
from multiprocessing.dummy import Pool

import requests

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.dirname(os.path.split(curPath)[0])
sys.path.append(rootPath)

from modules.config import get_media_path_conf


class HLSVideo(object):
    def __init__(self):
        self.datename = time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))
        self.media_path = get_media_path_conf()["media_path"]
        if not os.path.exists(self.media_path):
            print("{} No Found".format(self.media_path))
            exit()
        self.save_uri = os.path.join(self.media_path, self.datename + ".ts")

    def __requests(self, url, cookies=None, timeout=30):
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.1; E6533 Build/32.4.A.0.160)"
        }
        if cookies:
            r = requests.get(url, headers=headers, cookies=cookies, timeout=timeout)
        else:
            r = requests.get(url, headers=headers, timeout=timeout)
        return r

    def __errorList(self, value, para1=None, para2=None):
        infos = {
            "key_error": "Wrong key. Please check url.",
            "total_error": "Video is not complete, please download again [Total: {} Present: {}]".format(para1, para2),
        }
        available = "key_error, total_error"
        print(infos.get(value, "Keyword: " + available))
        return False

    def __isFolder(self, filename):
        try:
            filename = filename + "_" + self.datename
            video_path = os.path.join(self.media_path, filename)
            if not os.path.exists(video_path):
                os.mkdir(video_path)
                return video_path
            else:
                return video_path
        except BaseException as e:
            raise e

    def hlsInfo(self, playlist):
        key_video = {}

        response = self.__requests(playlist)
        cookies = response.cookies
        m3u8_list = response.text

        rule_m3u8 = r"^[\w\-\.\/\:\?\&\=\%]+"
        rule_key = r'URI=\"(.*?)\"'
        rule_video = r'[^#\S+][\w\/\-\.\:\?\&\=]+'

        m3u8urls = re.findall(rule_m3u8, m3u8_list, re.S | re.M)
        m3u8url = ''.join(m3u8urls)
        m3u8_main = self.__requests(m3u8url).text
        keyurl = re.findall(rule_key, m3u8_main, re.S | re.M)
        vhost = '/'.join(m3u8url.split("/")[0:-1]) + "/"
        vurls = re.findall(rule_video, m3u8_main, re.S | re.M)

        keyfolder = self.__isFolder("keys")
        keynum = len(keyurl)
        # print("(1)GET KEY [{}]".format(keynum))
        keyname = str(keynum).zfill(4) + "_key"
        keypath = os.path.join(keyfolder, keyname)
        kurl = ''.join(keyurl)
        r = self.__requests(kurl, cookies=cookies)
        with open(keypath, "wb") as code:
            for chunk in r.iter_content(chunk_size=1024):
                code.write(chunk)
        if os.path.getsize(keypath) != 16:
            self.__errorList("key_error")
        videourls = [vhost + v.strip() for v in vurls]

        key_video["key"] = keypath
        key_video["urls"] = videourls
        return key_video

    def __retry(self, urls, files):
        try:
            # print("Retrying...")
            r = self.__requests(urls)
            with open(files, "wb") as code:
                for chunk in r.iter_content(chunk_size=1024):
                    code.write(chunk)
        except BaseException:
            print("[{}] is failed.".format(urls))

    def __download(self, para):
        urls = para[0]
        files = para[1]
        try:
            r = self.__requests(urls)
            with open(files, "wb") as code:
                for chunk in r.iter_content(chunk_size=1024):
                    code.write(chunk)
        except BaseException:
            self.__retry(urls, files)

    def hlsDL(self, key_video):
        key_path = key_video["key"]
        video_urls = key_video["urls"]
        videos = []
        video_folder = self.__isFolder("encrypt")
        for i in range(0, len(video_urls)):
            video_num = i + 1
            video_name = str(video_num).zfill(4) + ".ts"
            video_encrypt = os.path.join(video_folder, video_name)
            videos.append(video_encrypt)
        total = len(video_urls)
        # print("(2)GET Videos...[{}]".format(total))
        # print("Please wait...")
        thread = total / 4
        if thread > 20:
            thread = 8
        else:
            thread = 4
        pool = Pool(thread)
        pool.map(self.__download, zip(video_urls, videos))
        pool.close()
        pool.join()
        present = len(os.listdir(video_folder))

        if present != total:
            self.__errorList("total_error", total, present)

        self.hlsDec(key_path, videos)

        mediapath = self.media_path
        folder = os.path.join(mediapath, "decrypt_" + self.datename)
        video_name = os.path.join(folder, self.datename + ".ts")
        if os.path.exists(video_name):
            # print("(3)Please check [ {}.ts ]".format(self.datename))
            enpath = os.path.join(mediapath, "encrypt_" + self.datename)
            kpath = os.path.join(mediapath, "keys_" + self.datename)
            os.chmod(folder, 128)
            os.chmod(enpath, 128)
            if os.path.exists(kpath):
                os.chmod(kpath, 128)
                shutil.rmtree(kpath)
            shutil.rmtree(enpath)
            shutil.copy(video_name, mediapath)
            shutil.rmtree(folder)
        else:
            self.__errorList("not_fount", self.datename)
        return self.save_uri

    # 视频解密函数
    def hlsDec(self, keypath, videos):
        outname = self.datename + ".ts"
        videos = videos
        indexs = range(0, len(videos))
        ivs = range(1, len(videos) + 1)
        STkey = open(keypath, "rb").read()
        KEY = binascii.b2a_hex(STkey)
        KEY = str(KEY, encoding="utf-8")
        videoin = self.__isFolder("encrypt")
        videoout = self.__isFolder("decrypt")
        new_videos = []
        # Decrypt the video
        for index in indexs:
            inputV = videos[index]
            iv = ivs[index]
            outputV = videos[index].split("/")[-1] + "_dec.ts"
            iv = '%032x' % iv
            inputVS = os.path.join(videoin, inputV)
            outputVS = os.path.join(videoout, outputV)
            # 解密命令 核心命令
            command = "openssl aes-128-cbc -d -in " + inputVS + " -out " + outputVS + " -nosalt -iv " + iv + " -K " + KEY
            os.system(command)
            new_videos.append(outputVS)
        self.hlsConcat(new_videos, outname)

    def hlsConcat(self, videolist, outname):
        videolist = videolist
        stream = ""
        video_folder = self.__isFolder("decrypt")
        videoput = os.path.join(video_folder, outname)
        for v in videolist:
            stream += v + " "
        videoin = stream[:-1]
        command = "cat {} > {}".format(videoin, videoput)
        os.system(command)
