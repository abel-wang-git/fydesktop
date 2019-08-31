# fwdesktop
![alt](https://github.com/wanghuiwen1/fwdesktop/fwdesktop-201908310915.png)
fwdesktop是基于python3的一个脚本，它会实时获取地球图片设置为桌面背景，灵感来自于[himawaripy](https://github.com/boramalper/himawaripy)<br>
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
  cd fwdesktop
  python setup.py install
  fwdesktop
  ```

## systemd 方式定时任务
####   Service 单元
    ```Bash
    vim /usr/lib/systemd/system/fwdesktop.service
    #添加以下内容    
    [Unit]
    Description=fwdesktop
    
    [Service]
    ExecStart=/usr/bin/fwdesktop #此处为fwdesktop的安装路径 通过 whereis fwdesktop 获取
    ```
#### Timer 单元
     ```Bash
     vim /usr/lib/systemd/system/fwdesktopTimer.timer
      #添加以下内容    
     [Unit]
     Description=fwdesktopTimer
    
     [Timer]
     OnBootSec=1s
     OnUnitActiveSec=15m
     Unit=fwdesktop.service
    
     [Install]
     WantedBy=multi-user.target
     ```
#### 启用
    ```Bash
    systemctl enable fwdesktopTimer.timer
    systemctl enable fwdesktopTimer.timer
    ```
##  [KDE用户](https://github.com/boramalper/himawaripy#for-kde-users)
##  [OS X](https://github.com/boramalper/himawaripy#for-mac-osx-users)
