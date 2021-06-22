# SplatoonKillDigestMakerPy
Python version of the SplatoonKillDigestMaker

# 環境
- Ubuntu 20.04 on wsl2
- Python 3.9.4



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
sudo apt install -y libbz2-dev libreadline-dev libssl-dev libsqlite3-dev
```
- pyenv virtualenv python環境インストール
```
git clone https://github.com/yyuu/pyenv.git ~/.pyenv
git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
CONFIGURE_OPTS=--enable-shared pyenv install 3.9.5
```
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

