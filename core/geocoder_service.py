import requests
from dotenv import dotenv_values


def get_coords(request: str):
    request = request.replace(' ', '+')
    api_key = dotenv_values('dot.env')['API_KEY_FOR_GEOCODER']
    get_request = (f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}"
                   f"&geocode={request}&format=json")
    response = requests.get(get_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]
        return toponym_coodrinates


def get_full_address(request: str, mail_ind=False):
    api_key = dotenv_values('dot.env')['API_KEY_FOR_GEOCODER']
    get_request = (f"http://geocode-maps.yandex.ru/1.x/?apikey={api_key}"
                   f"&geocode={request}&format=json")
    response = requests.get(get_request)
    if response:
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_address = toponym['metaDataProperty']['GeocoderMetaData']['text']
        if mail_ind:
            if "postal_code" in toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]:
                mail_index = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                return toponym_address + ", Почтовый индекс - " + mail_index
            else:
                return toponym_address
        else:
            return toponym_address
