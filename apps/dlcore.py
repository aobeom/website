# -*- coding: UTF-8 -*-
# @author AoBeom
# @create date 2017-12-25 04:49:59
# @modify date 2018-01-29 12:07:42
# @desc [HLS downloader]
import binascii
import os
import re
import shutil
import subprocess
import sys
import time
from multiprocessing.dummy import Pool

import requests


class HLSVideo(object):
    def __init__(self):
        self.datename = time.strftime(
            '%y%m%d%H%M%S', time.localtime(time.time()))
        self.debug = False
        self.dec = 0
        self.type = ""

    # requests处理
    def __requests(self, url, headers=None, cookies=None, timeout=30):
        if headers:
            headers = headers
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36"
            }
        if cookies:
            response = requests.get(url, headers=headers,
                                    cookies=cookies, timeout=timeout)
        else:
            response = requests.get(url, headers=headers, timeout=timeout)
        return response

    # 错误处理 最多接收4个变量
    def __errorList(self, value, para1=None, para2=None, para3=None):
        infos = {
            "url_error": "Url is incorrect.",
            "key_error": "Wrong key. Please check url.",
            "total_error": "Video is not complete, please download again [Total: {} Present: {}]".format(para1, para2),
            "not_found": "Not Found {}.ts".format(para1),
            "dec_error": "Solve the problem, please run again [ hlsvideo -e {} -k {} ]".format(para1, para2),
        }
        available = "url_error, key_error, total_error"
        print infos.get(value, "Keyword: " + available)
        raw_input("Press Enter to exit.\r\n")
        sys.exit()

    # 检查外部应用程序
    def __execCheck(self, video_type):
        prog_openssl = subprocess.Popen(
            "openssl version", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        result_err = prog_openssl.stderr.read()
        if result_err:
            raw_input("openssl NOT FOUND.\r\n")
            sys.exit()

    # 检查是否地址合法性
    def __checkHost(self, types, url):
        if url.startswith("http"):
            hostdir = ""
        else:
            hostdir = raw_input("Enter %s: " % types)
            if hostdir.endswith("/"):
                hostdir = hostdir
            else:
                hostdir = hostdir + "/"
        return hostdir

    # 以当前时间创建文件夹
    def __isFolder(self, filename):
        try:
            filename = filename + "_" + self.datename
            propath = os.path.join(os.getcwd(), "media")
            video_path = os.path.join(propath, filename)
            if not os.path.exists(video_path):
                os.mkdir(video_path)
                return video_path
            else:
                return video_path
        except BaseException, e:
            raise e

    # 识别HLS的类型
    def hlsSite(self, playlist):
        type_dict = {
            "STchannel": "aka-bitis-hls-vod.uliza.jp",
        }
        # 通过关键字判断HLS的类型
        type_check = self.__requests(playlist).text
        for site, keyword in type_dict.items():
            if keyword in playlist:
                video_type = site
            if keyword in type_check:
                video_type = site
        try:
            video_type = video_type
        except BaseException:
            video_type = None
        self.type = video_type
        self.__execCheck(video_type)
        return playlist, video_type

    # 根据类型做不同的处理 下载key并提取video列表
    def hlsInfo(self, site):
        playlist = site[0]
        key_video = []
        # key的下载需要playlist的cookies
        response = self.__requests(playlist)
        m3u8_list_content = response.text
        cookies = response.cookies
        # 提取m3u8列表的最高分辨率的文件
        rule_m3u8 = r"^[\w\-\.\/\:\?\&\=\%]+"
        rule_px = r"RESOLUTION=[\w]+"
        # 根据分辨率匹配
        if "m3u8" in m3u8_list_content:
            m3u8urls = re.findall(
                rule_m3u8, m3u8_list_content, re.S | re.M)
            px_sel_num = len(m3u8urls)
            # 根据码率匹配
            if px_sel_num != 1:
                px_sels = re.findall(
                    rule_px, m3u8_list_content, re.S | re.M)
                px_sels = [p.split("=")[-1].replace("x", "").zfill(4) for p in px_sels]
                if len(px_sels) == 0:
                    rule_bd = r"BANDWIDTH=[\w]+"
                    bd_sels = re.findall(
                        rule_bd, m3u8_list_content, re.S | re.M)
                    bd_sels = [b.split("=")[-1].zfill(4) for b in bd_sels]
                    maxindex = bd_sels.index(max(bd_sels))
                else:
                    maxindex = px_sels.index(max(px_sels))
                m3u8kurl = m3u8urls[maxindex]
            else:
                m3u8kurl = ''.join(m3u8urls)

        m3u8host = self.__checkHost("m3u8 host", m3u8kurl)
        m3u8main = m3u8host + m3u8kurl
        m3u8_content = self.__requests(m3u8main).text

        # video host
        rule_video = r'[^#\S+][\w\/\-\.\:\?\&\=]+'
        videourl = re.findall(rule_video, m3u8_content, re.S | re.M)

        hostlist = m3u8main.split("/")[1:-1]
        videohost = m3u8main.split("/")[0] + "//"
        for parts in hostlist:
            if parts:
                videohost = videohost + parts + "/"

        # download key and save url
        rule_key = r'URI=\"(.*?)\"'
        keyurl = re.findall(rule_key, m3u8_content)

        if keyurl:
            # tv-asahi分片数由m3u8文件决定
            keyfolder = self.__isFolder("keys")
            keylist = []
            t = len(keyurl)
            print "(1)GET Key...[%s]" % t
            for i, k in enumerate(keyurl):
                # download key
                key_num = i + 1
                url = m3u8host + k
                # rename key
                keyname = str(key_num).zfill(4) + "_key"
                keypath = os.path.join(keyfolder, keyname)
                keylist.append(keypath)
                r = self.__requests(url, cookies=cookies)
                with open(keypath, "wb") as code:
                    for chunk in r.iter_content(chunk_size=1024):
                        code.write(chunk)
            if os.path.getsize(keypath) != 16:
                self.__errorList("key_error")
            key_video.append(keylist)
            # save urls
            videourls = [videohost + v.strip() for v in videourl]
            key_video.append(videourls)
        return key_video

    # 下载重试函数
    def __retry(self, urls, files):
        try:
            print "   Retrying..."
            r = self.__requests(urls)
            with open(files, "wb") as code:
                for chunk in r.iter_content(chunk_size=1024):
                    code.write(chunk)
        except BaseException:
            print "[%s] is failed." % urls

    # 下载处理函数
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

    # 下载函数
    def hlsDL(self, key_video):
        key_video = key_video
        # Check the number of keys
        key_path = [''.join(kv) for kv in key_video[0]]
        video_urls = key_video[1]
        videos = []  # 视频保存路径列表
        video_folder = self.__isFolder("encrypt")
        # Rename the video for sorting
        for i in range(0, len(video_urls)):
            video_num = i + 1
            video_name = str(video_num).zfill(4) + ".ts"
            video_encrypt = os.path.join(video_folder, video_name)
            videos.append(video_encrypt)
        total = len(video_urls)
        print "(2)GET Videos...[%s]" % total
        print "Please wait..."
        thread = total / 4
        # Multi-threaded configuration
        if thread > 100:
            thread = 20
        else:
            thread = 10
        pool = Pool(thread)
        pool.map(self.__download, zip(video_urls, videos))
        pool.close()
        pool.join()
        present = len(os.listdir(video_folder))
        # 比较总量和实际下载数
        if present != total:
            self.__errorList("total_error", total, present)
        # 有key则调用解密函数
        if key_path:
            key_path = ''.join(key_path)
            try:
                self.hlsDec(key_path, videos)
            except Exception as e:
                raise e

        # 后置处理 删除临时文件
        folder = os.path.join(os.getcwd(), "media", "decrypt_" + self.datename)
        video_name = os.path.join(folder, self.datename + ".ts")
        if os.path.exists(video_name):
            print "(3)Good!"
            print "(4)Please check [ {}.ts ]".format(self.datename)
            # 清理临时文件
            if not self.debug:
                enpath = os.path.join(os.getcwd(), "media", "encrypt_" + self.datename)
                kpath = os.path.join(os.getcwd(), "media", "keys_" + self.datename)
                os.chmod(folder, 128)
                os.chmod(enpath, 128)
                if os.path.exists(kpath):
                    os.chmod(kpath, 128)
                    shutil.rmtree(kpath)
                shutil.rmtree(enpath)
                shutil.copy(video_name, os.path.join(os.getcwd(), "media"))
                shutil.rmtree(folder)
        else:
            self.__errorList("not_fount", self.datename)
        return "/media/" + self.datename + ".ts"

    # 视频解密函数
    def hlsDec(self, keypath, videos, outname=None, ivs=None, videoin=None):
        if outname is None:
            outname = self.datename + ".ts"
        else:
            outname = outname
        videos = videos
        indexs = range(0, len(videos))
        # 判断iv值，为空则序列化视频下标，否则用给定的iv值
        if ivs is None:
            ivs = range(1, len(videos) + 1)
        else:
            ivs = ivs
        k = keypath
        # format key
        STkey = open(k, "rb").read()
        KEY = binascii.b2a_hex(STkey)
        if videoin:
            videoin = videoin
        else:
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
            command = "openssl aes-128-cbc -d -in " + inputVS + \
                " -out " + outputVS + " -nosalt -iv " + iv + " -K " + KEY
            os.system(command)
            new_videos.append(outputVS)
        self.hlsConcat(new_videos, outname)

    # 合并处理函数
    def __concat(self, ostype, inputv, outputv):
        if ostype == "linux":
            os.system("cat " + inputv + " >" + outputv)

    # 视频合并函数
    def hlsConcat(self, videolist, outname=None):
        if outname is None:
            outname = self.datename + ".ts"
        else:
            outname = outname
        videolist = videolist
        stream = ""
        # 解密视频路径
        video_folder = self.__isFolder("decrypt")
        videoput = os.path.join(video_folder, outname)
        for v in videolist:
            stream += v + " "
        videoin = stream[:-1]
        self.__concat("linux", videoin, videoput)


def main():
    playlist = raw_input("Enter Playlist URL: ")
    HLS = HLSVideo()
    site = HLS.hlsSite(playlist)
    keyvideo = HLS.hlsInfo(site)
    HLS.hlsDL(keyvideo)


if __name__ == "__main__":
    main()
