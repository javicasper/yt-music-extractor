from flask import Flask, jsonify, request
from ytmusicapi import YTMusic
import requests

app = Flask(__name__)

# Inicializar la API de YouTube Music
yt_music = YTMusic('browser.json')

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
            print(query)
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
        print(f"Buscando: {query} con filtro: {filter_type}")
        if not query:
            return jsonify({"error": "Debe proporcionar un parámetro 'q' para la búsqueda."}), 400

        # Realizar la búsqueda en YouTube Music con filtro si se proporciona
        search_results = yt_music.search(query, filter=filter_type)

        # Si no hay resultados y se usó un filtro, intentar una búsqueda general
        if not search_results and filter_type:
            print("Sin resultados con el filtro. Intentando búsqueda general...")
            search_results = yt_music.search(query)

        # Formatear los resultados de búsqueda
        formatted_results = []
        for result in search_results:
            if result['resultType'] in ['song', 'video', 'album', 'artist', 'playlist']:
                formatted_result = {
                    "title": result.get('title', 'Sin título'),
                    "resultType": result['resultType'],
                }

                if 'artists' in result:
                    formatted_result["artist"] = ", ".join(artist['name'] for artist in result['artists'])

                if result['resultType'] == 'song':
                    formatted_result["album"] = result.get('album', {}).get('name', 'Sin álbum')
                    formatted_result["videoId"] = result.get('videoId', 'No disponible')
                elif result['resultType'] == 'album':
                    formatted_result["browseId"] = result.get('browseId', 'No disponible')
                elif result['resultType'] == 'artist':
                    formatted_result["artistId"] = result.get('browseId', 'No disponible')
                elif result['resultType'] == 'playlist':
                    formatted_result["playlistId"] = result.get('browseId', 'No disponible')

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
        # Obtener los datos de la playlist
        playlist_data = yt_music.get_playlist(playlist_id)

        # Formatear los datos
        playlist_info = {
            "title": playlist_data['title'],
            "description": playlist_data.get('description', 'Sin descripción'),
            "trackCount": playlist_data['trackCount'],
            "tracks": []
        }

        # Limitar la búsqueda al primer track
        if playlist_data['tracks']:
            track = playlist_data['tracks'][0]  # Solo el primer track
            
            # Verificar si el campo 'album' existe y no es None
            album = track.get('album')
            album_name = album['name'] if album else 'Sin álbum'

            # Verificar si hay artistas
            artist_name = track['artists'][0]['name'] if track.get('artists') else "Artista desconocido"

            # Obtener el ISRC desde Deezer
            isrc = buscar_isrc_en_deezer(track.get('title', 'Sin título'), artist_name, album_name)

            # Añadir la canción al JSON de respuesta
            playlist_info["tracks"].append({
                "title": track.get('title', 'Sin título'),
                "artist": artist_name,
                "album": album_name,
                "videoId": track.get('videoId', 'No disponible'),
                "isrc": isrc
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
