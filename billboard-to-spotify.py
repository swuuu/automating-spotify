import requests
import json
from secret import client_id, client_token, billboard_api_key

# storing the song names and artists
song_infos = [] # list of tuples


# retrieves the top 10 songs from the billboard api (Hot 100 billboard)
def get_songs_from_billboard():
    url = "https://billboard-api2.p.rapidapi.com/hot-100"

    querystring = {"date":"2020-07-11","range":"1-10"} #need to manually update the date, also inserting current date may not work since the api updates only weekly

    headers = {
        'x-rapidapi-host': "billboard-api2.p.rapidapi.com",
        'x-rapidapi-key': billboard_api_key
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    data = json.loads(response.text)

    #retrieving the song_name and song_artist from data and appending to song_infos
    for song_index in data["content"]:

        song_name = data["content"][song_index]["title"]
        song_artist = data["content"][song_index]["artist"]
        song_info = (song_name, song_artist)
        song_infos.append(song_info)


# billboard API returns artist names with the format "Main_artist featuring secondary_artists..."
# every word after "featuring" messes up the get_spotify_uri search so the function below removes it
def artist_string_parser(artist_name_from_billboard):

    # splitting the name by spaces
    artist_names_list = artist_name_from_billboard.split()

    # iterating and checking if the word "Featuring" is inside
    index = 0
    for name in artist_names_list:
        if name == "Featuring":
            break;
        else:
            index += 1

    # there is no features
    if index == len(artist_names_list):
        return " ".join(artist_names_list)

    # there is a feature, so return the main artist only
    else:
        artist_name_to_join = artist_names_list[0:index]
        return " ".join(artist_name_to_join)




# gets the uri of each of the 10 songs from the billboard
def get_spotify_uri(song_name, artist_name):

    querystring = "https://api.spotify.com/v1/search?q=track%3A{}%20artist%3A{}&type=track&offset=0&limit=20".format(
        song_name,
        artist_name
    )

    r = requests.get(querystring,
                     headers= {"Content-Type":"application/json",
                                "Authorization":"Bearer {}".format(client_token)
                                }
                     )

    r_json = r.json()
    songs = r_json["tracks"]["items"]

    # returns the uri of the first song of the search only
    uri = songs[0]["uri"]
    return uri

# creates the spotify playlist
def create_spotify_playlist():

    querystring = "https://api.spotify.com/v1/users/" + client_id + "/playlists"

    data = json.dumps({"name": "billboard-playlist",
                       "public": False,
                       "description": "Playlist of top 25 songs on the billboard this week"})

    headers = {
        "Authorization": "Bearer {}".format(client_token),
        "Content-Type": "application.json"
    }

    r = requests.post(querystring, data, headers=headers)

    #returns the spotify playlist id
    response = r.json()
    return response["id"]


# adds the songs to the playlist
# main function
# needs a spotify playlist id and the uri of each song to add
def add_song_to_playlist():

    # populates song_infos
    get_songs_from_billboard()

    # collect all of uri
    uris = []
    for song_info in song_infos:
        uri = get_spotify_uri(song_info[0], artist_string_parser(song_info[1]))
        uris.append(uri)

    # create a new playlist
    playlist_id = create_spotify_playlist()

    # add all songs into new playlist
    request_data = json.dumps(uris)
    querystring = "https://api.spotify.com/v1/playlists/{}/tracks".format(
        playlist_id)

    response = requests.post(
        querystring,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(client_token)
        }
    )

    print("Spotify error code:", response.status_code)

    response_json = response.json()
    return response_json



# running it
add_song_to_playlist()

