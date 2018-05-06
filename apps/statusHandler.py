def handler(status, data, types=None, code=None, message=None):
    infos = {}
    infos["status"] = status
    if data:
        infos["data"] = data
    if types:
        infos["type"] = types
    if code:
        infos["code"] = code
    if message:
        infos["message"] = message
    return infos
