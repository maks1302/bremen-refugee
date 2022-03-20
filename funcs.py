import time
import sqlite3
from datetime import datetime

from config import districts


conn = sqlite3.connect('sqlite.db', check_same_thread=False)
c = conn.cursor()


def get_district(index: int) -> str:

    return districts[index - 1]


def get_district_list() -> str:
    # List and layout given districts

    to_print = '\n'.join([f"{count + 1}. {district}" for count, district in enumerate(districts)])
    return f"Districts:\n\n<b>{to_print}</b>"


def process_query(query: dict) -> None:
    # Insert new query to the DB

    c.execute('INSERT INTO queries(user_id, role, district, date, time) VALUES(?,?,?,?,?)',
              (*query.values(),))
    conn.commit()


def check_expired(query_time: str) -> bool:
    # Check if the query is not expired (checking date only, not time)

    query_time_timestamp = time.mktime(datetime.strptime(query_time, "%d.%m.%Y").timetuple())
    time_timestamp = time.mktime(datetime.strptime(str(datetime.now().strftime("%d.%m.%Y")), "%d.%m.%Y").timetuple())

    return query_time_timestamp >= time_timestamp


def get_refugee_result(query: dict, role: str) -> list:

    c.execute(f'SELECT * FROM queries WHERE date=? and time=? and role=? and done=?',
              (query["date"], query["time"], role, 0))

    result = [helper for helper in c.fetchall() if check_expired(helper[3])]
    if query["district"] != districts[-1]:
        result = [helper for helper in result if helper[2] in [query["district"], districts[-1]]]

    return result


def user_queries(user_id: str) -> list:

    c.execute(f'SELECT * FROM queries WHERE user_id=? and done=?', (user_id,  0))
    result = [query for query in c.fetchall() if check_expired(query[3])]
    return result


def get_check_result(argument: str) -> list:

    index, date = argument.split()
    district = districts[int(index) - 1]

    c.execute(f'SELECT * FROM queries WHERE date=? and role=? and done=?', (date, 'helper', 0))

    result = [helper for helper in c.fetchall() if check_expired(helper[3])]
    if district != districts[-1]:
        result = [helper for helper in result if helper[2] in [district, districts[-1]]]
    return result


def helper_layout(helper_found: tuple, check=False, user_id=False) -> str:

    to_print = f'District: <b>{helper_found[2]}\n</b>' \
               f'Date: <b>{helper_found[3]}\n</b>' \
               f'Time: <b>{helper_found[4]}</b>'

    contact_person = helper_found[0]
    if user_id:
        contact_person = user_id
    if not check:
        to_print += f'\n\n<b><a href="tg://user?id={contact_person}">👉 Contact the volunteer</a></b>'

    return to_print


def remove_query(user_id, message) -> None:

    district, date, time_ = [data.split(': ')[1] for data in message.split('\n')]
    c.execute(f'UPDATE queries SET done=1 WHERE user_id=? and district=? and date=? and time=? and done=?',
              (user_id, district, date, time_, 0))
    conn.commit()
