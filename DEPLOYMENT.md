# Развертывание тестовой среды (VM)

Так как наша архитектура включает в себя множество тяжеловесных Big Data компонентов (Kafka, Spark, PostgreSQL, ClickHouse, Airflow, Superset, MinIO), требования к тестовой виртуальной машине (VM) должны быть соответствующими.

## Рекомендуемые характеристики тестовой VM
Для комфортного локального тестирования (чтобы контейнеры не падали по OOM - Out of Memory) рекомендуется создать VM со следующими параметрами:
- **ОС:** Ubuntu 22.04 LTS (или 20.04 LTS).
- **CPU:** Минимум 4 ядра (рекомендуется 8 ядер).
- **RAM:** Минимум 16 ГБ (рекомендуется 24-32 ГБ). *Меньше 16 ГБ — контейнеры (особенно Spark, Kafka, Airflow и Superset) могут не запуститься или работать крайне нестабильно.*
- **SSD:** Минимум 50 ГБ свободного места.

## Как подготовить VM

1. **Подключитесь к VM по SSH.**
2. **Установите Docker и Docker Compose:**

```bash
# Обновляем пакеты
sudo apt update && sudo apt upgrade -y

# Устанавливаем необходимые утилиты
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y

# Добавляем ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавляем репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Устанавливаем Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Добавляем пользователя в группу docker (чтобы не писать sudo)
sudo usermod -aG docker $USER
```
*(После добавления в группу docker нужно перезайти на сервер или выполнить `newgrp docker`)*

## Как развернуть и обновлять код

Для вашего удобства в корне проекта создан скрипт `deploy.sh`.

### Первичный запуск (Шаг за шагом):

**Шаг 1. Получение кода на сервер:**
Зайдите на вашу VM и склонируйте этот репозиторий (подставьте правильный URL вашего репозитория):
```bash
# Установка git, если он еще не установлен
sudo apt install git -y

# Клонирование репозитория (по HTTPS)
git clone https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/ВАШ_РЕПОЗИТОРИЙ.git

# Переход в папку проекта
cd ВАШ_РЕПОЗИТОРИЙ
```

**Шаг 2. Настройка секретов (БД и MQTT):**
Вам необходимо создать файл с настройками окружения, чтобы пароли от вашей MQTT не утекли в публичный доступ.
```bash
# Копируем пример файла настроек
cp .env.example .env

# Открываем файл для редактирования (вставьте ваш пароль в поле MQTT_PASSWORD)
nano .env
```
*(Для сохранения изменений в `nano` нажмите `Ctrl+O`, `Enter`, затем `Ctrl+X` для выхода).*

**Шаг 3. Запуск автоматического развертывания:**
Мы подготовили скрипт, который сам соберет все образы и запустит `docker compose up -d`.
```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем развертывание
./deploy.sh
```

Скрипт автоматически:
- Соберет необходимые кастомные Docker-образы (Airflow, MQTT-Bridge).
- Поднимет все сервисы (`docker compose up -d`).

### Как обновлять код:
Когда вы вносите изменения в код (например, обновляете Python-скрипты, SQL-файлы или Dockerfile), вам достаточно:
1. Подтянуть изменения из Git (`git pull`).
2. Снова запустить `./deploy.sh`.

Скрипт корректно остановит старые контейнеры, пересоберет образы с новым кодом и запустит их заново, не удаляя при этом накопленные данные в базах данных (volume-диски сохраняются).
