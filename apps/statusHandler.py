def handler(status, datas, types=None, code=None, message=None):
    infos = {}
    infos["status"] = status
    if datas:
        infos["datas"] = datas
    if types:
        infos["type"] = types
    if code:
        infos["code"] = code
    if message:
        infos["message"] = message
    return infos
