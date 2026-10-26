<div align="center">

# MODE MOB

**Новые существа для Minecraft — начиная с гигантского тарантула**

<br />

![NeoForge](https://img.shields.io/badge/NeoForge_21.1-F68A1E?style=for-the-badge&logoColor=white)
![Minecraft](https://img.shields.io/badge/Minecraft_1.21.1-62B47A?style=for-the-badge&logo=minecraft&logoColor=white)
![Java](https://img.shields.io/badge/Java_21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![Gradle](https://img.shields.io/badge/Gradle-02303A?style=for-the-badge&logo=gradle&logoColor=white)

![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

</div>

<br />

## О моде

MODE MOB добавляет в мир новых существ с собственными анимированными моделями и поведением.

Мод из серии MINECRAFT-MODE: худ и лечение — [MINECRAFT-MODE-HUD](https://github.com/KUZURAKI/MINECRAFT-MODE-HUD), транспорт — [MINECRAFT-MODE-TECH](https://github.com/KUZURAKI/MINECRAFT-MODE-TECH), тёмный персонаж — [MINECRAFT-MODE-DARKLORD](https://github.com/KUZURAKI/MINECRAFT-MODE-DARKLORD). Каждый мод работает сам по себе.

## Гигантский тарантул

<img src="docs/img/tarantula.png" width="420" />

| Параметр | Значение |
| --- | --- |
| Здоровье | 220 |
| Урон | 10 |
| Появление | Верхний мир, ночью и в темноте, вместе с обычными пауками, но гораздо реже |
| Добыча | 4–10 нитей и 2–5 паучьих глаз |

- Вокруг тарантула появляется стая из 8–15 пауков и пещерных пауков и 40–70 паутин.
- Заметив игрока, он переходит на быстрый бег.
- Стреляет паутиной: попадание сильно замедляет и оставляет паутину на месте.
- Анимации покоя, ходьбы и атаки.

Яйцо призыва лежит во вкладке творческого режима «Яйца призыва».

## Установка

1. Установите **NeoForge 1.21.1** (версия 21.1.x).
2. Скачайте `modemob-0.1.0.jar` и положите в папку `mods` вашей игры.
3. Запустите игру.

## Настройки

Файл `config/modemob-common.toml` создаётся после первого запуска: `spawnRarity` — насколько редко появляется тарантул, чем больше, тем реже.

## Сборка

```bash
./gradlew build
```

Готовый файл появится в `build/libs/modemob-0.1.0.jar`. JDK 21 Gradle скачает сам.

<br />

<div align="center">

Сделано **ZEDKODEX**

</div>
