## Mr.Nastolkin_Bot
Play with your friends! 
## [I want to try!](https://t.me/mr_nastolkin_bot)

### Install (Debian/Centos - like) require Python >= 3.10 version
```bash
git clone https://github.com/rombintu/nastolkinbot.git /opt/nastolkinbot
cd /opt/nastolkinbot
python3 -m venv venv
source ./venv/bin/activate
pip install -r deps.txt
sudo cp system/nastolkinbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now nastolkinbot.service
```

### Install (Docker)
```bash
docker build -t nastolkinbot:0.3.9 .
docker run -d -e 'BOT_TOKEN=<YOUR_TOKEN>' -name nastolkinbot nastolkinbot:0.3.0
```

### Screenshot
![img](./screenshots/image_1.png)