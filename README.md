# Discord OSINT Transform for Maltego

Discord OSINT Transform — это локальная трансформация для Maltego, которая собирает открытую информацию о пользователях Discord через API Discord Sensor.
[![Discord OSINT Transform Demo](https://img.youtube.com/vi/dQw4w9WgXcQ/0.jpg)](https://www.youtube.com/shorts/H9T0RFYJEAc)
---

## Возможности

- **Поиск по Discord ID или username**
- **Профиль пользователя** (ID, статус, аватар)
- **История никнеймов** с привязкой к серверам
- **История событий** (входы/выходы с серверов)
- **История голосовых сессий** (каналы, время, длительность)
- **Список друзей** (ID, username, время онлайн)
- **Запуск через Docker**

---

## Требования

- **Docker**
- **Maltego** (Community+)

---

## Быстрый старт

1. Скачать Docker образ

```bash
docker pull realsh1ro/maltego-discord:latest

2. Создание трансформации в Maltego
Поле	          Значение
Display Name	→ Discord OSINT
Input Entity Type	→ maltego.Phrase
Command	→ docker
Arguments	→ run --rm -i realsh1ro/maltego-discord:latest FullDiscordOSINT
Working directory →	(по умолчанию)
Output Entity Types →	any
Использование
Создать новый граф в Maltego

Добавить Phrase на граф

В поле Text ввести Discord ID

Run Transform → Discord OSINT

Профит: после запуска трансформации на графе появятся:

Entity	Данные
Person→ Профиль пользователя (Discord ID, статус, аватар)
Person→	Каждый знакомый пользователя с его ID, аватаром, временем онлайн
Phrase→	История никнеймов с привязкой к серверам
Phrase→	История событий (входы/выходы с серверов)
Phrase→	История голосовых сессий (канал, длительность, время)
Affiliation→ Серверы, на которых состоит пользователь

Как получить Discord ID?
В Discord: Настройки → Дополнительно → Режим разработчика (включить)

Правый клик по пользователю → Копировать ID

Трансформация не находит пользователя?
Убедись, что ввел корректный Discord ID

Лицензия
MIT License — свободно используй, модифицируй и делись!

Благодарности
Discord Sensor за бесплатный доступ к API

emptiness_and_destruction (Зло) за идею

Связь
Автор: sh1ro

Discord: shirov3_

GitHub: SH1ROdev

⭐ Если пригодилась трансформация — поставь звезду на репо!
