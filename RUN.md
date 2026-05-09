# Запуск и тестироване

##### Сборка проекта

1. **Создание виртуального окружения**

> 
> ```powershell
> python -m venv venv
> ```

2. **Загрузка зависимостей**

> 
> ```powershell
> pip install -r requirements.txt
> ```

##### Запуск генерации ключей

> [!NOTE]
> Все ключи по умолчанию находятся в папке cert

> 
> ```powershell
> python generator/cert_generator.py
> ```

##### Настройка для подключения из Chrome

1. WIN + R
2. Ввести `certmgr.msc`
3. Запустить `python chrome_generator.py` и сгенерировать .p12 ключ (Путь к файлу: `/cert/client/client-browser.p12`)
4. Установить файл client-browser.p12 в сертификаты на Windows
5. Установить ca-cert.pem в сертификаты в Chrome (Путь к файлу: `cert/ca/ca-cert.pem`, путь к странице Chrome: `chrome://certificate-manager/localcerts/usercerts`)

##### Работа с сервером

1. **Запустить сервер**

> 
> ```powershell
> python server/server.py
> ```

2. **Сделать запрос из Chrome и с клиента**

> 
> ```powershell
> python client/client.py
> ```

> 
> ```powershell
> https://localhost:8443/hello/test
> ```


##### Разница между TLS и mTLS

Файл server.py

* TSL - `ssl_cert_reqs=ssl.CERT_NONE`
* mTSL - `ssl_cert_reqs=ssl.CERT_REQUIRED`

##### Референсы

* [mTLS на FastAPI](https://github.com/akoserwal/fastapi-patterns)
* [mTLS на Flask](https://github.com/michaelkotelnikov/flask-mtls)
