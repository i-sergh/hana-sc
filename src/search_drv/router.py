from fastapi import APIRouter

from random import randint

from search_drv.utils import TABLES

router = APIRouter(
    prefix='/api/search',
    tags=['search']
)

@router.get('/fake-data')
def get_facke_data():
    return {
            "data": [
                    "eins Katze",
                    "zwei Zwiebelen",
                    "vier Bleischtiften",
                    ]
        }

@router.get('/fake-random-data')
def get_facke_random_data():
    data = ["eins", "Katze", "zwei", "Zwiebelen", "vier", "Bleischtiften"]
    random_data = [data[randint(0, 5)] + " " + str(randint(0,100)) for _ in range(randint(2, 5))]
    return {
            "data": random_data
        }


@router.get('/find')
def find_by(inpt = ''):
    data = TABLES.find(inpt.upper().strip())
    print(data)
    return {'data': data}