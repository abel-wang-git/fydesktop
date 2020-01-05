import argparse
import ctypes
import io
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from distutils.version import LooseVersion
from glob import iglob

import PIL.Image as Image
import appdirs
import threadpool
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler

# 坐标范围
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


def get_desktop_environment():
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    elif sys.platform == "darwin":
        return "mac"
    else:  # Most likely either a POSIX system or something not much common
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session != None:  # easier to match if we doesn't have  to deal with caracter cases
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome", "unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox",
                                   "blackbox", "openbox", "icewm", "jwm", "afterstep", "trinity", "kde"]:
                return desktop_session
            ## Special cases ##
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                return "xfce4"
            elif desktop_session.startswith("ubuntu"):
                return "unity"
            elif desktop_session.startswith("lubuntu"):
                return "lxde"
            elif desktop_session.startswith("kubuntu"):
                return "kde"
            elif desktop_session.startswith("razor"):  # e.g. razorkwin
                return "razor-qt"
            elif desktop_session.startswith("wmaker"):  # e.g. wmaker-common
                return "windowmaker"
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return "kde"
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return "gnome2"
        # From http://ubuntuforums.org/showthread.php?t=652320
    return "unknown"


def plasma_version():
    try:
        output = subprocess.Popen(["plasmashell", "-v"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
        print("Plasma version '{}'.".format(output))
        version = re.match(r"plasmashell (.*)", output).group(1)
        return LooseVersion(version)
    except (subprocess.CalledProcessError, IndexError):
        return LooseVersion("")


def set_wall(file_path):
    desk = get_desktop_environment()
    if desk == "windows":
        ctypes.windll.user32.SystemParametersInfoW(20, 0, file_path, 3)
    elif desk == "mac":
        subprocess.call(["osascript", "-e",
                         'tell application "System Events"\n'
                         'set theDesktops to a reference to every desktop\n'
                         'repeat with aDesktop in theDesktops\n'
                         'set the picture of aDesktop to \"' + file_path + '"\nend repeat\nend tell'])
    else:
        if desk == "xfce4":
            displays = subprocess.getoutput('xfconf-query --channel xfce4-desktop --list | grep last-image').split()
            for display in displays:
                subprocess.call(
                    ["xfconf-query", "--channel", "xfce4-desktop", "--property", display, "--set", file_path])
        elif desk in ["gnome", "unity", "cinnamon", "pantheon", "gnome-classic"]:
            if desk == "unity":
                subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "draw-background", "false"])
            subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", "file://" + file_path])
            subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "picture-options", "scaled"])
            subprocess.call(["gsettings", "set", "org.gnome.desktop.background", "primary-color", "#000000"])
            if desk == "unity":
                assert os.system('bash -c "gsettings set org.gnome.desktop.background draw-background true"') == 0
        elif desk == "mate":
            subprocess.call(["gsettings", "set", "org.mate.background", "picture-filename", file_path])
        elif desk == 'i3':
            subprocess.call(['feh', '--bg-max', file_path])
        elif desk == "lxde":
            subprocess.call(["pcmanfm", "--set-wallpaper", file_path, "--wallpaper-mode=fit", ])
        elif desk == "kde":
            if plasma_version() > LooseVersion("5.7"):
                ''' Command per https://github.com/boramalper/himawaripy/issues/57

                    Sets 'FillMode' to 1, which is "Scaled, Keep Proportions"
                    Forces 'Color' to black, which sets the background colour.
                '''
                script = 'var a = desktops();' \
                         'for (i = 0; i < a.length; i++) {{' \
                         'd = a[i];d.wallpaperPlugin = "org.kde.image";' \
                         'd.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");' \
                         'd.writeConfig("Image", "file://{}");' \
                         'd.writeConfig("FillMode", 1);' \
                         'd.writeConfig("Color", "#000");' \
                         '}}'
                try:
                    subprocess.check_output(["qdbus", "org.kde.plasmashell", "/PlasmaShell",
                                             "org.kde.PlasmaShell.evaluateScript", script.format(file_path)])
                except subprocess.CalledProcessError as e:
                    if "Widgets are locked" in e.output.decode("utf-8"):
                        print("Cannot change the wallpaper while widgets are locked! (unlock the widgets)")
                    else:
                        raise e
            else:
                print("Couldn't detect plasmashell 5.7 or higher.")


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
    set_wall(output_file)


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
    try:
        executors = {
            'default': {'type': 'threadpool', 'max_workers': 20},
            'processpool': ProcessPoolExecutor(max_workers=5)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        scheduler = BlockingScheduler(executors=executors, job_defaults=job_defaults)
        scheduler.add_job(tick, trigger="interval", seconds=900, id="tick")
        scheduler.start()
        scheduler.print_jobs()
    except:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
