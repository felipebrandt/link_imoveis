import brazilcep
from geopy.geocoders import Nominatim


def get_json_address_by_cep(cep):
    json_address = get_address_by_cep(cep)
    json_address['cep'] = cep
    json_address['latitude'], json_address['longitude'] = get_geolocation(json_address)
    return json_address


def get_geolocation(json_address, next_step=False):
    location = go_api_geolocation(json_address)
    if location:
        return location.latitude, location.longitude
    elif next_step:
        return None, None
    else:
        new_json_address = get_address_by_cep(json_address['cep'][:-1] + '0')
        return get_geolocation(new_json_address, True)


def get_address_by_cep(cep):
    return brazilcep.get_address_from_cep(cep)


def go_api_geolocation(json_address):
    geolocation = Nominatim(user_agent="test_app")
    return geolocation.geocode(json_address['street'] + ", " +
                               json_address['city'] + " - " +
                               json_address['district'])


def get_cep_by_olx_address(olx_address):
    return olx_address[-8:]

