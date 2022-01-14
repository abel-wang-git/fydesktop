# fydesktop
![alt](https://github.com/wanghuiwen1/fydesktop/blob/master/fwdesktop-201908310915.png?raw=true)
fydesktop是基于python3的一个脚本，它会实时获取地球图片设置为桌面背景，灵感来自于[himawaripy](https://github.com/boramalper/himawaripy)<br>
设置每15分钟运行一次的的cronjob（或systemd服务），以自动获取地球的近实时图片。
##  支持的桌面环境
  * windows 10
  * xfce4
  * Unity 7（未测）
  * Mate 1.8.1（未测）
  * Pantheon（未测）
  * LXDE（未测）
  * OS X（未测）
  * GNOME 3（未测）
  * Cinnamon 2.8.8（未测）
  * KDE（未测）
##  可用选项
  ```bash 
     -lever 图片分辨率 2 4 8 
     -outdir 图片下载保存的路径
     -save_his 是否保存下载的图片, 默认不保存 设置为 True 即保存
  ```
## 安装
  需要先安装pthon3 （python2下未测试）
  ```Bash
  cd fydesktop
  python3 setup.py install
  fydesktop
  ```
## win10定时任务
windows安装后会打印命令安装的位置 一般为 C:\Users\Administrator\AppData\Local\Programs\Python\Python37-32\Scripts<br>
[定时任务](https://blog.csdn.net/xielifu/article/details/81016220)

## systemd 方式定时任务
####   Service 单元
    vim /usr/lib/systemd/system/fydesktop.service
    #添加以下内容    
    [Unit]
    Description=fydesktop
    
    [Service]
    ExecStart=/usr/bin/fydesktop #此处为fydesktop的安装路径 通过 whereis fydesktop 获取
#### Timer 单元
     vim /usr/lib/systemd/system/fydesktopTimer.timer
      #添加以下内容    
     [Unit]
     Description=fydesktopTimer
    
     [Timer]
     OnBootSec=1s
     OnUnitActiveSec=15m
     Unit=fydesktop.service
    
     [Install]
     WantedBy=multi-user.target
#### 启用
    systemctl enable fydesktopTimer.timer
### archlinux 下xfce4中system无法设置背景
    新装系统后发现怎么也无法设置背景 ，最后发现是找不到环境变量
    修改 /etc/X11/xinit/xinitrc.d/50-systemd-user.sh 文件 添加 DESKTOP_SESSION
    ```Bash
    #!/bin/sh
    systemctl --user import-environment DISPLAY XAUTHORITY DESKTOP_SESSION
    
    if command -v dbus-update-activation-environment >/dev/null 2>&1; then
        dbus-update-activation-environment DISPLAY XAUTHORITY DESKTOP_SESSION
    fi
    ```
    修改 ~/.xprofile 文件 在最后添加上面的脚本
    ```Bash
    ...
    /etc/X11/xinit/xinitrc.d/50-systemd-user.sh
    ```
##  [KDE用户](https://github.com/boramalper/himawaripy#for-kde-users)
##  [OS X](https://github.com/boramalper/himawaripy#for-mac-osx-users)
