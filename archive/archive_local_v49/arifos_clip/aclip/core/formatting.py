import json

def output_result(data, as_json=False):
    """
    Print the result data either as JSON (if as_json is True) or as a plain string.
    If data is a dict or list and as_json is False, prints it in a condensed form.
    """
    if as_json:
        print(json.dumps(data, indent=2))
    else:
        if isinstance(data, (dict, list)):
            # Print a one-line summary for dict/list
            print(json.dumps(data))
        else:
            print(str(data))
