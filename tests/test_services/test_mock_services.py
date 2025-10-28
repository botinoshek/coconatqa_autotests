import datetime as dt
import requests
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException

app = FastAPI()

class WorldClockResponse(BaseModel):
    id: str = Field(alias="$id")
    currentDateTime: str
    utcOffset: str
    isDayLightSavingsTime: bool
    dayOfTheWeek: str
    timeZoneName: str
    currentFileTime: int
    ordinalDate: str
    serviceResponse: None

    class Config:
        allow_population_by_field_name = True


class DateTimeRequest(BaseModel):
    currentDateTime: str


russian_holidays = {
    "01-01": "Новый год",
    "01-07": "Рождество Христово",
    "02-23": "День защитника Отечества",
    "03-08": "Международный женский день",
    "05-01": "Праздник Весны и Труда",
    "05-09": "День Победы",
    "06-12": "День России",
    "11-04": "День народного единства",
    "12-31": "Канун Нового года",
}


@app.post("/what_is_today")
def what_is_today(request: DateTimeRequest):
    date_str = request.currentDateTime
    try:
        for fmt in ("%Y-%m-%dT%H:%MZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%HZ"):
            try:
                date_obj = dt.datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        else:
            raise HTTPException(status_code=400, detail=f"Неизвестный формат даты: {date_str}")

        month_day = date_obj.strftime("%m-%d")
        holiday = russian_holidays.get(month_day, "Сегодня нет праздников в России.")
        return {"message": holiday}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class WhatIsTodayResponse(BaseModel):
    message: str


class TestMockService:
    def run_wiremock_worldclockap_time(self):
        wiremock_url = "http://localhost:8080/__admin/mappings"
        mapping = {
            "request": {"method": "GET", "url": "/wire/mock/api/json/utc/now"},
            "response": {
                "status": 200,
                "body": '''{
                    "$id": "1",
                    "currentDateTime": "2025-03-08T00:00Z",
                    "utcOffset": "00:00",
                    "isDayLightSavingsTime": false,
                    "dayOfTheWeek": "Wednesday",
                    "timeZoneName": "UTC",
                    "currentFileTime": 1324567890123,
                    "ordinalDate": "2025-1",
                    "serviceResponse": null
                }''',
            },
        }
        response = requests.post(wiremock_url, json=mapping)
        assert response.status_code == 201, "Не удалось настроить WireMock"

    def test_what_is_today_BY_WIREMOCK(self):
        self.run_wiremock_worldclockap_time()
        world_clock_response = requests.get("http://localhost:8080/wire/mock/api/json/utc/now")
        assert world_clock_response.status_code == 200, "WireMock не отвечает"

        current_date_time = WorldClockResponse(**world_clock_response.json()).currentDateTime

        what_is_today_response = requests.post(
            "http://127.0.0.1:16002/what_is_today",
            data=DateTimeRequest(currentDateTime=current_date_time).model_dump_json(),
        )

        assert what_is_today_response.status_code == 200, f"FastAPI вернул {what_is_today_response.status_code}: {what_is_today_response.text}"
        what_is_today_data = WhatIsTodayResponse(**what_is_today_response.json())
        assert what_is_today_data.message == "Международный женский день"
