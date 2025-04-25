from datetime import date, datetime, timedelta
from typing import Union

def convertDatetimeToUnixTimestamp(dateTime: Union[date, datetime, str]) -> int:
    if type(dateTime) == str:
        dateTime = datetime.strptime(dateTime, "%Y-%m-%d %H:%M:%S")
    unixTime = int(datetime.timestamp(dateTime)) * 1000  # Convert to milliseconds
    return unixTime

def convertUnixTimestampToDatetime(unixTimestamp: int) -> str:
    dateTime = datetime.fromtimestamp(unixTimestamp)
    return dateTime.strftime("%Y-%m-%d %H:%M:%S")

def getStartTime(dayInterval: int) -> int:
    startTime = datetime.today() - timedelta(hours=24*dayInterval)
    return startTime