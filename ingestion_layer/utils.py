import requests
import json
import config


def store_realtime_data(data: list[dict]):
    """Store realtime data.

    Args:
        data (dict): Realtime data.

    Returns:
        dict: Response data.
    """
    data = json.dumps(data)
    data = json.loads(data)
    url = config.DATA_SERVICE_URL + "/realtime/store"
    response = requests.post(url, json=data)
    if response.status_code != 200:
        raise Exception(response.text)
    data = response.json()

