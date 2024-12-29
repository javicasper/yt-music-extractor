# YouTube Music & Deezer ISRC Extractor

Este proyecto es una API Flask que utiliza la **YouTube Music API** (implementada con la librería [ytmusicapi](https://github.com/sigma67/ytmusicapi)) y la **Deezer API** para buscar canciones, playlists y extraer información como el código ISRC (International Standard Recording Code).

## Características

- **Búsqueda de canciones, videos, álbumes, artistas y playlists** en YouTube Music.
- **Endpoints para manejar playlists y búsquedas personalizadas**.
- Opción para incluir ISRC al solicitar detalles de una playlist.

## Requisitos

- Python 3.9 o superior
- Docker (opcional para la ejecución en contenedores)
- Archivo `browser.json` exportado desde tu navegador para autenticar con YouTube Music API.

## Instalación

### Localmente

1. **Clona el repositorio**:
  ```bash
  git clone <repo-url>
  cd <repo-folder>
  ```

2. **Crea un entorno virtual**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate  # En Windows: .\\venv\\Scripts\\activate
  ```

3. **Instala las dependencias**:
  ```bash
  pip install -r requirements.txt
  ```

4. **Ejecuta la aplicación**:
  ```bash
  flask run
  ```

  La aplicación estará disponible en `http://localhost:5000`.

---

### Usando Docker

1. **Construye y ejecuta el contenedor**:
  ```bash
  docker-compose up --build
  ```

2. **Accede a la aplicación**:
  La API estará disponible en `http://localhost:5000`.

---

## Endpoints

### `/search`
**Descripción**: Realiza una búsqueda en YouTube Music.

- **Método**: `GET`
- **Parámetros**:
  - `q`: (requerido) Término de búsqueda.
  - `filter`: (opcional) Tipo de contenido (`songs`, `albums`, `artists`, `playlists`, `videos`).

**Ejemplo**:
```bash
curl "http://localhost:5000/search?q=sofia%20gabanna&filter=songs"
```

---

### `/playlist/<playlist_id>`
**Descripción**: Obtiene detalles de una playlist en YouTube Music, con opción de incluir el ISRC de las canciones.

- **Método**: `GET`
- **Parámetros**:
  - `playlist_id`: (requerido) ID de la playlist.
  - `isrc`: (opcional) Si se establece como `true`, intenta buscar el ISRC de cada canción en Deezer.

**Ejemplo**:
```bash
curl "http://localhost:5000/playlist/PLfpNc9SrNdDDvb10-w_RunX9Pq0xJvSBq?isrc=true"
```

---

### `/user_playlists`
**Descripción**: Obtiene todas las playlists públicas asociadas al usuario autenticado.

- **Método**: `GET`

**Ejemplo**:
```bash
curl "http://localhost:5000/user_playlists"
```

---

## Configuración del archivo `browser.json`

El archivo `browser.json` se utiliza para autenticar con YouTube Music API. Puedes generarlo siguiendo las instrucciones del repositorio oficial de [ytmusicapi](https://ytmusicapi.readthedocs.io/en/latest/setup.html).

---

## Seguridad

- **Archivo sensible**: No compartas tu `browser.json` públicamente.
- **Acceso externo**: Si expones la API, utiliza HTTPS y protege los endpoints sensibles.

---

## Licencia

Este proyecto está bajo la [MIT License](LICENSE).
