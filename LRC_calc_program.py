# coding:utf-8
import sys
current_pv_message = ":010400640001"
current_sv_message = ":010400660001"
sv_out_message = ":010600c8"

def config_temp(temperture):
    str_temperture = str(temperture)
    if str_temperture.startswith("-"):
      sv_temperture_str = hex(65536 + temperture)[2:]
      return sv_temperture_str
    elif str_temperture.isdigit():
      zero_count = 4 - len(hex(temperture)[2:])
      zero_num = "0" * zero_count
      sv_temperture_str = zero_num + hex(temperture)[2:]
      return sv_temperture_str
    else:
      print("無効な値です")
      sys.exit()

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

print ("どんな命令文を作成しますか？")
print("0:SVの出力設定\n1:正のSVの出力設定")
order = input("input number :")

if order == "0":
    print("*小数点第1位まで")
    _temperture = input("温度を入力して下さい:")
    temperture = int(float(_temperture) * 10)
    sv_temperture = config_temp(temperture)
    message = sv_out_message + sv_temperture
    messages = lrc_calc(message) + "\r\n"
    print(repr("命令文は: ser.write('%s'.encode())" % messages))
elif order == "1":
    print("*小数点第1位まで")
    _temperture = input("温度を入力して下さい:")
    temperture = int(float(_temperture) * 10)
    sv_temperture = config_temp(temperture)
    message = sv_out_message + sv_temperture
    messages = lrc_calc(message) + "\r\n"
    print(repr("命令文は: ser.write('%s'.encode())" % messages))
else:
    print ("無効な値です")
