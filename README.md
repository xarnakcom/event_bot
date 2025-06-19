# event_bot

## Описание
Бот с тремя ролями пользователей:
- Администраторы создают события с датой, местом, заказчиком, бригадиром и рабочими.
- Бригадир получает событие, пишет комментарий с инструментами.
- Рабочие получают уведомление и подтверждают участие кнопками Да/Нет.

## Установка

✅ Шаг 1: Установить зависимости на сервере
```
sudo apt update
sudo apt install python3 python3-venv python3-pip git -y
```
✅ Шаг 2: Клонировать репозиторий
```
cd ~
git clone https://github.com/xarnakcom/event_bot.git
cd event_bot
```
✅ Шаг 3: Создать виртуальное окружение и установить зависимости
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Если файла requirements.txt нет, создай его со следующим содержимым:
```
aiogram
python-dotenv
aiohttp
aiosqlite
```
И снова выполни:
```
pip install -r requirements.txt
```
✅ Шаг 4: Настроить .env
Создай файл .env:
```
nano .env
```
И вставь туда:
```
BOT_TOKEN=Заменить_твой_токен_бота
OPENWEATHER_TOKEN=Заменить_твой_ключ_OpenWeatherMap
```
Сохрани (Ctrl + O, Enter, Ctrl + X).
```
git clone https://github.com/your/repo.git
cd repo/event_bot
```
✅ Шаг 5: Протестировать вручную
```
source venv/bin/activate
python main.py
```
Если бот запустился — отлично! Останови его: Ctrl + C
✅ Шаг 6: Настроить автозапуск через systemd
Создай юнит-файл:
```
sudo nano /etc/systemd/system/eventbot.service
```
Вставь туда:
```
[Unit]
Description=Telegram Event Bot
After=network.target

[Service]
WorkingDirectory=/home/Заменить_имя_пользователя/event_bot
ExecStart=/home/Заменить_имя_пользователя/event_bot/venv/bin/python3 main.py
Restart=always
Environment=BOT_TOKEN=Заменить_токен
Environment=OPENWEATHER_TOKEN=Заменить_ключ

[Install]
WantedBy=multi-user.target```
✅ Шаг 7: Запустить и включить бота
```
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl start eventbot.service
sudo systemctl enable eventbot.service
```
✅ Шаг 8: Проверить статус
```
sudo systemctl status eventbot.service
```
Если всё хорошо, ты увидишь строчки типа:
```
Active: active (running)
```
