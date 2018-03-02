NAME: 液体キセノンオート制御プログラム
====

## Overview
- lxe_automatic_control = オート制御プログラム
- lxe_manual_control = マニュアル制御プログラム
- __pycache__ = キャッシュファイル
- その他 = ライブラリ
の三つから構成されている。

※　__pycahe__　は自前のモジュールがimportされると生成されるキャッシュファイルのようでデフォルトのpython3.2以降の仕様のようです。生成しないようにすることも可能ですが、生成されていても問題ないので残しておきます。

## Usage
### 初期設定: ヒーターの電圧は30V、初期目標温度は-90℃
### sshで入っていて、外部から動かしたい時
```
$ sudo nohup python lxe_automatic_control.py & # 起動→「+suspend」で動かない場合は「`$ fg`」とうてば動くかと
$ ps aux | grep lxe_automatic_control # プロセスが動いているかどうか確認
$ sudo kill プロセス番号  # プロセスを終了する場合
```

## Author

[key20171012](https://github.com/key20171012)
