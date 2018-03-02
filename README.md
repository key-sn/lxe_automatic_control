NAME: 液体キセノンオート制御プログラム
====

## Overview
- オート制御プログラム
- マニュアル制御プログラム
- ライブラリ
の三つから構成されている。

## Usage
### 初期設定
### ヒーターの電圧は30V、初期目標温度は-90℃
```
$ sudo nohup python lxe_automatic_control.py & # 起動→「+suspend」で動かない場合は「$ fg」とうてば動くかと
$ ps aux | grep lxe_automatic_control # プロセスが動いているかどうか確認
$ sudo kill プロセス番号  # プロセスを終了する場合
```

## Install

## Contribution

## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author

[tcnksm](https://github.com/tcnksm)
