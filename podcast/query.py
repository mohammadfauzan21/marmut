def podcast():
    return f""" 
        SELECT K.id AS id_konten, K.judul AS judul_podcast, A.nama AS nama_podcaster, K.durasi AS durasi_podcast
        FROM podcast P
        JOIN konten K ON P.id_konten = K.id
        JOIN podcaster Po ON P.email_podcaster = Po.email
        JOIN akun A ON Po.email = A.email
        ORDER BY K.durasi DESC;
    """