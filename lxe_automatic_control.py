# coding:utf-8
import serial # シリアル通信用
import lxml # scraping用
import requests # scraping用
from bs4 import BeautifulSoup # scraping用
# import play_music as sound # アラーム用
import line_notify as info # LINE通知用
import csv
import numpy as np
import matplotlib.pyplot as plt
import time
url = "http://133.34.150.183/digital.cgi?chgrp=0?118_2_6_17_17_50_3"  # データロガーのwebページ

# DB1000との通信の設定(Serial)
ser = serial.Serial('/dev/ttyUSB0',9600,7,'E',timeout=1)

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
    else: # 不要かも
      print("無効な値です")
      exit()

def lrc_calc(message):
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

def order_sv_output(temperature):
    if abs(temperature - temperature_sv) > 10:
        print("##########10度以上の出力変化は受け付けません##########")
    else:
        sv_out_message = ":010600c8"
        sv_temperature = config_temp(int(temperature * 10))
        message = sv_out_message + sv_temperature
        messages = lrc_calc(message) + '\r\n'
        ser.write(messages.encode())
        ser.readline()
        print("##############温度の出力を%sに変更しました###############\n" % temperature)

def scraping_pressure(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, "lxml")
    p_data = soup.find_all("td")[34].b.text # データロガーの35番目のtdタグを取得
    pressure = float(p_data.strip().strip('+').strip()) # 空白や+などを削除してstr→float
    # 以下の2行はデータロガーの位置変えたりしたら、変更の必要がある。
    # print(soup.find_all("td")[34]) # 圧力表示部分のtdタグを出力
    # print(len(soup.find_all("td"))) # tdタグの個数を出力
    return pressure

def pid_calc(pid,now,target,time_diff): #pid計算
    _diff = target - now
    diff = pid[0] * _diff + pid[1] * time_diff * _diff / 2 - pid[2] * _diff / time_diff
    return diff

phase = 1  # 目標温度に収束と温度・圧力を平衡に保つ段階とで分けるために導入
# 以下の定数は最適化する必要あり temp_pid,pres_pidはそれぞれ[Kp,Ki,Kd]
# Kp:大きくすると立ち上がり時間が短くなるが、大きくしすぎると振動が起こる
# Ki:大きくすると収束値との誤差(定常偏差)を小さくする
# Kd:大きくすると振動現象を抑えられる
temp_pid = [1.0,1.0,2.0]
target_temp = -108.0 # 初期目標温度
pres_pid = [1.0,1.0,3.0]
target_pres = 95.0
## 時間の計測&csv保存用
time_diff = 0.0 #
sum_time = 0.0
time_prev = 0.0

prev_pv = 0.0 # 前回の計測時との差分を求めるために定義
prev_pres = 0.0 # 収束フェーズで変化率に応じてtarget_tempを変えるため
pres_count = 0 # 収束フェーズにおけるカウント用
## csvの保存用
pv_data = []
sv_data = []
pressure_data = []
time_data = []
csv_data = []

while True:
    print("------------------------------------------------------\n")
    ####sv,pvの取得の関数は定義したいなー
    ser.write(':01040064000196\r\n'.encode())  # 現在の温度(PV)を取得するための命令文
    response_pv = ser.readline() # readline()が応答を全て取得
    if int(response_pv[7:11], 16) >= 32768:
        _temperature_pv = int(response_pv[7:11], 16) - 65536
    else:
        _temperature_pv = int(response_pv[7:11], 16)
    temperature_pv = float(str(_temperature_pv)[:-2] + '.' + str(_temperature_pv)[-2:])
    print("現在の温度(PV)を表示 :",temperature_pv,"\n")

    ser.write(':01040066000194\r\n'.encode())  # 現在の温度(SV)を取得するための命令文
    response_sv = ser.readline() # readline()が応答を全て取得
    if int(response_sv[7:11], 16) >= 32768:
        _temperature_sv = int(response_sv[7:11], 16) - 65536
    else:
        _temperature_sv = int(response_sv[7:11], 16)
    temperature_sv = float(str(_temperature_sv)[:-1] + '.' + str(_temperature_sv)[-1:])
    print("現在の温度(SV)を表示 :",temperature_sv,"\n")

    change_temp = temperature_sv # SVの出力調整用

    pressure = scraping_pressure(url)
    print("現在の圧力を表示 :",pressure,"kPa\n")

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
    ## csvの保存処理
    csv_data.append([int(sum_time),temperature_pv,temperature_sv,pressure])
    with open('thesis.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく ←いらないかも
        writer.writerows(csv_data)

    if temperature_pv <= -112.00:
        message = "[注意]温度が%s℃になっています!!" % temperature_pv
        info.lxe_line_notify(message)
        order_sv_output(temperature_sv + 0.5)
        time.sleep(5)
    elif pressure <= 80.0 and temperature_pv <= 0.0: # 最初のXe導入時には反応しないようにする
        message = "[注意]圧力が%skPaになっています!!" % pressure
        info.lxe_line_notify(message)
        order_sv_output(temperature_sv + 0.5)
        time.sleep(5)
    elif 130.0 <= pressure:
        message = "[注意]圧力が%skPaになっています!!" % pressure
        info.lxe_line_notify(message)
        order_sv_output(temperature_sv - 0.5)
        time.sleep(5)
    elif phase == 1: # -114℃ ~ -50℃までの処理は書いてる
        if -80.00 <= temperature_pv <= -50.00:
            time.sleep(15)
        elif -90.00 <= temperature_pv <= -80.00:
            time.sleep(10)
        elif -106.00 <= temperature_pv <= -90.00 and time_diff != 0.0: # phase1:カーブを緩やかに
            if -0.2 < (temperature_pv - prev_pv) / 2:
                while temperature_pv < change_temp:
                    change_temp -= 0.5
                if temperature_sv != change_temp: # 同じ出力の場合、変更命令は出さない
                    order_sv_output(change_temp)
            time.sleep(5)  #より早く対応できるように
        elif -112.00 <= temperature_pv <= -106.00 and time_diff != 0.0:
            phase = 2
            message = "フェーズ2に移行するよ!\n温度:%s℃\n圧力:%skPa" % (temperature_pv,pressure)
            info.lxe_line_notify(message)
            time.sleep(1)
        else:
            time.sleep(20)
    elif phase == 2:
        if -112.00 <= temperature_pv <= -106.00: # phase2:目標値に収束
            pres_count += 1
            if pres_count % 100 == 0: # 5分ごとに確認
                if -0.0067 < (pressure - prev_pres) / 300 < 0.0067: # 5分で2kPaの変更がない場合収束値を変更
                    target_temp -= 0.5 # 変化ないため、pressureが下がるように温度を変更
                    message = "目標値を%s℃に変更するよ!" % target_temp
                    info.lxe_line_notify(message)
                    print("##############目標値を0.5度下げます###############\n")
                prev_pres = pressure
            elif pres_count == 1:
                prev_pres = pressure
            diff = pid_calc(temp_pid,temperature_pv,target_temp,time_diff)
            sv_conf = target_temp + round(diff,1)
            if temperature_sv != sv_conf: # 出力が同じじゃない時だけ出力変更
                order_sv_output(sv_conf)
            time.sleep(3)  # 変化率の計算(300の値)に紐づいてるので変更時は注意
        # phaseの切り替え
        if -106.00 <= temperature_pv:
            pres_count = 0 # 一度リセット
            phase = 1
            message = "フェーズ1に移行するよ!\n温度:%s℃\n圧力:%skPa" % (temperature_pv,pressure)
            info.lxe_line_notify(message)
            print("############フェーズ1に移行します############\n")
            time.sleep(1)
        elif pressure <= 95.0 and -112.0 <= temperature_pv <= 106.00:
            pres_count = 0 # 一度リセット
            phase = 3
            message = "フェーズ3に移行するよ!\n温度:%s℃\n圧力:%skPa" % (temperature_pv,pressure)
            info.lxe_line_notify(message)
            message = "キセノンを圧力100kPa以上になるまで導入して下さい"
            info.lxe_line_notify(message)
            print("############フェーズ3に移行します############\n")
            time.sleep(1)
    elif phase == 3:
        diff = pid_calc(pres_pid,pressure,target_pres,time_diff)
        sv_conf = target_temp + round(diff,1)
        if -1.5 <= round(diff,1) <= 10.0 and temperature_sv != sv_conf: # 急激な温度変化はさせないように
            order_sv_output(sv_conf)
        if 100 <= pressure or temperature_pv <= -111.00: # 下がりすぎた場合もフェーズ2に移行
            phase = 2
            message = "フェーズ2に移行するよ!\n温度:%s℃\n圧力:%skPa" % (temperature_pv,pressure)
            info.lxe_line_notify(message)
            print("############フェーズ2に移行します############\n")
        time.sleep(1)


    prev_pv = temperature_pv
