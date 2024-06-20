def show_royalti_artist(user_email):
    return f"""
        SELECT DISTINCT konten.judul AS SONG, album.judul AS ALBUM, song.total_play, song.total_download, royalti.jumlah
        FROM SONG
        JOIN KONTEN ON song.id_konten=konten.id
        JOIN ALBUM ON song.id_album=album.id
        JOIN ARTIST ON song.id_artist=artist.id
        JOIN pemilik_hak_cipta ON pemilik_hak_cipta.id=artist.id_pemilik_hak_cipta
        JOIN ROYALTI ON royalti.id_pemilik_hak_cipta=pemilik_hak_cipta.id
        WHERE artist.email_akun='{user_email}'
    """

def show_royalti_songwriter(user_email):
    return f"""
        SELECT K.judul AS SONG, A.judul AS ALBUM, S.total_play, S.total_download, R.jumlah
        FROM song S
        JOIN konten K ON S.id_konten = K.id
        LEFT JOIN album A ON S.id_album = A.id
        JOIN royalti R ON S.id_konten = R.id_song
        JOIN pemilik_hak_cipta PH ON PH.id = R.id_pemilik_hak_cipta
        JOIN songwriter SW ON SW.id_pemilik_hak_cipta = PH.id
        WHERE SW.email_akun = '{user_email}'
        ORDER BY K.tanggal_rilis ASC
    """

def show_royalti_label(user_email):
    return f"""
        SELECT DISTINCT konten.judul AS SONG, album.judul AS ALBUM, song.total_play, song.total_download, royalti.jumlah
        FROM SONG
        JOIN KONTEN ON song.id_konten=konten.id
        JOIN ALBUM ON song.id_album=album.id
        JOIN LABEL ON label.id=album.id_label
        JOIN pemilik_hak_cipta ON pemilik_hak_cipta.id=label.id_pemilik_hak_cipta
        JOIN ROYALTI ON royalti.id_pemilik_hak_cipta=pemilik_hak_cipta.id
        WHERE label.email='{user_email}'
    """

def total_royalti_artist(user_email):
    return f"""
        SELECT royalti.id_pemilik_hak_cipta, SUM(royalti.jumlah) AS total_royalti
        FROM royalti
        JOIN pemilik_hak_cipta ON pemilik_hak_cipta.id=royalti.id_pemilik_hak_cipta
        JOIN artist ON artist.id_pemilik_hak_cipta=pemilik_hak_cipta.id
        WHERE artist.email_akun='{user_email}'
        GROUP BY royalti.id_pemilik_hak_cipta;
    """

def total_royalti_songwriter(user_email):
    return f"""
        SELECT royalti.id_pemilik_hak_cipta, SUM(royalti.jumlah) AS total_royalti
        FROM royalti
        JOIN pemilik_hak_cipta ON pemilik_hak_cipta.id=royalti.id_pemilik_hak_cipta
        JOIN songwriter ON songwriter.id_pemilik_hak_cipta=pemilik_hak_cipta.id
        WHERE songwriter.email_akun='{user_email}'
        GROUP BY royalti.id_pemilik_hak_cipta;
    """

def total_royalti_label(user_email):
    return f"""
        SELECT royalti.id_pemilik_hak_cipta, SUM(royalti.jumlah) AS total_royalti
        FROM royalti
        JOIN pemilik_hak_cipta ON pemilik_hak_cipta.id=royalti.id_pemilik_hak_cipta
        JOIN label ON label.id_pemilik_hak_cipta=pemilik_hak_cipta.id
        WHERE label.email='{user_email}'
        GROUP BY royalti.id_pemilik_hak_cipta;
    """