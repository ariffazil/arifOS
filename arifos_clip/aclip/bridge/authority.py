# Authority token validation

def validate_token(token):
    """
    Validate the authority token provided by user.
    In this basic implementation, any non-empty token is considered valid.
    (In a real scenario, this could check against a registry or perform cryptographic verification.)
    """
    return token is not None and token != ""
