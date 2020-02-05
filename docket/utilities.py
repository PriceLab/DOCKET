

# Confirm that value is an int or can be converted to an int
def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
