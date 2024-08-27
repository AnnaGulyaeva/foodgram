# Foodgram
## _Сайт для публикации рецептов_

[![Workflow](https://github.com/AnnaGulyaeva/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/AnnaGulyaeva/foodgram/actions/workflows/main.yml)

Foodgram — это сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Стек используемых технологий
- Python 3.9
- Django REST Framework 3.12.4
- Djosier 2.1.0
- Django 3.2.3
- React 17.0.2
- Reportlab 4.2.2

##  Как развернуть проект на Ubuntu 22.04
### Очистить кеши
_Очистить кеш npm_
```sh
npm cache clean --force
```
_Очистить кеш APT_
```sh
sudo apt clean
```
_Удалить старые системные логи_
```sh
 sudo journalctl --vacuum-time=1d
  ```
  
### Устанавить `Docker Compose`
```sh
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin 
```

### Подготовить директорию `foodgram`
_Создать директорию foodgram/_
```sh
mkdir foodgram
```
_Добавить вfoodgram/ файл docker-compose.production.yml_
```sh
scp -i path_to_SSH/SSH_name docker-compose.production.yml \
    username@server_ip:/home/username/foodgram
```
_Добавить в foodgram/ файл .env_
```sh
scp -i path_to_SSH/SSH_name .env \
    username@server_ip:/home/username/foodgram
```
- `path_to_SSH` — путь к файлу с SSH-ключом;
- `SSH_name` — имя файла с SSH-ключом (без расширения);
- `username` — ваше имя пользователя на сервере;
- `server_ip` — IP вашего сервера.

### Запустить `Docker Compose`
_Запустить Docker Compose в режиме демона_
_Выполните эту команду на сервере в папке `foodgram/`_
```sh
sudo docker compose -f docker-compose.production.yml up -d 
```
_Выполнить миграции_
```sh
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
_Собрать статические файлы бэкенда_
```sh
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```
_Скопировать их в `/backend_static/static/`_
```sh
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

### Настроить Nginx:
_На сервере в редакторе nano открыть конфиг Nginx_
```sh
nano /etc/nginx/sites-enabled/default
```
_Изменить настройки location в секции server_
```sh
    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8080;
    }
```
_Перезагрузить конфиг Nginx_
```sh
sudo service nginx reload 
```

### Как заполнить базу данных ингридиентами и тегами
_Заполнение таблицы ингредиентами_
```sh
python manage.py add_ingredients
```
_Заполнение таблицы тегами_
```sh
python manage.py add_tags
```


##  Как заполнить .env
- `ALLOWED_HOSTS` — доменное имя сайта и ip-адрес сервера, на котором запускается проект,
записывать через разделитель "/" (по умолчанию localhost или 127.0.0.1);
- `DEBUG` — включить или выключить режим отладки, true или false (по умолчанию false);
- `SECRET_KEY` — токен для Джанго-приложения;
- `DATABASE` — какая база данных используется (по умолчанию PostgreSQL).

[Проект Фудграм](https://foodgram81.hopto.org)
[Документация на API](https://foodgram81.hopto.org/api/docs/)

## Автор

Гуляева Анна, студентка Яндекс Практикума, программа "Python разработчик".
