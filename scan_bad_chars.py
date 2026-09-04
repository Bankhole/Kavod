import os
bad=[]
root='c:/Users/HP/Desktop/DjangoProjects/Kavod'
for dirpath, _, files in os.walk(root):
    for f in files:
        if not f.endswith(('.py','.html','.txt','.js','.css','.md','.json')):
            continue
        p = os.path.join(dirpath, f)
        try:
            data = open(p, 'rb').read()
        except Exception:
            continue
        for i, b in enumerate(data):
            if b < 32 and b not in (9, 10, 13):
                bad.append((p, i, b))
                if len(bad) >= 20:
                    break
        if len(bad) >= 20:
            break
    if len(bad) >= 20:
        break
print('BAD_COUNT', len(bad))
for item in bad[:20]:
    print(item)
