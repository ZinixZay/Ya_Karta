import requests
from dotenv import dotenv_values


def get_organization(cords: tuple):
    api_key = dotenv_values('dot.env')['API_KEY_FOR_ORGANIZATIONS']
    get_request = (f"https://search-maps.yandex.ru/v1/?apikey={api_key}"
                   f"&text={cords[0]},{cords[1]}&lang=ru_RU")
    response = requests.get(get_request)
    if response:
        json_response = response.json()
        print(response.url)

