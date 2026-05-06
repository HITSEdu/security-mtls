#!/usr/bin/env python3
"""
Клиент партнера - подключается к серверу банка HITsoff с mTLS
Использует встроенные библиотеки Python
"""

import http.client
import ssl
import os
import json
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Пути к сертификатам и ключам
CERTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'certs')
CLIENT_CERT = os.path.join(CERTS_DIR, 'client-cert.pem')
CLIENT_KEY = os.path.join(CERTS_DIR, 'client-key.pem')
CA_CERT = os.path.join(CERTS_DIR, 'ca-cert.pem')

# Параметры сервера
BANK_HOST = '127.0.0.1'
BANK_PORT = 8443

def create_ssl_context():
    """Создает SSL контекст с mTLS конфигурацией"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    
    # Загружаем клиентский сертификат и ключ
    context.load_cert_chain(CLIENT_CERT, CLIENT_KEY)
    
    # Проверяем сертификат сервера с помощью CA
    context.load_verify_locations(CA_CERT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    
    logger.info("SSL контекст успешно инициализирован для mTLS клиента")
    return context

def send_request(method, path, data=None):
    """Отправляет HTTP запрос с mTLS"""
    ssl_context = create_ssl_context()
    
    try:
        # Создаем защищенное соединение
        connection = http.client.HTTPSConnection(
            BANK_HOST,
            BANK_PORT,
            context=ssl_context,
            timeout=10
        )
        
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data, ensure_ascii=False).encode('utf-8') if data else None
        
        if body:
            headers['Content-Length'] = len(body)
        
        # Отправляем запрос
        connection.request(method, path, body, headers)
        
        # Получаем ответ
        response = connection.getresponse()
        response_data = response.read().decode('utf-8')
        
        connection.close()
        
        return response.status, response_data
        
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {str(e)}")
        raise

def check_server_health():
    """Проверяет доступность сервера"""
    try:
        logger.info("Проверка доступности сервера...")
        status, response_text = send_request('GET', '/health')
        
        if status == 200:
            data = json.loads(response_text)
            logger.info(f"✓ Сервер доступен: {data.get('service')}")
            return True
        else:
            logger.error(f"Ошибка: статус {status}")
            return False
    except Exception as e:
        logger.error(f"Сервер недоступен: {str(e)}")
        return False

def validate_connection():
    """Проверяет mTLS соединение"""
    try:
        logger.info("Проверка mTLS соединения...")
        status, response_text = send_request('GET', '/api/validate')
        
        if status == 200:
            data = json.loads(response_text)
            logger.info(f"✓ mTLS соединение установлено")
            logger.info(f"  Клиент: {data.get('client_subject')}")
            logger.info(f"  Статус проверки: {data.get('verification_status')}")
            return True
        else:
            logger.error(f"Ошибка при проверке: статус {status}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при проверке mTLS: {str(e)}")
        return False

def send_transfer_request(amount, recipient):
    """Отправляет запрос на перевод средств"""
    try:
        logger.info(f"Отправка запроса на перевод {amount} RUB для {recipient}...")
        
        payload = {
            'amount': amount,
            'recipient': recipient
        }
        
        status, response_text = send_request('POST', '/api/transfer', payload)
        
        if status == 200:
            data = json.loads(response_text)
            logger.info("✓ Платеж успешно обработан")
            logger.info(f"  ID транзакции: {data.get('transaction_id')}")
            logger.info(f"  Сумма: {data.get('amount')} RUB")
            logger.info(f"  Получатель: {data.get('recipient')}")
            logger.info(f"  Время: {data.get('timestamp')}")
            return True
        else:
            logger.error(f"Ошибка при обработке платежа: статус {status}")
            logger.error(f"Ответ: {response_text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса: {str(e)}")
        return False

def main():
    """Главная функция клиента"""
    logger.info("=" * 60)
    logger.info("Клиент партнера - Подключение к банку HITsoff")
    logger.info("=" * 60)
    
    # Проверяем наличие необходимых файлов
    if not all(os.path.exists(f) for f in [CLIENT_CERT, CLIENT_KEY, CA_CERT]):
        logger.error("Необходимые сертификаты не найдены. Запустите скрипт generate_certs.sh")
        return False
    
    try:
        # Проверяем доступность сервера
        logger.info("\n[1] Проверка доступности сервера...")
        if not check_server_health():
            logger.error("Сервер недоступен")
            return False
        
        # Проверяем mTLS соединение
        logger.info("\n[2] Проверка mTLS соединения...")
        if not validate_connection():
            logger.error("mTLS соединение не установлено")
            return False
        
        # Отправляем примеры платежей
        logger.info("\n[3] Отправка платежных операций...")
        
        transfers = [
            {'amount': 1000, 'recipient': 'ООО Компания А'},
            {'amount': 5000, 'recipient': 'ИП Иванов И.И.'},
            {'amount': 3500, 'recipient': 'АО Торговая сеть'}
        ]
        
        for transfer in transfers:
            send_transfer_request(transfer['amount'], transfer['recipient'])
            logger.info("")
        
        logger.info("=" * 60)
        logger.info("Все операции завершены успешно")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
