from apps import redisMode, statusHandler


def limitIP(ip):
    r = redisMode.redisMode()
    keyname = "ip:{}".format(ip)
    limit_ip = r.redisCheck(keyname)
    if limit_ip is not None and int(limit_ip) > 9:
        data = statusHandler.handler(
            1, None, message="Too many requests per second")
        return data
    else:
        r.redisCounter(keyname)
