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