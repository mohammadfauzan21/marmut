def check_email_pengguna(email):
    return f"""
        SELECT email 
        FROM AKUN 
        WHERE email='{email}' 
    """

def check_email_label(email):
    return f"""
        SELECT email 
        FROM LABEL 
        WHERE email='{email}' 
    """