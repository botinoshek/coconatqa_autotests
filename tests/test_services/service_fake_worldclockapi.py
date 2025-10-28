
#test_services\service_fake_worldclockapi.py
from fastapi import FastAPI
from datetime import datetime, timedelta
import pytz

app = FastAPI()

@app.get("/ping")
def ping():
    return "PONG!"

#имитация работы реального сервиса http://worldclockapi.com/api/json/utc/now
# (можете перейти по ссылке или сделать гет запрос в реальный сервис чтоб проверить как он работает)
@app.get("/fake/worldclockapi/api/json/utc/now")
def get_current_utc_time():
    # Получаем текущее время в UTC
    now = datetime.now(pytz.utc)
    # мы можем сами регулировать то как отвечать на конкретные запросы
    # не только отдавая конкретное текущее время, но и добавляя различную логику
    # например можем при каждом запросе отдавать разные ответы
    # или выбрасывая различные exception для проверки как отреагирует наша система

    # Формируем ответ
    response = {
        "$id": "1",
        "currentDateTime": now.strftime("%Y-%m-%dT%H:%MZ"),
        "utcOffset": "00:00:00",
        "isDayLightSavingsTime": False,
        "dayOfTheWeek": now.strftime("%A"),
        "timeZoneName": "UTC",
        "currentFileTime": int(now.timestamp() * 10**7),  # Преобразуем в FILETIME (100-наносекундные интервалы с 1 января 1601)
        "ordinalDate": now.strftime("%Y-%j"),  # Год и день года (001-366)
        "serviceResponse": None
    }

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=16001)

# для запуска сервера
# pip install -r requirements.txt
# python test_services\service_fake_worldclockapi.py
# для проверки работоспособности curl http://127.0.0.1:16001/ping
# curl http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now