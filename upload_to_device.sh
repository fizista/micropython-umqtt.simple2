#!/bin/bash
COMPILED='yes'
PORT=/dev/ttyUSB0
BAUD=115200

if [ -e "/dev/ttyUSB0" ]; then
  PORT=/dev/ttyUSB0 # esp8266
elif [ -e "/dev/ttyACM0" ]; then
  PORT=/dev/ttyACM0 # esp32
else
  echo "ERROR: Device not connected."
  exit 1
fi

[ "$1" != "" ] && COMPILED=$1
[ "$2" != "" ] && PORT=$2
[ "$3" != "" ] && BAUD=$3

function a() {
  echo "RUN: $*"
  ampy -d1 --baud "${BAUD}" --port "${PORT}" $*
}

files_on_device=$(a ls)

function copy_compiled() {
  a mkdir /umqtt
  a put ./build_port/umqtt/errno.mpy /umqtt/errno.mpy
  a put ./build_port/umqtt/simple2.mpy /umqtt/simple2.mpy
  a put ./build_port/umqtt/__init__.mpy /umqtt/__init__.mpy
  a put ./build_port/tests.mpy
  a put ./main.py
}

function _rm_dir() {
  [ $(echo -e "$files_on_device" | grep $1) ] && a rmdir $1
}

function _rm_file() {
  [ $(echo -e "$files_on_device" | grep $1) ] && a rm $1
}

function delete_compiled() {
  _rm_dir /umqtt
  _rm_file /tests.mpy
  _rm_file /main.mpy
}

function copy_normal() {
  a mkdir /umqtt
  a put ./src/umqtt/errno.py /umqtt/errno.py
  a put ./src/umqtt/simple2.py /umqtt/simple2.py
  a put ./src/umqtt/__init__.py /umqtt/__init__.py
  a put ./tests.py
  a put ./main.py
}

function delete_normal() {
  _rm_dir /umqtt
  _rm_file /tests.py
  _rm_file /main.mpy
}

case "$COMPILED" in
"yes" | "y")
  delete_normal
  ./compile.sh r
  copy_compiled
  ;;
"no" | "n")
  delete_compiled
  copy_normal
  ;;
esac
