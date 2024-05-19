def get_user_playlist():
    return """
        SELECT judul, nama, total_durasi, id_playlist
        FROM akun, user_playlist 
        where email=email_pembuat;
    """

def get_detail_playlist(id_playlist):
    return f"""
        SELECT konten.judul, akun.nama, konten.durasi, song.id_konten
        FROM konten, akun, song, artist, playlist_song 
        WHERE konten.id=song.id_konten AND song.id_artist=artist.id AND artist.email_akun=akun.email AND playlist_song.id_song=song.id_konten AND playlist_song.id_playlist= '{id_playlist}'
    """

def get_detail_playlist_header(id_playlist):
    return f"""
        SELECT nama, jumlah_lagu, total_durasi, tanggal_dibuat, judul, deskripsi FROM akun, user_playlist WHERE id_playlist='{id_playlist}' AND email=email_pembuat
    """

def get_detail_song(id_konten):
    return f"""
        SELECT konten.judul, akun.nama, array_agg(genre.genre), konten.durasi, konten.tanggal_rilis, konten.tahun, song.total_play, song.total_download, album.judul, song.id_konten
        FROM song 
        left JOIN konten ON song.id_konten=konten.id
        left JOIN album ON song.id_album=album.id
        left JOIN artist ON song.id_artist=artist.id
        left JOIN akun ON akun.email=artist.email_akun 
        left JOIN genre ON genre.id_konten=konten.id
        WHERE song.id_konten='{id_konten}'
        GROUP BY konten.judul, akun.nama, konten.durasi, konten.tanggal_rilis, konten.tahun, song.total_play, song.total_download, album.judul, song.id_konten
    """

def get_songwriter_song(id_konten):
    return f"""
        SELECT a.nama
        FROM akun as a
        JOIN songwriter as sr ON sr.email_akun=a.email
        JOIN songwriter_write_song as sws ON sws.id_songwriter=sr.id
        WHERE sws.id_song = '{id_konten}'
    """

def get_playlist_akun(email):
    return f"""
        SELECT * 
        FROM user_playlist WHERE email_pembuat='{email}'
    """

def delete_akun_play_user_playlist(id_user_playlist):
    return f"""
        DELETE FROM akun_play_user_playlist WHERE id_user_playlist = '{id_user_playlist}'
    """

def delete_user_playlist(id_user_playlist):
    return f"""
        DELETE FROM user_playlist WHERE id_user_playlist = '{id_user_playlist}'
    """

def insert_id_playlist(id_playlist):
    return f"""
        INSERT INTO playlist (id) VALUES ('{id_playlist}')
    """

def insert_user_playlist(email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi):
    return f"""
        INSERT INTO user_playlist (email_pembuat, id_user_playlist, judul, deskripsi, jumlah_lagu, tanggal_dibuat, id_playlist, total_durasi) VALUES ('{email_pembuat}', '{id_user_playlist}', '{judul}', '{deskripsi}', {jumlah_lagu}, '{tanggal_dibuat}', '{id_playlist}', {total_durasi})
    """

def insert_id_playlist(id_playlist):
    return f"""
        INSERT INTO playlist (id) VALUES ('{id_playlist}')
    """

def ubah_playlist_query(judul, deskripsi, id_playlist):
    return f"""
        UPDATE user_playlist SET judul = '{judul}', deskripsi = '{deskripsi}' WHERE id_playlist = '{id_playlist}'
    """

def show_song():
    return f"""
        SELECT konten.id, konten.judul, akun.nama
        FROM konten
        JOIN song ON konten.id=song.id_konten
        JOIN artist ON artist.id=song.id_artist
        JOIN akun ON akun.email=artist.email_akun
    """

def add_song(id_song, id_playlist):
    return f"""
        INSERT INTO playlist_song (id_playlist, id_song) VALUES ('{id_playlist}', '{id_song}')
    """

def check_song(id_song, id_playlist):
    return f"""
        SELECT * FROM playlist_song WHERE id_playlist = '{id_playlist}' AND id_song = '{id_song}'
    """
