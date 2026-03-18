import calendar
from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query
from chinese_calendar import get_holiday_detail, is_in_lieu, is_workday


SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
WEEKDAY_NAMES = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

app = FastAPI(
    title="Holiday Or Work API",
    description="查询中国节假日、补班日，以及某个月的工作日和休息日。",
    version="1.0.0",
)


def parse_date_or_raise(date_str: str) -> date:
    try:
        return date.fromisoformat(date_str)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail="date_str must be in YYYY-MM-DD format.",
        ) from exc


def build_day_payload(target_date: date) -> dict:
    _, holiday_name = get_holiday_detail(target_date)
    weekday_index = target_date.weekday()
    workday = is_workday(target_date)
    weekend = weekday_index > 4
    in_lieu_day = is_in_lieu(target_date)
    public_holiday = holiday_name is not None and not workday and not in_lieu_day
    makeup_workday = holiday_name is not None and workday

    if makeup_workday:
        day_type = "makeup_workday"
    elif in_lieu_day:
        day_type = "in_lieu_rest_day"
    elif public_holiday:
        day_type = "public_holiday"
    elif weekend:
        day_type = "weekend"
    else:
        day_type = "workday"

    return {
        "date": target_date.isoformat(),
        "is_workday": workday,
        "is_rest_day": not workday,
        "is_weekend": weekend,
        "is_public_holiday": public_holiday,
        "is_in_lieu": in_lieu_day,
        "is_makeup_workday": makeup_workday,
        "is_holiday_related_day": holiday_name is not None,
        "holiday_name": holiday_name,
        "day_type": day_type,
        "weekday": weekday_index + 1,
        "day_of_week": WEEKDAY_NAMES[weekday_index],
    }


@app.get("/")
def read_root() -> dict:
    today = datetime.now(SHANGHAI_TZ).date()
    return {
        "message": "Holiday Or Work API is running.",
        "today": today.isoformat(),
        "docs": "/docs",
        "endpoints": {
            "check_single_date": "/check_date/{date_str}",
            "check_month": "/month?year=2026&month=3",
        },
    }


@app.get("/check_date/{date_str}")
def check_date(date_str: str) -> dict:
    target_date = parse_date_or_raise(date_str)
    return build_day_payload(target_date)


@app.get("/month")
def check_month(
    year: int | None = Query(default=None, ge=1901, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
) -> dict:
    today = datetime.now(SHANGHAI_TZ).date()
    selected_year = year or today.year
    selected_month = month or today.month

    _, total_days = calendar.monthrange(selected_year, selected_month)
    all_days = [
        build_day_payload(date(selected_year, selected_month, day))
        for day in range(1, total_days + 1)
    ]

    workdays = [item for item in all_days if item["is_workday"]]
    rest_days = [item for item in all_days if item["is_rest_day"]]
    public_holidays = [item for item in all_days if item["is_public_holiday"]]
    makeup_workdays = [item for item in all_days if item["is_makeup_workday"]]
    in_lieu_days = [item for item in all_days if item["is_in_lieu"]]

    return {
        "year": selected_year,
        "month": selected_month,
        "days": all_days,
        "workdays": workdays,
        "rest_days": rest_days,
        "public_holidays": public_holidays,
        "makeup_workdays": makeup_workdays,
        "in_lieu_days": in_lieu_days,
        "total_days": total_days,
        "total_workdays": len(workdays),
        "total_rest_days": len(rest_days),
        "total_public_holidays": len(public_holidays),
        "total_makeup_workdays": len(makeup_workdays),
        "total_in_lieu_days": len(in_lieu_days),
    }
