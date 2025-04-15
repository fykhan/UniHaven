import requests

def lookup_coordinates_als(address):
    url = "https://www.als.gov.hk/lookup"
    params = {
        "q": address,
        "output": "JSON"
    }
    headers = {
        "Accept": "application/json"
    }

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()

        suggestions = data.get("SuggestedAddress")
        if not suggestions:
            print("No address found.")
            return None

        geo_info = suggestions[0]['Address']['PremisesAddress']['GeospatialInformation']
        lat = float(geo_info['Latitude'])
        lon = float(geo_info['Longitude'])

        print(f"Address: {address}\nLatitude: {lat}, Longitude: {lon}")
        return lat, lon

    except Exception as e:
        print("rror:", e)
        return None

# Example
lookup_coordinates_als("Haking Wong Building")
