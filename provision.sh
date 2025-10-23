#!/usr/bin/env bash
set -e

# 1) Pacotes básicos
sudo apt-get update -y
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release \
  git apache2 mysql-server python3-venv python3-pip

# 2) Docker (namespaces/cgroups p/ CPU/Mem/IO)
# chave docker
if ! [ -f /usr/share/keyrings/docker-archive-keyring.gpg ]; then
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
fi
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker vagrant
sudo systemctl enable --now docker

# 3) Pastas de log
sudo mkdir -p /var/log/jobs
sudo chown vagrant:vagrant /var/log/jobs

# 4) MySQL: cria DB e usuário simples (somente para laboratório)
sudo systemctl enable --now mysql
sudo mysql -e "CREATE DATABASE IF NOT EXISTS execdb DEFAULT CHARACTER SET utf8mb4;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'execuser'@'localhost' IDENTIFIED BY 'execpass';"
sudo mysql -e "GRANT ALL PRIVILEGES ON execdb.* TO 'execuser'@'localhost'; FLUSH PRIVILEGES;"

# 5) App Python
cd /vagrant/app
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6) Inicializa tabelas
mysql -uexecuser -pexecpass execdb < db_init.sql

# 7) Apache como reverse proxy (opcional; pode usar Flask direto na :5000)
sudo a2enmod proxy proxy_http
sudo bash -c 'cat >/etc/apache2/sites-available/000-default.conf' <<'EOF'
<VirtualHost *:80>
  ServerName localhost
  ProxyPreserveHost On
  ProxyPass / http://127.0.0.1:5000/
  ProxyPassReverse / http://127.0.0.1:5000/
  ErrorLog ${APACHE_LOG_DIR}/proj2_error.log
  CustomLog ${APACHE_LOG_DIR}/proj2_access.log combined
</VirtualHost>
EOF
sudo systemctl restart apache2
