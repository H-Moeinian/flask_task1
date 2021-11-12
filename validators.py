def non_empty_string(s):
    if not s:
        raise ValueError
    return s


def age_validator(age):
    if age == "":
        return age
    try:
        age = int(age)
    except:
        raise ValueError
    if age < 0 or age > 300:
        raise ValueError
    return age