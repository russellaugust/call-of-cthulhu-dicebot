def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def RepresentsBool(s):
    if s.lower() == "true" or s.lower() == "false":
        return True
    else:
        return False

def convertToBool(s):
    if s.lower() == "true":
        return True
    else:
        return False