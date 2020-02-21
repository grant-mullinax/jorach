def find_by_id(l, id: str):
    for x in l:
        if x.name.lower() == id.lower():
            return x
    return None