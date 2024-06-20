def get_info_label(email):
    return f"""
        SELECT id, nama, email, kontak FROM label WHERE email = '{email}'
    """