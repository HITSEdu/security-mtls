#!/usr/bin/env python3
"""
Сервер банка HITsoff - слушает на порту 5000 с mTLS
Требует валидный сертификат клиента для проверки партнера
Использует встроенные библиотеки Python
"""

import http.server
import ssl
import os
import json
import logging
import threading
from urllib.parse import urlparse, parse_qs

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Пути к сертификатам и ключам
CERTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'certs')
SERVER_CERT = os.path.join(CERTS_DIR, 'server-cert.pem')
SERVER_KEY = os.path.join(CERTS_DIR, 'server-key.pem')
CA_CERT = os.path.join(CERTS_DIR, 'ca-cert.pem')

class mTLSRequestHandler(http.server.BaseHTTPRequestHandler):
    """Обработчик HTTP запросов с поддержкой mTLS"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/health':
            self.send_health_response()
        elif self.path == '/api/validate':
            self.send_validate_response()
        else:
            self.send_error_response(404, 'Not found')
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/transfer':
            self.handle_transfer()
        else:
            self.send_error_response(404, 'Not found')
    
    def send_health_response(self):
        """Отправляет ответ здоровья сервера"""
        response = {
            'status': 'healthy',
            'service': 'HITsoff Bank Server'
        }
        self.send_json_response(200, response)
    
    def send_validate_response(self):
        """Отправляет информацию о валидации mTLS"""
        # Получаем информацию о сертификате клиента
        cert_subject = self.get_client_cert_subject()
        
        logger.info(f"Проверка сертификата: {cert_subject}")
        
        response = {
            'message': 'mTLS соединение установлено',
            'client_subject': cert_subject,
            'verification_status': 'SUCCESS'
        }
        self.send_json_response(200, response)
    
    def handle_transfer(self):
        """Обработка запроса на перевод средств"""
        try:
            # Проверяем сертификат клиента
            cert_subject = self.get_client_cert_subject()
            if not cert_subject:
                logger.warning("Попытка доступа без сертификата клиента")
                self.send_error_response(403, 'Client certificate required')
                return
            
            logger.info(f"Запрос от партнера: {cert_subject}")
            
            # Читаем тело запроса
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Парсим JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self.send_error_response(400, 'Invalid JSON')
                return
            
            # Проверяем обязательные поля
            if 'amount' not in data or 'recipient' not in data:
                self.send_error_response(400, 'Missing required fields: amount, recipient')
                return
            
            amount = data.get('amount')
            recipient = data.get('recipient')
            
            # Валидируем сумму
            if not isinstance(amount, (int, float)) or amount <= 0:
                self.send_error_response(400, 'Invalid amount')
                return
            
            # Логирование транзакции
            logger.info(f"Обработка перевода: {amount} RUB для {recipient}")
            
            # Формируем ответ
            response = {
                'status': 'success',
                'transaction_id': 'TXN-2026-05-06-001',
                'amount': amount,
                'recipient': recipient,
                'timestamp': '2026-05-06T21:22:33Z',
                'message': 'Платеж успешно обработан'
            }
            self.send_json_response(200, response)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {str(e)}")
            self.send_error_response(500, 'Internal server error')
    
    def get_client_cert_subject(self):
        """Получает информацию о сертификате клиента"""
        try:
            # Получаем сертификат из SSL соединения
            cert = self.connection.getpeercert()
            if cert and 'subject' in cert:
                subject_parts = []
                for rdn in cert['subject']:
                    for key, value in rdn:
                        subject_parts.append(f"{key}={value}")
                return ', '.join(subject_parts) if subject_parts else None
        except:
            pass
        return None
    
    def send_json_response(self, status_code, data):
        """Отправляет JSON ответ"""
        response_body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-length', len(response_body))
        self.end_headers()
        self.wfile.write(response_body)
    
    def send_error_response(self, status_code, message):
        """Отправляет ошибку"""
        error = {'error': message}
        self.send_json_response(status_code, error)
    
    def log_message(self, format, *args):
        """Переопределяем логирование запросов"""
        logger.info(f"{self.client_address[0]} - {format % args}")

def create_ssl_context():
    """Создает SSL контекст с mTLS конфигурацией"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    # Загружаем сертификат и приватный ключ сервера
    context.load_cert_chain(SERVER_CERT, SERVER_KEY)
    
    # Требуем сертификат клиента и проверяем его с помощью CA
    context.load_verify_locations(CA_CERT)
    context.verify_mode = ssl.CERT_REQUIRED
    
    logger.info("SSL контекст успешно инициализирован с mTLS")
    return context

if __name__ == '__main__':
    # Проверяем наличие необходимых файлов
    if not all(os.path.exists(f) for f in [SERVER_CERT, SERVER_KEY, CA_CERT]):
        logger.error("Необходимые сертификаты не найдены. Запустите скрипт generate_certs.sh")
        exit(1)
    
    ssl_context = create_ssl_context()
    
    logger.info("=" * 60)
    logger.info("Запуск сервера банка HITsoff")
    logger.info("Адрес: https://127.0.0.1:8443")
    logger.info("mTLS включен - требуется валидный сертификат клиента")
    logger.info("=" * 60)
    
    server = http.server.HTTPServer(('0.0.0.0', 8443), mTLSRequestHandler)
    server.socket = ssl_context.wrap_socket(server.socket, server_side=True)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Сервер остановлен")
        server.server_close()
