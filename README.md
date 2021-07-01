# SplatoonKillDigestMakerPy
Python version of the SplatoonKillDigestMaker

## 概要
　SplatoonKillDigestMakerはスプラトゥーン2で撮り溜めた動画を何とか供養したいという思いで作られた、キルシーン自動生成プログラムです。
古典的なテンプレートマッチング手法を使ってキルシーンを切り出し、自動で動画編集します。
SplatoonKillDigestMakerはもともとWindows上のVisual Studioを用いてC++で開発されていましたが、
Visual Studioの度重なるバージョン変更により、プログラムの保守が難しくなったため、Pythonバージョンに新たに移行しました。

# 環境
- Ubuntu 20.04 on wsl2
- Python 3.6.13

### WSL2でUbuntu 20.04をインストールするための参考になりそうなサイト
- https://qiita.com/whim0321/items/ed76b490daaec152dc69
- https://www.kkaneko.jp/tools/wsl/wsl2.html
- (私はこの方法でやってないので保証できません・・・。）

# 使用方法
## 準備
### ローカルのファイルを使用する場合
- 動画ファイルをTargetFilesの中に入れる

### Youtubeの動画を使用する場合
- youtube_url.txtにYouTubeのURLを貼り付ける
- 複数行に対応。最後に改行を入れること

## 実行方法
```
python3 kill_digest_maker.py
```

### To do: 
- 引数で入力を与えられるようにする

# 環境構築メモ
- 自分の環境構築時の手順を記載しておく
- WSL2およびUbuntuはインストール済みとする
### gitのインストール
```
sudo apt install -y git
```
### コンパイラインストール
```
sudo apt install -y build-essential
```
### その他必要なライブラリ
```
sudo apt install -y wget libbz2-dev libreadline-dev libssl-dev libsqlite3-dev cmake
```
### pyenv virtualenv python環境インストール
```
git clone https://github.com/yyuu/pyenv.git ~/.pyenv
git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/lib:/usr/lib;' >> ~/.bashrc
source ~/.bashrc
CONFIGURE_OPTS=--enable-shared pyenv install 3.6.13
```
### ffmpegインストール
```
sudo apt install -y yasm libx264-dev libx265-dev
cd ~
mkdir ~/tools
cd ~/tools
wget http://pkgconfig.freedesktop.org/releases/pkg-config-0.29.2.tar.gz
tar -zxvf pkg-config-0.29.2.tar.gz
cd cd pkg-config-0.29.2
./configure --with-internal-glib
make -j8
sudo make install
cd ~/tools
wget https://launchpad.net/ubuntu/+archive/primary/+sourcefiles/ffmpeg/7:4.3.2-0+deb11u2ubuntu1/ffmpeg_4.3.2.orig.tar.xz
tar Jxfv ffmpeg_4.3.2.orig.tar.xz
cd ffmpeg-4.3.2
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/lib/x86_64-linux-gnu/pkgconfig
./configure --enable-shared --enable-gpl --enable-version3 --enable-libx264 --enable-libx265
make -j8
sudo make install
```
### ~~Avidemuxのインストール~~ (現versionでは未使用)
```
sudo add-apt-repository ppa:rock-core/qt4
sudo apt install libqt4-dev
sudo apt install qttools5-dev-tools qtbase5-dev
sudo apt install libasound2-dev
sudo apt install sqlite libsqlite-dev
cd ~/tools
wget https://sourceforge.net/projects/avidemux/files/avidemux/2.7.8/avidemux_2.7.8.tar.gz
tar -zxvf avidemux_2.7.8.tar.gz
cd avidemux_2.7.8
export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/usr/lib/x86_64-linux-gnu/pkgconfig
bash bootStrap.bash
sudo cp -R install/usr/* /usr/ **
```
-  ~~Avidemuxの動作確認~~ (現versionでは未使用)
```
avidemux3_cli
```
- ~~いろいろと出てくればOK~~ (現versionでは未使用)

### pyenvディレクトリ作成
```
mkdir ~/workspace
cd ~/workspace
git clone https://github.com/t-ogura/SplatoonKillDigestMakerPy.git
cd SplatoonKillDigestMakerPy
pyenv virtualenv 3.6.13 KDM
pyenv local KDM
```
### python環境構築
```
sudo apt install pip
cd ~/workspace/SplatoonKillDigestMakerPy
pip install --upgrade pip
pip install -r requirements.txt
```

### Docker環境について
Docker環境では、libopencv-devのインストールが必要なようです。
（はりぃ様情報提供ありがとうございます。）

# FAQ
### キルシーンを一部検出できていない
　元動画の画質が悪い場合正しく検出できないことがあります。
「init.txt」にあるTAMPLATE_MATCHING_THRESHOLDの値を低くすることで、
今まで検出できなかったものが検出できるようになる場合があります。
ただし下げ過ぎると誤検出が増えるので注意。
推奨は0.80～0.85程度になります。

　※可変フレームレートの動画の場合、正しい位置でキルシーンを切り出せない不具合を確認しています。
現在対応中ですが、固定フレームレートの動画に変換することで解決できそうです。
こちらで対応中です。https://github.com/t-ogura/SplatoonKillDigestMakerPy/issues/1

### 連続キルのシーンだけ抽出したい（1体キルは無視したい）
　「init.txt」にあるCANDIDATE_FRAME_NUMを5.0より大きく（5.1, 6.0等）にすると、
単独キルの検出が誤認識扱いとされ、連続キルのシーンのみ抽出が出来るようになります。
ただし、同時に2体倒した等のシーンは単独キルと同様に5秒間しか表示がないため、
連続キルとしての抽出にはなりません。

### キルシーンの切り出しの時間長を長く（短く）したい
　「init.txt」にあるADDITIONAL_TIME_BEFORE_KILLとADDITIONAL_TIME_AFTER_KILLを調節してみてください。
その場合、この2つの値の合計値がCONNECTING_INTERVALより大きくならないように気を付けてください。
CONNECTING_INTERVALの値を超えてしまうと、完成動画でまれに時間の巻き戻りが起きます。
その場合はCONNECTING_INTERVALの値を大きくして調整してください。

### エンコードのコーデックを指定したい
　「init.txt」にあるVIDEO_CODECで指定することが可能です。
ffmpegで利用可能なコーデックを指定できます。
ただし、デフォルトでffmpegに搭載されているコーデック以外は、
ffmpegの環境構築時に設定する必要があります。
上記の環境構築例では、libx264のほかにlibx265が使えるようにしていますので、ご活用ください。
MicrosoftのInsider Programのdevチャネルに加入しているとWSL2でもnvenc使えそうですよ。（上級者向け）
あとはWSL2からWindows環境のコマンドが実行できるらしいので、
うまく活用すればグラボを使ったエンコードが出来そうですね。（上級者向け）

## nvencを使うためのヒント (上級者向け)
- https://qiita.com/yamakenjp/items/7474f210efd82bb28490
- https://takake-blog.com/wsl-nvidia-cuda/
- https://qiita.com/ksasaki/items/ee864abd74f95fea1efa
