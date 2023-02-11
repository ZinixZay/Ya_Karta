import requests
import typing
import random
from dotenv import dotenv_values


def get_organization(coords: tuple, spn: tuple) -> typing.Union[None, str]:
    api_key = dotenv_values('dot.env')['API_KEY_FOR_ORGANIZATIONS']
    get_request = (f"https://search-maps.yandex.ru/v1/?apikey={api_key}"
                   f"&text=магазин&lang=ru_RU&ll={coords[0]},{coords[1]}&spn={spn[0] * 5},{spn[1] * 5}&type=biz&rspn=1")
    response = requests.get(get_request)
    if response:
        json_response = response.json()
        try:
            print(json_response)
            print(spn)
            return json_response['features'][0]['properties']['CompanyMetaData']['address']
        except KeyError:
            return None
        except IndexError:
            return None

