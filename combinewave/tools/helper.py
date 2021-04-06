import re, json

def get_float_number(string):
    numbers = [float(s) for s in re.findall(r'-?\d+\.?\d*', string)]
    return numbers[-1]  # return the last number as float

def inverse_dict(my_dict):
    return {value: key for key, value in my_dict.items()}

def format_json_file(json_file_name):
    with open(json_file_name, 'r+') as f:
        old_data = json.load(f)
        f.seek(0)
        f.write(json.dumps(old_data, indent=4))
        f.truncate()


def is_float(x):
    '''test a string or number could be converted to a float'''
    try:
        float(x)
        if str(x) in ['inf', 'infinity', 'INF', 'INFINITY', 'True', 'NAN', 'nan', 'False', '-inf', '-INF', '-INFINITY', '-infinity', 'NaN', 'Nan']:
            return False
        else:
            return True
    except:
        return False


if __name__ == "__main__":
    my = {1:"ccc"}
    print(inverse_dict(my))
    # for i in range(10):
    #     no = convert_number_to_A1(i, 5, 7)
    #     print(i, no)
