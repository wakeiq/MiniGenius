from flask import Blueprint, render_template, request
from flask_login import login_required
from services.genius import (search_all, get_track_info, get_album_info, get_top_tracks)

page = Blueprint("page", __name__)

@page.route("/")
@login_required
def home():

    query = request.args.get("q")

    top_tracks = []
    # top_albums = []
    # search_results = []
    tracks = []
    albums = []

    if query:
        results = search_all(query, limit=50)

        for item in results:
            item_category = item.get("_type")

            if item_category == "song":
                tracks.append(item)
            elif item_category == "album":
                albums.append(item)
    else:
        top_tracks = get_top_tracks()
        # top_albums = get_top_albums()
    #passo parmetri alla view    
    return render_template("home.html", query=query, tracks=tracks, albums=albums, top_tracks=top_tracks)


@page.route("/track/<int:track_id>")
@login_required
def track_detail(track_id):
    data =  get_track_info(track_id)

    if not data:
        return render_template("track_detail.html", track=None, error="Track non trovata :(")

    track = data["response"]["song"]
    return render_template("track_detail.html", track=track)

@page.route("/album/<int:album_id>")
@login_required
def album_detail(album_id):
    data = get_album_info(album_id)

    if not data:
        return render_template("album_detail.html", album=None, error="Album non trovato :(")

    album = data["response"]["album"]
    return render_template("album_detail.html", album=album)
