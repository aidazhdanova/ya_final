Социальная сеть
=====
Описание:
=====
Проект создан в рамках учебного курса Яндекс.Практикум.
Основной упор делался на Backend, дизайн страдает :))

Пользователи могут публиковать записи, подписываться на любимых авторов, отмечать понравившиеся записи и оставлять комментарии

Запустить проект можно следующим образом:
----------


1. Клонировать репозиторий и перейти в него:
```bash
git clone https://github.com/aidazhdanova/ya_final.git
cd api_final_yatube
```
2. Cоздать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/Scripts/activate
```
3. Установить зависимости ```requirements.txt```:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
4. Выполнить миграции:
```bash
python manage.py migrate
```
5. Запустить проект:
```bash
python manage.py runserver
```
----------