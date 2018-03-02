# coding:utf-8
import serial
import lxml
import requests
from bs4 import BeautifulSoup
import csv
import numpy as np
import matplotlib.pyplot as plt
import time
url = "http://133.34.150.183/digital.cgi?chgrp=0?118_2_6_17_17_50_3"  # データロガーのwebページ
# ループ用
time_diff = 0.0
pv_data = []
sv_data = []
pressure_data = []
time_data = []
csv_data = []
sum_time = 0.0
time_prev = 0.0

ser = serial.Serial('/dev/ttyUSB0',9600,7,'E',timeout=1) # DB1000との通信の設定(Serial)

def config_temp(temperature):
    str_temperature = str(temperature)
    if str_temperature.startswith("-"):
      sv_temperature_str = hex(65536 + temperature)[2:]
      return sv_temperature_str
    elif str_temperature.isdigit():
      zero_count = 4 - len(hex(temperature)[2:])
      zero_num = "0" * zero_count
      sv_temperature_str = zero_num + hex(temperature)[2:]
      return sv_temperature_str
    else:
      print("無効な値です")

def lrc_calc(message): # エラーコードの計算
    calc_number = list(message[1:])
    even_number = 0
    odd_number = 0
    for index, str_number in enumerate(calc_number):
        if index % 2 == 0:
          odd_number += int(str_number,16)
        else:
          even_number += int(str_number,16)
    err_num_2 = 15 - even_number % 16 + 1
    if err_num_2 == 16:
      err_num_1 = 15 - (odd_number + even_number // 16) % 16 + 1
    else:
      err_num_1 = 15 - (odd_number + even_number // 16) % 16
    return message + hex(err_num_1)[-1] + hex(err_num_2)[-1]

def order_pv_input():
    ser.write(':01040064000196\r\n'.encode())  # 現在の温度(PV)を取得するための命令文
    response_pv = ser.readline() # readline()が応答を全て取得
    if int(response_pv[7:11], 16) >= 32768:
        _temperature_pv = int(response_pv[7:11], 16) - 65536
    else:
        _temperature_pv = int(response_pv[7:11], 16)
    temperature_pv = float(str(_temperature_pv)[:-2] + '.' + str(_temperature_pv)[-2:])
    print("現在の温度(PV)を表示 :",temperature_pv,"\n")

def order_sv_input():
    ser.write(':01040066000194\r\n'.encode())  # 現在の温度(SV)を取得するための命令文
    response_sv = ser.readline() # readline()が応答を全て取得
    if int(response_sv[7:11], 16) >= 32768:
        _temperature_sv = int(response_sv[7:11], 16) - 65536
    else:
        _temperature_sv = int(response_sv[7:11], 16)
    temperature_sv = float(str(_temperature_sv)[:-1] + '.' + str(_temperature_sv)[-1:])
    print("現在の温度(SV)を表示 :",temperature_sv,"\n")

def order_sv_output(temperature):
    sv_out_message = ":010600c8"
    temperature = int(temperature * 10)
    str_temperature = str(temperature)
    if str_temperature.startswith("-"):
      sv_temperature = hex(65536 + temperature)[2:]
    elif str_temperature.isdigit():
      zero_count = 4 - len(hex(temperature)[2:])
      zero_num = "0" * zero_count
      sv_temperature = zero_num + hex(temperature)[2:]
    else:
      print("無効な値です")
      exit()
    message = sv_out_message + sv_temperature
    messages = lrc_calc(message) + '\r\n'
    ser.write(messages.encode())
    ser.readline()

def scraping_pressure(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    p_data = soup.find_all("td")[34].b.text
    pressure = float(p_data.strip().strip('+').strip()) # 空白や+などを削除してstr→float
    return pressure

while True:
    print("------------------------------------------------------\n")
    print ("どんな命令を実行しますか？")
    print("1:温度(SV)の出力設定\n2:現在データの取得\n3:データの記録(ループ)\n4:プログラムの終了")
    order = input("input number : ")
    print()
    if order == "1":
        print("*小数点第1位まで")
        _temperature = input("温度を入力して下さい:")
        order_sv_output(float(_temperature))
    elif order == "2":
        order_pv_input()
        order_sv_input()
        pressure = scraping_pressure(url)
        print("現在の圧力を表示 :",pressure,"kPa\n")
    elif order == "3":
        while True:
            print("------------------------------------------------------\n")
            temperature_pv = order_pv_input()
            temperature_sv = order_sv_input()
            pressure = scraping_pressure(url)
            print("現在の圧力を表示 :",pressure,"kPa\n")
            # 時間経過の計算
            if not time_prev == 0.0:
                time_diff = time.time() - time_prev
                sum_time += time_diff
            time_prev = time.time()
            # 経過時間を表示
            if int(sum_time) <= 60:
                print("経過時間 :",int(sum_time),"秒\n")
            elif 60 <= int(sum_time) <= 3600:
                print("経過時間 :",int(sum_time) // 60,"分",int(sum_time) % 60,"秒\n")
            else:
                print("経過時間 :",int(sum_time) // 3600,"時",int(sum_time) // 60 % 60,"分",int(sum_time) % 60,"秒\n")
            # csv保存
            csv_data.append([int(sum_time),temperature_pv,temperature_sv,pressure])
            with open('lxe_log.csv', 'w') as f:
                writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
                writer.writerows(csv_data)
            time.sleep(5)
    elif order == "4":
        exit()
    else:
        print ("無効な値です\n")
