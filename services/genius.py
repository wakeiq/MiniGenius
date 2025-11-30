import os
import requests
from dotenv import load_dotenv

load_dotenv()

GENIUS_TOKEN = os.getenv("API_KEY")
BASE_URL = "https://api.genius.com/"

HEADERS = {
    "Authorization": f"Bearer {GENIUS_TOKEN}"
}

def genius_request(endpoint, params=None):
    if params is None:
        params = {}
    
    url = BASE_URL + endpoint
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    return data

def search_all(query, limit=50):
    data = genius_request("search", {"q": query})
    data_response = data["response"]["hits"][:limit]

    results = []

    for item in data_response:
        result = item["result"]
        result["_type"] = item["type"]
        results.append(result)


    return results


def get_top_tracks(limit=50):
    data = genius_request("search", {"q": "popular songs worldwide"})
    data_response = data["response"]["hits"][:limit]

    tracks = []

    for item in data_response:
        if item["type"] == "song":
            tracks.append(item["result"])

    return tracks


def get_track_info(track_id):
    ep = "songs/" + str(track_id)
    data = genius_request(ep)

    if data == None or "response" not in data or "song" not in data["response"]:
        return None
    
    return data

def get_album_info(album_id):
    ep = "albums/" + str(album_id)
    data = genius_request(ep)

    if data == None or "response" not in data or "album" not in data["response"]:
        return None
    
    return data

# def get_top_albums(limit=50):
#     data = genius_request("search", {"q": "popular albums"})
#     data_response = data["response"]["hits"][:limit]
    
#     albums = []

#     for item in data_response:
#         if item["type"] == "album":
#             albums.append(item["result"])

#     return albums

