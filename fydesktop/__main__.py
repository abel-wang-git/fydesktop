import argparse
import io
import xml.etree.ElementTree as ET
import os
import urllib.request
from datetime import datetime
from glob import iglob

import PIL.Image as Image
Image.MAX_IMAGE_PIXELS = None
import appdirs

# 坐标范围
from fydesktop import util

from screeninfo import get_monitors

x = -5500
y = 5500


def getlast():
    # 获取最后更新的日期和时间
    url = "https://img.nsmc.org.cn/PORTAL/NSMC/XML/FY4B/FY4B_AGRI_IMG_DISK_GCLR_NOM.xml"
    resp = urllib.request.urlopen(url)
    last = resp.read()
    decoded_data = last.decode("utf-8")
    root = ET.fromstring(decoded_data)
    first_image = root.find('image')
    first_image_time = first_image.get('time').split(' ')[0]
    first_image_url = first_image.get('url')
    return first_image_time, first_image_url



def download(url, index, lever, to_image):
    for i in range(1, 4):
        try:
            with urllib.request.urlopen(url) as resp:
                print("download  {}/{}...".format(index, (lever * 2) * (lever * 2)))
                tile = Image.open(io.BytesIO(resp.read()))
                to_image.paste(tile, ((index % (lever * 2)) * 512, int(index / (lever * 2)) * 512))
                return
        except Exception as e:
            print(e)
            print("[{}/3] Retrying to download ...\n".format(i))


def parse_arg():
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-lever', type=int, default=2, help="lever (2,4,8)", )
    parser.add_argument("-outdir", type=str, dest="outdir",
                        help="directory to save the temporary background image",
                        default=appdirs.user_cache_dir(appname="fydesktop", appauthor=False))
    parser.add_argument('-save_his', type=bool, default=False, help="Is save image download history", )
    args = parser.parse_args()
    return args


def save_img(arg, date, to_image):
    output_file = os.path.join(arg.outdir, "fydesktop-%s.jpg" % (date))
    print("\nSaving to '%s'..." % (output_file,))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    if (not arg.save_his):
        for file in iglob(os.path.join(arg.outdir, "fydesktop-*.jpg")):
            os.remove(file)
    to_image.save(output_file,format="JPEG")
    util.set_background(output_file)


def tick():
    arg = parse_arg()
    monitors = get_monitors()
    monitorProportion = 1
    for monitor in monitors:
        prop = monitor.width / monitor.height
        if prop > monitorProportion:
            monitorProportion = monitor.width / monitor.height

    first_image_time, first_image_url = getlast()

    response = urllib.request.urlopen(first_image_url)
    imageByte = Image.open(io.BytesIO(response.read()))
    # imageByte.save('downloaded_image.jpg', format="JPEG")
    width, height = imageByte.size
    imageHeight = int(height * 1.5)
    to_image = Image.new('RGB', (int(imageHeight * monitorProportion), imageHeight))
    to_image.paste(imageByte, (int((imageHeight * monitorProportion/2)-(width/2)), int(height * 0.25)))
    save_img(arg, first_image_time, to_image)
    print('Tick! The time is: %s' % datetime.now())

def main():
    tick()


if __name__ == "__main__":
    main()
