import PIL.Image as Image
import io
import json
import threadpool
import urllib.request

# 清晰度  2 4 8
lever = 8
# 坐标范围
x = -5500
y = 5500
to_image = Image.new('RGB', (lever * 2 * 512, lever * 2 * 512))
path = "/home/wanghuiwen/map.jpg"


def getlast():
    # 获取最后更新的日期和时间
    url = "http://fy4.nsmc.org.cn/nsmc/v1/nsmc/image/animation/datatime/mongodb?dataCode=FY4A-_AGRI--_N_DISK_1047E_L1C_MTCC_MULT_NOM_YYYYMMDDhhmmss_YYYYMMDDhhmmss_4000M_V0001.JPG&hourRange=3&isHaveNight=1&isCustomTime=false&endTime=2018-07-11+16%3A00%3A00"
    resp = urllib.request.urlopen(url)
    last = json.loads(resp.read())
    date = last.get("ds")[-1].get("dataDate")
    time = last.get("ds")[-1].get("dataTime")[0:4]
    return "https://satellite.nsmc.org.cn/mongoTile_DSS/NOM/TileServer.php?layer=PRODUCT&PRODUCT=FY4A-_AGRI--_N_DISK_1047E_L1C_MTCC_MULT_NOM_YYYYMMDDhhmmss_YYYYMMDDhhmmss_4000M_V0001.JPG&DATE=" + date + "&TIME=" + time + "&&ENDTIME=&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&FORMAT=image%2Fjpeg&TRANSPARENT=true&LAYERS=satellite&NOTILE=BLACK&TILED=true&WIDTH=256&HEIGHT=256&SRS=EPSG%3A11111&STYLES=&BBOX="


# 生成坐标
def genurl():
    index = 0
    urls = []
    for a in range((lever * 2) * (lever * 2)):
        x1 = x + ((index % (lever * 2)) * int(5500 / lever))
        y1 = 5500 - int((index / (lever * 2) + 1)) * int(5500 / lever)
        y2 = 5500 - int(index / (lever * 2)) * int(5500 / lever)
        x2 = x + (((index % (lever * 2)) + 1) * int(5500 / lever))
        index += 1
        urls.append(str(x1) + ',' + str(y1) + ',' + str(x2) + ',' + str(y2))
    return urls


def download(url, index):
    for i in range(1, 4):
        try:
             with urllib.request.urlopen(url) as resp:
                print("download  {}/{}...".format(index, (lever * 2) * (lever * 2)))
                tile = Image.open(io.BytesIO(resp.read()))
                to_image.paste(tile, ((index % (lever * 2)) * 512, int(index / (lever * 2)) * 512))
                return tile
        except Exception as e:
            print(e)
            print("[{}/3] Retrying to download ...".format(i))


def main():
    baseurl = getlast()
    index = 0
    pool = threadpool.ThreadPool(10)
    params = []
    for url in genurl():
        param = [baseurl + url, index]
        params.append((param, None))
        index += 1
    tasks = threadpool.makeRequests(download, params)
    [pool.putRequest(task) for task in tasks]
    pool.wait()
    to_image.save(path)


if __name__ == "__main__":
    main()
