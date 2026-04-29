import requests

def search_address(address):
    if address:
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        server_address = 'http://geocode-maps.yandex.ru/1.x/?'
        geocoder_request = f'{server_address}apikey={api_key}&geocode={address}&format=json'
        # Выполняем запрос.
        response = requests.get(geocoder_request)
        if response:
            # Преобразуем ответ в json-объект
            json_response = response.json()
            geocode = list(map(float,
                               json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                                   'Point'][
                                   "pos"].split()))
            ll = geocode
            return ll

        else:
            print("Ошибка выполнения запроса:")
            print(geocoder_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")


def getImage(ll, spn=[0.001, 0.001]):
    help_list = ','.join([str(i) for i in ll])
    help_list_spn = ','.join([str(i) for i in spn])
    server_address = 'https://static-maps.yandex.ru/v1?'
    api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
    ll_spn = f'll={help_list}&spn={help_list_spn}'
    # Готовим запрос.
    map_request = f"{server_address}{ll_spn}&apikey={api_key}"
    return map_request