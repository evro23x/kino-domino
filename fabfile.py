from fabric.api import *

env.hosts = ['192.168.23.3']
env.user = 'vagrant'
env.key_filename = '/Users/macpro/vagrant-vm/test_srv_3/.vagrant/machines/default/virtualbox/private_key'

# @task
# def some_task():
#     fabtools.vagrant.machines()


# update и upgrade системы
# установка пострги
# создание базы и доступов к базе
# клонирование репозитория гита
# создание виртуального окружения
# включение виртуального окружения
# установка пакетов и зависимостей
# копирование конфигов(база и алембик) из гитигнора
# запуск миграции
# запуск парсера
# запуск телеграмм бота


def load_vm():
    local("cd ~/vagrant-vm/test_srv_3/ && vagrant destroy -f")
    local("rm -rf ~/vagrant-vm/test_srv_3/")

    local("mkdir ~/vagrant-vm/test_srv_3/ && cd ~/vagrant-vm/test_srv_3/ && vagrant init ubuntu/trusty64")
    local("rm ~/vagrant-vm/test_srv_3/Vagrantfile")
    local("cp ~/vagrant-vm/Vagrantfile ~/vagrant-vm/test_srv_3/")
    local("cd ~/vagrant-vm/test_srv_3/ && ssh-keygen -R 192.168.23.3")
    local("cd ~/vagrant-vm/test_srv_3/ && vagrant up")
    local("cd ~/vagrant-vm/test_srv_3/ && vagrant reload")
    local("cd ~/vagrant-vm/test_srv_3/ && vagrant reload")


def prepare_soft():
    sudo("apt-get install postgresql -y")


def pg():
    run("sudo -u postgres psql -c 'CREATE DATABASE db_name;'")
    run("sudo -u postgres psql -c \"CREATE USER username WITH password 'password';\"")
    run("sudo -u postgres psql -c 'GRANT ALL privileges ON DATABASE db_name TO username;'")
    sudo("echo \"listen_addresses = '*'\" >> /etc/postgresql/9.3/main/postgresql.conf")
    sudo("echo \"host all all 0.0.0.0/0 md5\" >> /etc/postgresql/9.3/main/pg_hba.conf")
    sudo("service postgresql stop && service postgresql start")

    # with cd("/tmp"):
    #     run("ls -la")


def main():
    load_vm()
    prepare_soft()
    pg()

    # local("cd ~/vagrant-vm/test_srv_2/ && ls -la")
    # local("cd / && ls -la")


# def q1():
#     run("ls -la")
#     run("cd / && ls -la")
