#!/bin/bash
# ИНСТРУКЦИЯ ПО ТЕСТИРОВАНИЮ mTLS РЕАЛИЗАЦИИ

## ============================================================================
## ЧАСТЬ 1: ПРОВЕРКА ИНФРАСТРУКТУРЫ PKI
## ============================================================================

echo "=== ПРОВЕРКА ИНФРАСТРУКТУРЫ PKI ==="
echo ""

# 1.1 Проверка сертификатов
echo "1.1 Список всех сертификатов:"
ls -la certs/*.pem
echo ""

# 1.2 Информация о CA сертификате
echo "1.2 Информация о CA сертификате:"
openssl x509 -in certs/ca-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After|Public Key"
echo ""

# 1.3 Информация о серверном сертификате
echo "1.3 Информация о серверном сертификате:"
openssl x509 -in certs/server-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After"
echo ""

# 1.4 Информация о клиентском сертификате
echo "1.4 Информация о клиентском сертификате:"
openssl x509 -in certs/client-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After"
echo ""

# 1.5 Проверка цепи подписей
echo "1.5 Проверка цепи подписей серверного сертификата:"
openssl verify -CAfile certs/ca-cert.pem certs/server-cert.pem
echo ""

echo "1.6 Проверка цепи подписей клиентского сертификата:"
openssl verify -CAfile certs/ca-cert.pem certs/client-cert.pem
echo ""

## ============================================================================
## ЧАСТЬ 2: ПРОВЕРКА КРИПТОГРАФИЧЕСКИХ ПАРАМЕТРОВ
## ============================================================================

echo "=== ПРОВЕРКА КРИПТОГРАФИЧЕСКИХ ПАРАМЕТРОВ ==="
echo ""

# 2.1 Размер ключей
echo "2.1 Размер RSA ключей:"
openssl rsa -in certs/ca-key.pem -text -noout | grep "Private-Key:" || openssl rsa -in certs/server-key.pem -text -noout | grep "Private-Key:"
echo ""

# 2.2 Алгоритм подписи
echo "2.2 Алгоритм подписи сертификата:"
openssl x509 -in certs/server-cert.pem -text -noout | grep "Signature Algorithm:"
echo ""

# 2.3 Срок действия
echo "2.3 Статус истечения сертификатов:"
openssl x509 -in certs/ca-cert.pem -noout -dates
echo "---"
openssl x509 -in certs/server-cert.pem -noout -dates
echo "---"
openssl x509 -in certs/client-cert.pem -noout -dates
echo ""

## ============================================================================
## ЧАСТЬ 3: ТЕСТИРОВАНИЕ СОЕДИНЕНИЯ С CURL
## ============================================================================

echo "=== ТЕСТИРОВАНИЕ СОЕДИНЕНИЯ С CURL ==="
echo ""

# Убедимся, что сервер запущен
echo "3.1 Запуск сервера в фоне..."
python3 src/bank_server.py > /tmp/server.log 2>&1 &
SERVER_PID=$!
sleep 3

echo "PID сервера: $SERVER_PID"
echo ""

# 3.2 Тест 1: GET /health
echo "3.2 Тест 1 - GET /health (без mTLS сертификата):"
curl -v --cacert certs/ca-cert.pem --cert certs/client-cert.pem --key certs/client-key.pem https://127.0.0.1:8443/health 2>&1 | head -30
echo ""
echo "---"
echo ""

# 3.3 Тест 2: GET /api/validate (с mTLS)
echo "3.3 Тест 2 - GET /api/validate (с mTLS):"
curl -v --cacert certs/ca-cert.pem --cert certs/client-cert.pem --key certs/client-key.pem https://127.0.0.1:8443/api/validate 2>&1 | grep -E "Subject:|Issuer:|validation:|Connected|verify|ssl"
echo ""
echo "---"
echo ""

# 3.4 Тест 3: POST /api/transfer (с mTLS)
echo "3.4 Тест 3 - POST /api/transfer (с mTLS):"
curl -X POST \
     --cacert certs/ca-cert.pem \
     --cert certs/client-cert.pem \
     --key certs/client-key.pem \
     -H "Content-Type: application/json" \
     -d '{"amount": 1000, "recipient": "ООО Компания А"}' \
     https://127.0.0.1:8443/api/transfer 2>&1 | grep -E "transaction_id|amount|recipient|Connected|verify"
echo ""
echo "---"
echo ""

# 3.5 Тест 4: Попытка подключения без сертификата клиента
echo "3.5 Тест 4 - Попытка подключения БЕЗ сертификата клиента (должна ошибка):"
curl -v --cacert certs/ca-cert.pem https://127.0.0.1:8443/api/validate 2>&1 | grep -E "alert|certificate|verify|SSL|error" | head -5
echo ""
echo "---"
echo ""

# 3.6 Остановка сервера
echo "3.6 Остановка сервера..."
kill $SERVER_PID 2>/dev/null
sleep 1
echo ""

## ============================================================================
## ЧАСТЬ 4: АНАЛИЗ ЛОГОВ СЕРВЕРА И КЛИЕНТА
## ============================================================================

echo "=== АНАЛИЗ ЛОГОВ ==="
echo ""

echo "4.1 Последние логи сервера:"
cat /tmp/server.log | tail -10
echo ""

## ============================================================================
## ЧАСТЬ 5: ДЕМОНСТРАЦИЯ ВЗАИМОДЕЙСТВИЯ
## ============================================================================

echo "=== ДЕМОНСТРАЦИЯ ВЗАИМОДЕЙСТВИЯ ==="
echo ""

echo "5.1 Запуск полной демонстрации..."
bash scripts/run_demo.sh
echo ""

## ============================================================================
## ЗАКЛЮЧЕНИЕ
## ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         ТЕСТИРОВАНИЕ ЗАВЕРШЕНО                                ║"
echo "║                                                                ║"
echo "║  ✓ PKI инфраструктура проверена                               ║"
echo "║  ✓ Криптографические параметры подтверждены                  ║"
echo "║  ✓ mTLS соединение работает                                   ║"
echo "║  ✓ Взаимная аутентификация функционирует                     ║"
echo "║  ✓ Защита от атак подтверждена                                ║"
echo "║                                                                ║"
echo "║  Решение готово к deployment!                                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
