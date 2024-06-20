def get_user_playlist():
    return """
        SELECT user_playlist.judul, akun.nama, user_playlist.total_durasi, user_playlist.id_playlist
        FROM user_playlist
        JOIN akun ON user_playlist.email_pembuat = akun.email
        ORDER BY user_playlist.total_durasi DESC;
    """

def get_detail_playlist(id_playlist):
    return f"""
        SELECT konten.judul, akun.nama, konten.durasi, song.id_konten
        FROM konten, akun, song, artist, playlist_song 
        WHERE konten.id=song.id_konten AND song.id_artist=artist.id AND artist.email_akun=akun.email AND playlist_song.id_song=song.id_konten AND playlist_song.id_playlist= '{id_playlist}'
    """

def get_detail_playlist_header(id_playlist):
    return f"""
        SELECT 
            akun.nama, COALESCE(COUNT(playlist_song.id_song),0) AS jumlah_lagu, COALESCE(SUM(konten.durasi), 0) AS total_durasi, user_playlist.tanggal_dibuat, user_playlist.judul, 
            user_playlist.deskripsi
            FROM akun 
            LEFT JOIN user_playlist ON akun.email = user_playlist.email_pembuat
            LEFT JOIN playlist on playlist.id=user_playlist.id_playlist
            LEFT JOIN playlist_song on playlist_song.id_playlist=playlist.id
            LEFT JOIN song ON playlist_song.id_song = song.id_konten
            LEFT JOIN konten ON song.id_konten = konten.id
            WHERE user_playlist.id_playlist = '{id_playlist}'
            GROUP BY akun.nama, playlist_song.id_playlist, user_playlist.tanggal_dibuat, user_playlist.judul, user_playlist.deskripsi
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

def create_new_album(id_album, judul, id_label):
    return f"""
        INSERT INTO album (id, judul, id_label) VALUES ('{id_album}', '{judul}', '{id_label}')
    """

def add_song_to_album(id_konten, id_artist, id_album):
    return f"""
        INSERT INTO song (id_konten, id_artist, id_album) VALUES ('{id_konten}', '{id_artist}', '{id_album}')
    """

def add_konten(id_konten, judul, tanggal_rilis, durasi):
    return f"""
        INSERT INTO konten (id, judul, tanggal_rilis, durasi) VALUES ('{id_konten}', '{judul}', '{tanggal_rilis}', '{durasi}')
    """

def add_songwriter(id_songwriter, id_song):
    return f"""
        INSERT INTO songwriter_write_song (id_songwriter, id_song) VALUES ('{id_songwriter}', '{id_song}')
    """

def add_genre(id_konten, genre):
    return f"""
        INSERT INTO genre (id_konten, genre) VALUES ('{id_konten}', '{genre}')
    """

def user_id_artist(email):
    return f"""
        SELECT id 
        FROM artist 
        JOIN AKUN ON email_akun=email
        WHERE email='{email}'
    """

def user_id_songwriter(email):
    return f"""
        SELECT id 
        FROM songwriter 
        JOIN AKUN ON email_akun=email
        WHERE email='{email}'
    """

def show_album(email_artist):
    return f"""
        (SELECT DISTINCT album.id, album.judul, album.jumlah_lagu, album.total_durasi, label.id_pemilik_hak_cipta
        FROM album
        JOIN song ON album.id=id_album
        JOIN artist ON artist.id=song.id_artist
        JOIN label ON label.id=album.id_label
        WHERE artist.email_akun='{email_artist}')
        UNION
        (SELECT DISTINCT album.id, album.judul, album.jumlah_lagu, album.total_durasi, label.id_pemilik_hak_cipta
        FROM album
        JOIN song ON album.id=id_album
        JOIN label ON label.id=album.id_label
        WHERE label.email='{email_artist}')
        UNION
        (SELECT DISTINCT album.id, album.judul, album.jumlah_lagu, album.total_durasi, label.id_pemilik_hak_cipta
        FROM album
        JOIN song ON album.id=id_album
        JOIN label ON label.id=album.id_label
        JOIN songwriter_write_song ON songwriter_write_song.id_song=song.id_konten
        JOIN songwriter ON songwriter.id=songwriter_write_song.id_songwriter
        WHERE songwriter.email_akun='{email_artist}')
    """

def delete_album(id_album):
    return f"""
        DELETE FROM album WHERE id = '{id_album}'
    """

def delete_song(id_album):
    return f"""
        DELETE FROM song WHERE id_album = '{id_album}'
    """

def delete_album_songwriter_write_song(id_album):
    return f"""
        DELETE FROM songwriter_write_song 
        WHERE id_song in (
            SELECT id_konten 
            FROM song
            WHERE id_album = '{id_album}'
        )
    """

def delete_album_playlist_song(id_album):
    return f"""
        DELETE FROM playlist_song 
        WHERE id_song in (
            SELECT id_konten 
            FROM song
            WHERE id_album = '{id_album}'
        )
    """

def delete_album_akun_play_song(id_album):
    return f"""
        DELETE FROM akun_play_song
        WHERE id_song in (
            SELECT id_konten 
            FROM song
            WHERE id_album = '{id_album}'
        )
    """

def delete_album_downloaded_song(id_album):
    return f"""
        DELETE FROM downloaded_song
        WHERE id_song in (
            SELECT id_konten 
            FROM song
            WHERE id_album = '{id_album}'
        )
    """

def delete_album_royalti(id_album):
    return f"""
        DELETE FROM royalti
        WHERE id_song in (
            SELECT id_konten 
            FROM song
            WHERE id_album = '{id_album}'
        )
    """

def get_detail_album_header(id_album):
    return f"""
        SELECT label.nama, album.total_durasi, album.jumlah_lagu, album.judul
        FROM album
        JOIN label ON album.id_label=label.id
        WHERE album.id='{id_album}'
    """

def get_detail_album(id_album):
    return f"""
        SELECT konten.id, konten.judul, konten.durasi, song.total_play, song.total_download 
        FROM album
        JOIN song ON album.id=song.id_album
        JOIN konten ON song.id_konten=konten.id
        WHERE album.id='{id_album}'
    """

def get_artist_id_pemilik_hak_cipta(user_email):
    return f"""
        SELECT id_pemilik_hak_cipta
        FROM artist
        WHERE email_akun='{user_email}'
    """

def get_songwriter_id_pemilik_hak_cipta(user_email):
    return f"""
        SELECT id_pemilik_hak_cipta
        FROM songwriter
        WHERE email_akun='{user_email}'
    """

def add_royalti(id_pemilik_hak_cipta, id_song):
    return f"""
        INSERT INTO royalti (id_pemilik_hak_cipta, id_song, jumlah) VALUES ('{id_pemilik_hak_cipta}', '{id_song}', 0)
    """