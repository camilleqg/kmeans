#!/bin/sh
sudo mke2fs -t ext4 -L RAMDISK  -vm0 /dev/ram0 200G
sudo mkdir /media/ramdisk_empir
sudo mount /dev/ram0 /media/ramdisk_empir
sudo chmod --verbose a+rwx /media/ramdisk_empir