def search_query_song(query):
    return f""" 
        SELECT DISTINCT konten.judul, akun.nama, konten.tanggal_rilis, song.total_play, song.id_konten
        FROM song
        JOIN konten ON konten.id=song.id_konten
        JOIN artist ON song.id_artist=artist.id
        JOIN akun ON akun.email=artist.email_akun
        WHERE konten.judul ILIKE '%{query}%'
    """

def search_query_album(query):
    return f""" 
        SELECT DISTINCT album.judul, label.nama, album.jumlah_lagu, album.total_durasi, album.id
        FROM album
        JOIN label ON label.id=album.id_label
        WHERE album.judul ILIKE '%{query}%'
    """

def search_query_playlist(query):
    return f""" 
        SELECT DISTINCT user_playlist.judul, akun.nama, user_playlist.total_durasi, user_playlist.tanggal_dibuat, user_playlist.id_playlist
        FROM user_playlist
        JOIN akun ON akun.email=user_playlist.email_pembuat
        WHERE user_playlist.judul ILIKE '%{query}%'
    """