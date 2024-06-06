#!/bash/bin

scp AlphaBot2.py leandro@leandro.local:/home/leandro/Documents

scp PCA9685.py leandro@leandro.local:/home/leandro/Documents

scp main.py leandro@leandro.local:/home/leandro/Documents

scp requirements.txt leandro@leandro.local:/home/leandro/Documents

ssh leandro@leandro.local sudo apt-get install libpcap-dev
ssh leandro@leandro.local sudo apt install -y python3-libcamera python3-kms++ libcap-dev

ssh leandro@leandro.local python3 -m venv --system-site-packages /home/leandro/Documents

ssh leandro@leandro.local /home/leandro/Documents/bin/pip install --upgrade pip
ssh leandro@leandro.local /home/leandro/Documents/bin/pip install -r /home/leandro/Documents/requirements.txt

