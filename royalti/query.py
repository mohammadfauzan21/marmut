def show_royalti_artist(user_email):
    return f"""
        SELECT DISTINCT konten.judul AS SONG, album.judul AS ALBUM, song.total_play, song.total_download, royalti.jumlah
        FROM SONG
        JOIN KONTEN ON song.id_konten=konten.id
        JOIN ALBUM ON song.id_album=album.id
        JOIN ROYALTI ON song.id_konten=royalti.id_song
        JOIN ARTIST ON song.id_artist=artist.id
        WHERE artist.email_akun='{user_email}'
    """

def show_royalti_songwriter(user_email):
    return f"""
        SELECT DISTINCT konten.judul AS SONG, album.judul AS ALBUM, song.total_play, song.total_download, royalti.jumlah
        FROM SONG
        JOIN KONTEN ON song.id_konten=konten.id
        JOIN ALBUM ON song.id_album=album.id
        JOIN ROYALTI ON song.id_konten=royalti.id_song
        JOIN SONGWRITER_WRITE_SONG ON songwriter_write_song.id_song=song.id_konten
        JOIN SONGWRITER ON songwriter.id=songwriter_write_song.id_songwriter
        WHERE songwriter.email_akun='{user_email}'
    """