from flask import Flask, jsonify, request
from ytmusicapi import YTMusic
import requests

app = Flask(__name__)

# Inicializar la API de YouTube Music
yt_music = YTMusic('browser.json', language='es')

# Función para buscar el ISRC en Deezer
def buscar_isrc_en_deezer(titulo, artista, album):
    try:
        # Construir la URL de búsqueda de Deezer
        base_url = "https://api.deezer.com/search"
        query = f'{titulo} {artista}'
        url = f"{base_url}?q={query}"

        # Realizar la solicitud
        response = requests.get(url)
        if response.status_code == 200:
            resultados = response.json()
            if resultados['data']:
                for cancion in resultados['data']:
                    # Verificar coincidencias estrictas en título y artista
                    if (titulo.lower() in cancion['title'].lower() and
                        artista.lower() in cancion['artist']['name'].lower()):
                        track_id = cancion.get('id')
                        if track_id:
                            track_url = f"https://api.deezer.com/track/{track_id}"
                            track_response = requests.get(track_url)
                            if track_response.status_code == 200:
                                track_data = track_response.json()
                                return track_data.get('isrc', 'ISRC no disponible')
        return 'ISRC no disponible'
    except Exception as e:
        print(f"Error al buscar ISRC: {e}")
        return 'Error al obtener ISRC'

@app.route('/search', methods=['GET'])
def buscar_cancion():
    try:
        # Obtener los parámetros de consulta y filtro
        query = request.args.get('q', '')
        filter_type = request.args.get('filter', 'songs')  # Valor por defecto: None
        if not query:
            return jsonify({"error": "Debe proporcionar un parámetro 'q' para la búsqueda."}), 400

        # Realizar la búsqueda en YouTube Music con filtro si se proporciona
        search_results = yt_music.search(query, filter=filter_type, ignore_spelling=True)

        # Si no hay resultados y se usó un filtro, intentar una búsqueda general
        if not search_results and filter_type:
            print("Sin resultados con el filtro. Intentando búsqueda general...")
            search_results = yt_music.search(query)

        # Formatear los resultados de búsqueda
        formatted_results = []
        for result in search_results:
            if result['resultType'] in ['song', 'video', 'album', 'artist', 'playlist']:
                formatted_result = {
                    "resultType": result['resultType'],
                }

                if 'artists' in result:
                    formatted_result["artist"] = ", ".join(artist['name'] for artist in result['artists'])

                if result['resultType'] == 'song':
                    print("result", result)
                    formatted_result["title"] = result.get('title', 'Sin título')
                    # formatted_result["album"] = result.get('album', {}).get('name', 'Sin álbum')
                    formatted_result["videoId"] = result.get('videoId', 'No disponible')
                    formatted_result["channel"] = result.get('channel', 'No disponible')
                    formatted_result["duration"] = result.get('duration', 'No disponible')
                    formatted_result["thumbnails"] = result['thumbnails'][-1]['url'] if result.get('thumbnails') else None
                elif result['resultType'] == 'album':
                    formatted_result["albumId"] = result.get('browseId', 'No disponible')
                    formatted_result["album"] = result.get('title', 'Sin título')
                    formatted_result["browseId"] = result.get('browseId', 'No disponible')
                elif result['resultType'] == 'artist':
                    formatted_result["artistId"] = result.get('browseId', 'No disponible')
                    formatted_result["artist"] = result.get('artist', 'Sin nombre')
                    formatted_result["shuffleId"] = result.get('shuffleId', 'No disponible')
                    formatted_result["radioId"] = result.get('radioId', 'No disponible')
                elif result['resultType'] == 'playlist':
                    formatted_result["playlistId"] = result.get('browseId', 'No disponible')
                    formatted_result["title"] = result.get('title', 'Sin título')
                    formatted_result["thumbnail"] = result['thumbnails'][-1]['url'] if result.get('thumbnails') else None

                formatted_results.append(formatted_result)

        # Si no hay resultados, devolver un mensaje
        if not formatted_results:
            return jsonify({"message": "No se encontraron resultados para la búsqueda."}), 404

        return jsonify({"results": formatted_results})

    except Exception as e:
        print(f"Error en la búsqueda: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/playlist/<string:playlist_id>', methods=['GET'])
def obtener_playlist(playlist_id):
    try:
        use_isrc = request.args.get('isrc', 'false').lower() == 'true'
        # Obtener los datos de la playlist
        playlist_data = yt_music.get_playlist(playlist_id)
        print(playlist_data)
        
        # Formatear los datos
        playlist_info = {
            "title": playlist_data['title'],
            "description": playlist_data.get('description', 'Sin descripción'),
            "trackCount": playlist_data['trackCount'],
            "tracks": []
        }

        # Procesar cada canción en la playlist
        for track in playlist_data['tracks']:
            # Verificar si el campo 'album' existe y no es None
            album = track.get('album')
            album_name = album['name'] if album else 'Sin álbum'

            # Verificar si hay artistas
            artist_name = (
                track['artists'][0]['name'] if track.get('artists') else "Artista desconocido"
            )

            if use_isrc:
                # Buscar el ISRC en Deezer
                isrc = buscar_isrc_en_deezer(track['title'], artist_name, album_name)
                track['isrc'] = isrc

            # Añadir la canción al JSON de respuesta
            playlist_info["tracks"].append({
                "title": track.get('title', 'Sin título'),
                "artist": artist_name,
                "album": album_name,
                "videoId": track.get('videoId', 'No disponible'),
                "isrc": track.get('isrc', '')
            })

        # Devolver la respuesta como JSON
        return jsonify(playlist_info)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/user_playlists', methods=['GET'])
def obtener_playlists_usuario():
    try:
        # Obtener las playlists públicas del usuario
        playlists = yt_music.get_library_playlists()

        # Formatear las playlists en JSON
        playlists_info = [
            {
                "title": playlist['title'],
                "playlistId": playlist['playlistId'],
                "count": playlist.get('count', 0),
                "thumbnail": playlist['thumbnails'][-1]['url'] if playlist.get('thumbnails') else None
            }
            for playlist in playlists
        ]

        return jsonify(playlists_info)

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
