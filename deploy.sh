#!/bin/bash

# Скрипт для развертывания и обновления тестовой среды

echo "========================================="
echo "🚀 Начало развертывания Data Pipeline"
echo "========================================="

# 1. Проверка наличия Docker
if ! command -v docker &> /dev/null
then
    echo "❌ Ошибка: Docker не установлен. Пожалуйста, установите Docker и Docker Compose."
    exit 1
fi

echo "✅ Docker найден."

# 2. Остановка текущих контейнеров (если они запущены)
echo "🛑 Остановка текущих сервисов..."
docker compose down

# 3. Пересборка образов
# Ключ --build заставляет Docker Compose пересобрать образы (Airflow, Python Bridge),
# если вы меняли код в папках, которые в них копируются.
echo "🔨 Сборка Docker образов..."
docker compose build

# 4. Запуск среды
echo "🟢 Запуск всех сервисов в фоновом режиме..."
docker compose up -d

echo "========================================="
echo "🎉 Развертывание завершено!"
echo "========================================="
echo ""
echo "Полезные команды:"
echo "- Просмотр статуса сервисов: docker compose ps"
echo "- Просмотр логов: docker compose logs -f [имя_сервиса]"
echo "- Остановка среды: docker compose down"
echo ""
echo "Доступы к UI (после того как сервисы поднимутся):"
echo "- Airflow: http://<ip_вашей_vm>:8081 (admin/admin)"
echo "- Superset: http://<ip_вашей_vm>:8088 (admin/admin)"
echo "- Spark Master: http://<ip_вашей_vm>:8080"
echo "- MinIO (S3): http://<ip_вашей_vm>:9091 (minioadmin/minioadmin)"
