def try_parse_int64(string):
    try:
        ret = int(string)
    except ValueError:
        return None
    return None if ret < -2 ** 64 or ret >= 2 ** 64 else ret

def try_parse_time(string):
    try:
        t_vec = [try_parse_int64(t) for t in string.split(":")]
        t_hh_sec = float(t_vec[0]) * 3600.0
        t_mm_sec = float(t_vec[1]) * 60.0
        t_ss_sec = round(float(t_vec[2]))

        t_vec_sec = t_hh_sec + t_mm_sec + t_ss_sec
        if any(t < 0 for t in t_vec) or any(t >= 60 for t in t_vec[1 :]):
            return None
        else:
            return int(round(t_vec_sec))
    except IndexError:
        return None
