def mongo_to_dict(obj):
    return_data = []
    for v in obj:
        data = {}
        for field_name in v:
            if field_name == '_id':
                data[field_name] = str(v[field_name])
            else:
                data[field_name] = v[field_name]
        return_data.append(data)
    return return_data
