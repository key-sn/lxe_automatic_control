# coding:utf-8
import lxml # scraping用
import requests # scraping用
from bs4 import BeautifulSoup # scraping用
import play_music as sound # アラーム用
import line_notify as info # LINE通知用
import csv
import numpy as np
import matplotlib.pyplot as plt
import time
url = "http://133.34.150.183/digital.cgi?chgrp=0?118_2_6_17_17_50_3"  # データロガーのwebページ
message = "hoge"
info.lxe_line_notify(message)

sound.music("keihou",3)

# 0x41             # 65 16進数表記
# 0o0101           # 65 8進数表記
# 0b1000001        # 65 2進数表記
# print(hex(65))          # '0x41' 16進数文字列へ変換
# print(oct(65))          # '0101' 8進数文字列へ変換
# print(bin(65))          # '0b1000001' 2進数文字列へ変換
# print(format(0x41,'b')) # '1000001'
# print(int('41',16))     # 65 16進数文字列を数値へ変換
# print(int('65'))        # 65 10進数文字列を数値へ変換
# print(int('1000001',2)) # 65
# print(str(6565))        # '6565' 1byte以上の数値を10進数文字列へ変換
# print(chr(65))          # 'A' 数値をASCII文字へ変換
# print(ord('A'))         # 65 ASCII文字を数値へ変換

###python-control導入###
# from control import matlab
# from matplotlib import pyplot as plt
#
# num = [1]
# den = [1, 19, 108, 180]
# sys = matlab.tf(num, den)
# matlab.rlocus(sys)
# plt.show()
######################
# import numpy as np
# from control import matlab
# from matplotlib import pylab as plt
# # PID 制御器 5 8 0.4
# Kp = 5
# Ki = 8
# Kd = 0.4
# num = [Kd, Kp, Ki]
# den = [1, 0]
# K = matlab.tf(num, den)
# # 制御対象
# Kt = 1
# J = 0.05
# C = 0.3
# # J = 0.01
# # C = 0.1
# num = [Kt]
# den = [J, C, 1]
# G = matlab.tf(num, den)
# # フィードバックループ
# sys = matlab.feedback(K*G, 1)
#
# t = np.linspace(0, 3, 1000)
# yout, T = matlab.step(sys, t)
# plt.xlabel("time [s]")
# plt.ylabel("controlled variable")
# plt.plot(T, yout)
# plt.axhline(1, color="b", linestyle="--")
# plt.xlim(0, 3)
# plt.show()


# from control.matlab import *
# from matplotlib import pyplot as plt
#
# def main():
#   # PID制御器のパラメータ
#   Kp = 0.6  # 比例
#   Ki = 0.03 # 積分
#   Kd = 0.03 # 微分
#   num = [Kd, Kp, Ki]
#   den = [1, 0]
#   K = tf(num, den)
#   # 制御対象
#   Kt = 1
#   J = 0.01
#   C = 0.1
#   num = [Kt]
#   den = [J, C, 0]
#   G = tf(num, den)
#   # フィードバックループ
#   sys = feedback(K*G, 1)
#   t = np.linspace(0, 3, 1000)
#   y, T = step(sys, t)
#   plt.plot(T, y)
#   plt.grid()
#   plt.axhline(1, color="b", linestyle="--")
#   plt.xlim(0, 3)
#   plt.show()
#
# if __name__ == "__main__":
#   main()
