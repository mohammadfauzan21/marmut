def show_label():
    return f"""
        SELECT *
        FROM label as l, pemilik_hak_cipta as p
        WHERE l.id_pemilik_hak_cipta=p.id
    """

def show_artist():
    return f"""
        SELECT a.id, nama
        FROM artist a
        JOIN pemilik_hak_cipta p ON a.id_pemilik_hak_cipta=p.id
        JOIN akun n ON a.email_akun=n.email
    """

def show_songwriter():
    return f"""
        SELECT s.id, nama
        FROM songwriter s
        JOIN pemilik_hak_cipta p ON s.id_pemilik_hak_cipta=p.id
        JOIN akun n ON s.email_akun=n.email
    """

def show_genre():
    return f"""
        SELECT id_konten, genre
        FROM genre g
        JOIN konten k ON k.id=g.id_konten
    """

def user_info(email):
    return f"""
            SELECT a.nama, a.email, a.kota_asal, 
                CASE WHEN a.gender = 0 THEN 'Laki-Laki' ELSE 'Perempuan' END AS gender,
                a.tempat_lahir
            FROM akun a
            WHERE a.email = '{email}'
        """