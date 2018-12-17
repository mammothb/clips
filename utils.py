def try_parse_int64(string):
    try:
        ret = int(string)
    except ValueError:
        return None
    return None if ret < -2 ** 64 or ret >= 2 ** 64 else ret

def try_parse_time(string):
    t_start = [try_parse_int64(t) for t in string.split(":")]
    t_hh_sec = float(t_start[0]) * 3600.0
    t_mm_sec = float(t_start[1]) * 60.0
    t_ss_sec = round(float(t_start[2]))

    t_start_sec = t_hh_sec + t_mm_sec + t_ss_sec
    if (t_start[0] < 0 or t_start[1] < 0 or t_start[2] < 0 or
            t_start[1] >= 60 or t_start[2] >= 60):
        return None
    else:
        return int(round(t_start_sec))
