import re

# Intentar diferentes encodings
encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

content = None
used_encoding = None

for enc in encodings:
    try:
        with open('templates/containers/_service_rows.html', 'r', encoding=enc) as f:
            content = f.read()
        used_encoding = enc
        print(f"Successfully read with encoding: {enc}")
        break
    except UnicodeDecodeError:
        continue

if content is None:
    print("ERROR: Could not read file with any encoding")
    exit(1)

# Reemplazar todas las comparaciones sin espacios
content = re.sub(r'status=="', 'status == "', content)
content = re.sub(r'status !="', 'status != "', content)

# Guardar el archivo con UTF-8
with open('templates/containers/_service_rows.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Template fixed successfully! (Original encoding: {used_encoding})")
