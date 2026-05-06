#!/bin/bash

# Скрипт для запуска mTLS демонстрации
# Не требует установки зависимостей - использует встроенные Python библиотеки

PROJECT_DIR="/Users/srgrsj/Documents/learn/cybersecurity/security-mtls"

echo "=== Запуск mTLS демонстрации ==="
echo ""
echo "Запуск сервера банка в фоне..."
python3 "$PROJECT_DIR/src/bank_server.py" &
SERVER_PID=$!

# Даем серверу время на запуск
sleep 2

echo ""
echo "=== Запуск клиента партнера ==="
echo ""

python3 "$PROJECT_DIR/src/partner_client.py"

# Останавливаем сервер
echo ""
echo "Остановка сервера..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo "=== Демонстрация завершена ==="
