import requests
import typing
from dotenv import dotenv_values
from core import geocoder_service


def get_organization(coords: tuple, spn: tuple) -> typing.Union[None, str]:
    api_key = dotenv_values('dot.env')['API_KEY_FOR_ORGANIZATIONS']
    address = geocoder_service.get_address(coords)
    get_request = (f"https://search-maps.yandex.ru/v1/?apikey={api_key}"
                   f"&text={address}&lang=ru_RU&type=biz"
                   f"&ll={coords[1]},{coords[0]}&spn={spn[0]},{spn[1]}&rspn=1")
    response = requests.get(get_request)
    if response:
        json_response = response.json()
        try:
            return json_response['features'][0]['properties']['CompanyMetaData']['address']
        except KeyError:
            return None
        except IndexError:
            return None


def get_full_name(request, mail_ind: bool = False):
    api_key = dotenv_values('dot.env')['API_KEY_FOR_ORGANIZATIONS']
    get_request = (f"https://search-maps.yandex.ru/v1/?apikey={api_key}"
                   f"&text={request}&lang=ru_RU&type=biz")
    response = requests.get(get_request)
    if response:
        json_response = response.json()
        organization_name = json_response['features'][0]['properties']['CompanyMetaData']['name']

        if mail_ind:
            api_key = dotenv_values('dot.env')['API_KEY_FOR_GEOCODER']
            get_request = (f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}"
                           f"&geocode={request}&format=json")
            geocode_response = requests.get(get_request)
            if response:
                geocode_json_response = geocode_response.json()
                toponym = geocode_json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                if "postal_code" in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]:
                    mail_index = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                    return organization_name + ", Почтовый индекс - " + mail_index
                else:
                    return organization_name
        return organization_name
