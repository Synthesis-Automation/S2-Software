
def is_float(x):
    try:
        float(x)
        if str(x) in ['inf', 'infinity', 'INF', 'INFINITY', 'True', 'NAN', 'nan', 'False', '-inf', '-INF', '-INFINITY', '-infinity', 'NaN', 'Nan']:
            return False
        else:
            return True
    except:
        return False



a = "0.5"

print(isFloat(a))


a = ""

print(isFloat(a))