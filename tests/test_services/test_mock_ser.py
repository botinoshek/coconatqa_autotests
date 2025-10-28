import requests
from test_mock_services import WorldClockResponse, WhatIsTodayResponse, DateTimeRequest
import datetime
import pytz


#Modul_4\Cinescope\tests\api\test_mock_services.py
#Функция выполняющая запрос в Fake сервис worldclockapi для получения текущей даты
def get_fake_worldclockap_time() -> WorldClockResponse:
    # Выполняем GET-запрос
    response = requests.get("http://127.0.0.1:16001/fake/worldclockapi/api/json/utc/now")  #Запрос в реальный сервис
    # Проверяем статус ответа
    assert response.status_code == 200, "Удаленный сервис недоступен"
    # Парсим JSON-ответ с использованием Pydantic модели
    return  WorldClockResponse(**response.json())

class TestTodayIsHolidayServiceAPI:
    #worldclockap
    def test_fake_worldclockap(self):# проверка работоспособности сервиса worldclockap
        world_clock_response = get_fake_worldclockap_time()
        # Выводим текущую дату и время
        current_date_time = world_clock_response.currentDateTime
        print(f"Текущая дата и время: {current_date_time=}")

        assert current_date_time == datetime.now(pytz.utc).strftime("%Y-%m-%dT%H:%MZ"), "Дата не совпадает"

    def test_fake_what_is_today(self):# проверка работоспособности Fake сервиса what_is_today
        # Запрашиваем текущее время у сервиса worldclockap
        world_clock_response = get_fake_worldclockap_time()

        what_is_today_response = requests.post("http://127.0.0.1:16002/what_is_today",
                                               data=DateTimeRequest(currentDateTime=world_clock_response.currentDateTime).model_dump_json()
                                               )

        # Проверяем статус ответа от тестируемого сервиса
        assert what_is_today_response.status_code == 200, "Удаленный сервис недоступен"
        # Парсим JSON-ответ от тестируемого сервиса с использованием Pydantic модели
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())

        assert what_is_today_data.message ==  "Сегодня нет праздников в России.", "Сегодня нет праздника!"