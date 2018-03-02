########################
# 名前:石原 慧
# 作成日:
# 変更日:
# 使い方:再生時間と再生ファイルを指定。
# 再生時間の変わりにループ再生でも指定できる
########################
# coding:utf-8
import pygame.mixer
import time
def music(name,play_time):
    # mixerモジュールの初期化
    pygame.mixer.init()
    # 音楽ファイルの読み込み
    pygame.mixer.music.load("%s.mp3"%name)
    # 音楽再生、および再生回数の設定(-1はループ再生)
    pygame.mixer.music.play(-1)
    time.sleep(play_time)
    # 再生の終了
    pygame.mixer.music.stop()
