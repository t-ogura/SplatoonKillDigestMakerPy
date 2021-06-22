# SplatoonKillDigestMakerPy
Python version of the SplatoonKillDigestMaker

# 環境
- Ubuntu 20.04 on wsl2
- Python 3.6.13



# 環境構築メモ
### 自分の環境構築時の手順を記載しておく
- WSL2およびUbuntuはインストール済みとする
- gitのインストール
```
sudo apt install git
```
- コンパイラインストール
```
sudo apt install build-essential
```
- その他必要なライブラリ
```
sudo apt install -y libbz2-dev libreadline-dev libssl-dev libsqlite3-dev cmake
```
- pyenv virtualenv python環境インストール
```
git clone https://github.com/yyuu/pyenv.git ~/.pyenv
git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
CONFIGURE_OPTS=--enable-shared pyenv install 3.9.5
```
- ffmpegインストール
```
sudo apt install yasm
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
./configure --enable-shared --disable-gpl --enable-version3
make -j8
sudo make install
```
- Avidemuxのインストール
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
- Avidemuxの動作確認
```
avidemux3_cli
```
- いろいろと出てくればOK

- pyenvディレクトリ作成
```
mkdir ~/workspace
cd workspace
git clone https://github.com/t-ogura/SplatoonKillDigestMakerPy.git
cd SplatoonKillDigestMakerPy
pyenv virtualenv 3.9.5 KDM
pyenv local KDM
```
- python環境構築
```
pip install --upgrade pip
pip install -r requirements.txt
```

