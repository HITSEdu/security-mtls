#!/bin/bash

# Скрипт для генерирования CA и mTLS сертификатов

CERTS_DIR="../certs"
DAYS=365

echo "=== Генерирование mTLS сертификатов ==="

# 1. Создаем CA (Certificate Authority) приватный ключ
echo "1. Генерируем CA приватный ключ..."
openssl genrsa -out $CERTS_DIR/ca-key.pem 2048

# 2. Создаем CA сертификат
echo "2. Генерируем CA сертификат..."
openssl req -new -x509 -days $DAYS -key $CERTS_DIR/ca-key.pem -out $CERTS_DIR/ca-cert.pem \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=HITsoff Bank/CN=HITsoff-CA"

# 3. Создаем приватный ключ сервера (банк)
echo "3. Генерируем приватный ключ сервера (банк)..."
openssl genrsa -out $CERTS_DIR/server-key.pem 2048

# 4. Создаем CSR (Certificate Signing Request) для сервера
echo "4. Генерируем CSR для сервера..."
openssl req -new -key $CERTS_DIR/server-key.pem -out $CERTS_DIR/server.csr \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=HITsoff Bank/CN=bank.hitsoff.local"

# 5. Подписываем сертификат сервера CA с правильным SAN
echo "5. Подписываем сертификат сервера CA..."
openssl x509 -req -days $DAYS -in $CERTS_DIR/server.csr \
    -CA $CERTS_DIR/ca-cert.pem -CAkey $CERTS_DIR/ca-key.pem -CAcreateserial \
    -out $CERTS_DIR/server-cert.pem \
    -extfile <(printf "subjectAltName=DNS:bank.hitsoff.local,DNS:localhost,IP:127.0.0.1,IP:0.0.0.0")

# 6. Создаем приватный ключ клиента (партнер)
echo "6. Генерируем приватный ключ клиента (партнер)..."
openssl genrsa -out $CERTS_DIR/client-key.pem 2048

# 7. Создаем CSR для клиента
echo "7. Генерируем CSR для клиента..."
openssl req -new -key $CERTS_DIR/client-key.pem -out $CERTS_DIR/client.csr \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=Partner Corp/CN=partner.hitsoff.local"

# 8. Подписываем сертификат клиента CA
echo "8. Подписываем сертификат клиента CA..."
openssl x509 -req -days $DAYS -in $CERTS_DIR/client.csr \
    -CA $CERTS_DIR/ca-cert.pem -CAkey $CERTS_DIR/ca-key.pem -CAcreateserial \
    -out $CERTS_DIR/client-cert.pem

echo ""
echo "=== Сертификаты успешно созданы ==="
echo "Файлы сохранены в директории $CERTS_DIR:"
ls -la $CERTS_DIR/*.pem

# Очистка CSR файлов
rm $CERTS_DIR/*.csr $CERTS_DIR/*.srl 2>/dev/null

echo ""
echo "=== Информация о сертификатах ==="
echo ""
echo "CA сертификат:"
openssl x509 -in $CERTS_DIR/ca-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After"
echo ""
echo "Сертификат сервера:"
openssl x509 -in $CERTS_DIR/server-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After"
echo ""
echo "Сертификат клиента:"
openssl x509 -in $CERTS_DIR/client-cert.pem -text -noout | grep -E "Subject:|Issuer:|Not Before|Not After"
