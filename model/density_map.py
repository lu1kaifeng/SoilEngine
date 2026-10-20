db_map = {
    ('sand','loamy sand'):[1.6,1.8],
    ('sandy loam','loam'):[1.4,1.8],
    ('sandy clay loam','clay loam'):[1.4,1.75],
    ('silt','silt loam'):[1.3,1.75],
    ('silty clay loam'):[1.4,1.65],
    ('sandy clay','silty clay'):[1.1,1.58],
    ('clay'):[1.1,1.47]
}
db = dict()
for kk,v in db_map.items():
    for k in kk:
        db[k] = v

db_map = db

def if_compacted(texture,db_val):
    if texture is None:
        return False
    texture = texture.strip().lower()
    if texture in db:
        return db_val>= db[texture][1]
    else:
        return False