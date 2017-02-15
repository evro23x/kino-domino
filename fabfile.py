from fabric.api import *
import time
import socket

env.hosts = ['192.168.23.3']
env.user = 'vagrant'
env.key_filename = '/Users/macpro/vagrant-vm/test_srv_3/.vagrant/machines/default/virtualbox/private_key'


# update и upgrade системы
# установка пострги
# создание базы и доступов к базе
# клонирование репозитория гита
# создание виртуального окружения
# включение виртуального окружения
# установка пакетов и зависимостей
# копирование конфигов(база и алембик) из гитигнора
# запуск миграций
# запуск парсера
# запуск телеграмм бота


def wait_for_ssh():
    s = socket.socket()
    address = '192.168.23.3'
    port = 22
    while True:
        time.sleep(1)
        try:
            s.connect((address, port))
            return
        except Exception:
            print("failed to connect to {}:{}".format(address, port))
            pass


def reload_vm():
    local("cd ~/vagrant-vm/test_srv_3/ && vagrant destroy -f")
    local("rm -rf ~/vagrant-vm/test_srv_3/")
    local("mkdir ~/vagrant-vm/test_srv_3/ && cd ~/vagrant-vm/test_srv_3/ && vagrant init ubuntu/xenial64")
    local("rm ~/vagrant-vm/test_srv_3/Vagrantfile")
    local("cp ~/vagrant-vm/Vagrantfile ~/vagrant-vm/test_srv_3/")
    local("cd ~/vagrant-vm/test_srv_3/ && ssh-keygen -R 192.168.23.3")
    local("cd ~/vagrant-vm/test_srv_3/ && vagrant up")


def setup_pg():
    wait_for_ssh()
    sudo("apt-get install postgresql python-psycopg2 libpq-dev -y")
    sudo("apt-get install libxml2 libxslt1.1 libxml2-dev libxslt1-dev python-libxml2 -y")
    sudo("apt-get install python-libxslt1 python-dev python-setuptools build-essential libssl-dev libffi-dev -y")
    run("sudo -u postgres psql -c 'CREATE DATABASE db_name;'")
    run("sudo -u postgres psql -c \"CREATE USER username WITH password 'password';\"")
    run("sudo -u postgres psql -c 'GRANT ALL privileges ON DATABASE db_name TO username;'")
    sudo("echo \"listen_addresses = '*'\" >> /etc/postgresql/9.3/main/postgresql.conf")
    sudo("echo \"host all all 0.0.0.0/0 md5\" >> /etc/postgresql/9.3/main/pg_hba.conf")
    sudo("service postgresql stop && service postgresql start")


def unpack_project():
    sudo("apt-get install git -y")
    run("git clone https://github.com/evro23x/kino-domino.git")
    with cd("kino-domino/"):
        put('~/vagrant-vm/config.py', 'config.py')
        put('~/vagrant-vm/alembic.ini', 'alembic.ini')
    run("mkdir ~/venvs")
    sudo("apt-get install python3.4-venv -y")
    run("cd venvs && python3 -m venv kino-domino")
    run("source venvs/kino-domino/bin/activate")
    run("cd kino-domino && pip install -r requirements.txt")
    run("cd kino-domino && alembic upgrade head")


def deploy_from_github():
    pass


def bootstrap():
    reload_vm()
    setup_pg()
    unpack_project()


def deploy():
    deploy_from_github()
