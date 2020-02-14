

# Confirm that value is an int or can be converted to an int
def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


# Convert 'True' or 'False' to boolean True or False
def str2bool(value):
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return value.lower() in ['true', '1']
    else:
        return False
