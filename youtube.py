import subprocess
import time
import os
import urllib
import urllib.request
import yt_dlp

# 添加代理
os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# 添加 yt-dlp 路径
os.environ["PATH"] += os.pathsep + os.path.dirname(os.path.abspath(__file__)) + "/yt-dlp"
# 添加 ffmpeg 路径
ffmpeg_path = os.path.dirname(os.path.abspath(__file__)) + "/ffmpeg"
os.environ["PATH"] += os.pathsep + ffmpeg_path

#视频链接txt路径
PATH = os.path.dirname(os.path.abspath(__file__)) + "/url.txt"

#视频和封面保存路径
DOWNLOAD_PATH = os.path.dirname(os.path.abspath(__file__)) + "/download/"

#查询视频信息
COMMAND_PREFIX_CHECK = 'yt-dlp -F'

#下载1080p视频，并替换title中的空格
COMMAND_PREFIX_DOWNLOAD = 'yt-dlp -o "{}%(title)s.%(ext)s" --restrict-filenames -f 22 --merge-output-format mp4 --write-auto-sub --sub-langs=zh-Hans,en '

#获取视频标题（空格会被替换成_）
COMMAND_TITLE_SUFIX = 'yt-dlp --print filename -o "%(title)s" --restrict-filenames '

#获取视频的封面
COMMAND_COVER_DOWNLOAD = 'yt-dlp -o "{}%(title)s.%(ext)s" --restrict-filenames --skip-download --write-thumbnail --ffmpeg-location {} --convert-thumbnail png '

#获取视频的封面
COMMAND_SRT_VEDIO_ZH = "ffmpeg -i {} -strict -2 -vf subtitles=FearConditioning.zh-Hans.vtt:force_style='Fontsize=20\,Fontname=FZYBKSJW--GB1-0\,MarginV=35\,Bold=-1\,BorderStyle=1' -qscale:v 3 {}"

def download_file(command, url):
    # 下载文件
    print("开始下载文件，下载指令："+command+url)
    p = subprocess.Popen(command + url, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    start = time.time()
    print("********Start cover download command:" + url + "\n" + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
    while True:
        line = p.stdout.readline().decode("utf8", "ignore")
        if line == '':
            break
        print(line.strip('\n'))
    p.wait()
    end =time.time()
    print("********End:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)))
    print("taking："+str(int(end-start))+" seconds")

def handle_vedio(url):
    # 获取视频标题
    title = subprocess.getstatusoutput(COMMAND_TITLE_SUFIX + url)[1]
    print("获取视频标题: "+title)
    # 以title创建文件夹
    dir = DOWNLOAD_PATH + title
    if not os.path.exists(dir):
        os.makedirs(dir)
    dir = dir + "/"
    # 下载视频封面
    download_file(COMMAND_COVER_DOWNLOAD.format(dir, ffmpeg_path), url)
    # 下载视频
    download_file(COMMAND_PREFIX_DOWNLOAD.format(dir), url)
    # 添加中文字幕
    c1,c2 = add_srt_2_vedio(dir+title, ".mp4", dir+title+".zh-Hans.vtt", dir+title+".en.vtt")
    # 如果c1,c2都是0，表示添加字幕成功
    if c1[0] == 0 and c2[0] == 0:
        print("添加字幕成功")
        # 标记下载ok的链接
        mark_downloaded_url(url)
        # 删除过程中产生的字幕文件
        os.remove(dir+title+".zh-Hans.vtt")
        os.remove(dir+title+".en.vtt")
    else:
        print("添加字幕失败")

def get_url():
    '''读取文本中的视频链接'''
    print("\n********读取文本中的视频链接********")
    f = open(PATH, 'r+')
    for line in f.readlines():
        if not line == "\n":
            if line[0] == "h":
                return line.strip('\n')
    return ''


def add_srt_2_vedio(title, suffix, zh_srt, en_srt):
    print("\n********vvt  添加双语字幕 ********")
    COMMAND_SRT_VEDIO_ZH = ("ffmpeg -i {} -strict -2 -vf subtitles={}:force_style='Fontsize"
                           "=20\,Fontname=FZYBKSJW--GB1-0\,MarginV=35\,Bold=-1\,BorderStyle=1' -qscale:v 3 {}").format(title+suffix, zh_srt, title+".zh-Hans"+suffix)
    COMMAND_SRT_VEDIO_EN = ("ffmpeg -i {} -strict -2 -vf subtitles={}:force_style='Fontsize"
                           "=15\,Fontname=FZYBKSJW--GB1-0\,Bold=-1\,BorderStyle=1' -qscale:v 3 {}").format(title+".zh-Hans"+suffix, en_srt, title+".en"+suffix)
    print("\n zh :  " + COMMAND_SRT_VEDIO_ZH + "\n en :  " + COMMAND_SRT_VEDIO_EN )
    c1 = subprocess.getstatusoutput(COMMAND_SRT_VEDIO_ZH)
    print(c1)
    c2 = subprocess.getstatusoutput(COMMAND_SRT_VEDIO_EN)
    print(c2)
    return c1, c2


def mark_downloaded_url(url):
    '''标记下载ok的链接'''
    output = []
    f = open(PATH, 'r+')
    i = 0
    for line in f.readlines():
        line = line.strip('\n')
        url = url.strip('\n')
        if line == url:
            line = "*" + line
        output.append(line + "\n")
        i = i + 1
    f.close()
    f = open(PATH, 'w+')
    f.writelines(output)
    f.close()

def download_video(url, save_folder):
    try:
        options = {
            'outtmpl': save_folder + '/%(title)s.%(ext)s',
            'format': '22',
            'merge_output_format': 'mp4',
            'write_auto_sub': True,
            'sub_langs': 'zh-Hans,en',
            'restrictfilenames': True,
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            video_info = ydl.extract_info(url, download=False)
            if 'uploader' in video_info and 'youtube' in urllib.parse.urlparse(url).netloc:
                ydl.download([url])
            else:
                ydl.download([url])
        return True, video_info
    except Exception as e:
        print(e)
        return False, ''

if __name__ == "__main__":
    #检查url.txt是否存在
    if not os.path.exists(PATH):
        print("没有找到视频链接存放文本-url.txt,程序即将退出")
        time.sleep(2)
        exit(0)
    while True:
        url = get_url()
        print("获取：" + url)
        if url == "":
            print("全部视频和封面已下载完成")
            exit(0)
        handle_vedio(url)