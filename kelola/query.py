def detail_episode(id_konten):
    return f"""
        SELECT id_episode, judul, deskripsi, durasi, tanggal_rilis
        FROM episode
        WHERE id_konten_podcast = '{id_konten}'
    """

def durasi_podcast(id_konten):
    return f"""
        SELECT SUM(durasi)
        FROM episode
        WHERE id_konten_podcast = '{id_konten}'
    """

def delete_genre(id_konten):
    return f"""
        DELETE FROM GENRE
        WHERE id_konten = '{id_konten}'
    """

def add_genre(id_konten, genre):
    return f"""
        INSERT INTO GENRE (id_konten, genre)
        VALUES ('{id_konten}', '{genre}')
    """

def delete_song_playlist(id_konten):
    return f"""
        DELETE FROM PLAYLIST_SONG
        WHERE id_song = '{id_konten}'
    """

def delete_album_query(id_album):
    return f"""
        DELETE FROM ALBUM
        WHERE id = '{id_album}'
    """

def get_id_playlist(id_user_playlist):
    return f"""
        SELECT id_playlist FROM USER_PLAYLIST
        WHERE id_user_playlist = '{id_user_playlist}'
    """

def delete_playlist_song(id_playlist):
    return f"""
        DELETE FROM PLAYLIST_SONG
        WHERE id_playlist = '{id_playlist}'
    """

def delete_playlist_query(id_playlist):
    return f"""
        DELETE FROM PLAYLIST
        WHERE id = '{id_playlist}'
    """

def get_id_pemilik_hak_cipta_label(id_label):
    return f"""
        SELECT id_pemilik_hak_cipta FROM label
        WHERE id = '{id_label}'
    """

def get_id_pemilik_hak_cipta_artist(id_artist):
    return f"""
        SELECT id_pemilik_hak_cipta FROM artist
        WHERE id = '{id_artist}'
    """

def get_id_pemilik_hak_cipta_songwriter(id_songwriter):
    return f"""
        SELECT id_pemilik_hak_cipta FROM songwriter
        WHERE id = '{id_songwriter}'
    """