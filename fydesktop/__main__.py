import argparse
import io
import json
import os
import urllib.request
from datetime import datetime
from glob import iglob

import PIL.Image as Image
import appdirs
import threadpool
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler

# 坐标范围
from fydesktop import util

x = -5500
y = 5500


def getlast():
    # 获取最后更新的日期和时间
    url = "http://fy4.nsmc.org.cn/nsmc/v1/nsmc/image/animation/datatime/mongodb?dataCode=FY4A-_AGRI--_N_DISK_1047E_L1C_MTCC_MULT_NOM_YYYYMMDDhhmmss_YYYYMMDDhhmmss_4000M_V0001.JPG&hourRange=3&isHaveNight=1&isCustomTime=false&endTime=2018-07-11+16%3A00%3A00"
    resp = urllib.request.urlopen(url)
    last = json.loads(resp.read())
    date = last.get("ds")[-1].get("dataDate")
    time = last.get("ds")[-1].get("dataTime")[0:4]
    return date, time, "https://satellite.nsmc.org.cn/mongoTile_DSS/NOM/TileServer.php?layer=PRODUCT&PRODUCT=FY4A-_AGRI--_N_DISK_1047E_L1C_MTCC_MULT_NOM_YYYYMMDDhhmmss_YYYYMMDDhhmmss_4000M_V0001.JPG&DATE=" + date + "&TIME=" + time + "&&ENDTIME=&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fjpeg&TRANSPARENT=true&LAYERS=satellite&NOTILE=BLACK&TILED=true&WIDTH=256&HEIGHT=256&SRS=EPSG%3A11111&STYLES=&BBOX="


# 生成坐标
def genurl(baseurl, lever, to_image):
    index = 0
    params = []
    for a in range((lever * 2) * (lever * 2)):
        x1 = x + ((index % (lever * 2)) * int(5500 / lever))
        y1 = 5500 - int((index / (lever * 2) + 1)) * int(5500 / lever)
        y2 = 5500 - int(index / (lever * 2)) * int(5500 / lever)
        x2 = x + (((index % (lever * 2)) + 1) * int(5500 / lever))
        param = [baseurl + str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2), index, lever, to_image]
        params.append((param, None))
        index += 1
    return params


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


def save_img(arg, date, time, to_image):
    output_file = os.path.join(arg.outdir, "fydesktop-%s%s.png" % (date, time))
    print("\nSaving to '%s'..." % (output_file,))
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    if (not arg.save_his):
        for file in iglob(os.path.join(arg.outdir, "fydesktop-*.png")):
            os.remove(file)
    to_image.save(output_file)
    util.set_background(output_file)


def tick():
    arg = parse_arg()

    lever = arg.lever
    to_image = Image.new('RGB', (lever * 2 * 512, lever * 2 * 512))
    date, time, baseurl = getlast()

    pool = threadpool.ThreadPool(10)
    tasks = threadpool.makeRequests(download, genurl(baseurl, lever, to_image))
    [pool.putRequest(task) for task in tasks]
    pool.wait()

    save_img(arg, date, time, to_image)
    print('Tick! The time is: %s' % datetime.now())


def main():
    tick()
    # try:
    #     executors = {
    #         'default': {'type': 'threadpool', 'max_workers': 20},
    #         'processpool': ProcessPoolExecutor(max_workers=5)
    #     }
    #     job_defaults = {
    #         'coalesce': False,
    #         'max_instances': 3
    #     }
    #     scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults)
    #     scheduler.add_job(tick, trigger="interval", seconds=900, id="tick")
    #     scheduler.start()
    #     scheduler.print_jobs()
    # except:
    #     scheduler.shutdown()


if __name__ == "__main__":
    main()
