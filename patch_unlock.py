import re, pathlib

root = pathlib.Path(__file__).parent
PREP = 'const PREP = now < new Date(2026, 11, 1, 19, 0, 0); // режим подготовки: замки сняты\n'
changed = 0

for f in sorted(root.glob("day*/index.html")):
    s = f.read_text(encoding="utf-8"); o = s
    # 1) PREP + разблокировка open
    s = re.sub(
        r'const open\s*=\s*q\.has\("all"\)\s*\|\|\s*\(inDec[^\n]*\n',
        PREP + 'const open = q.has("all") || PREP || (inDec && (DAY < today || (DAY === today && now.getHours() >= 19)));\n',
        s, count=1)
    # 2) past больше не включает ?all=1
    s = re.sub(
        r'const past\s*=\s*q\.has\("all"\)\s*\|\|\s*\(inDec\s*&&\s*DAY\s*<\s*today\)\s*;\s*\n',
        'const past = !q.has("all") && (inDec && DAY < today);\n',
        s, count=1)
    # 3) архив (сразу ответ) пропускаем в предпросмотре
    s = re.sub(
        r'else if\s*\(\s*(daySolved|solved)\(\)\s*\|\|\s*past\s*\)',
        lambda m: f'else if (!q.has("all") && ({m.group(1)}() || past))',
        s, count=1)
    if s != o:
        f.write_text(s, encoding="utf-8"); changed += 1; print("✔", f)
    else:
        print("… не тронул:", f)

hub = root / "index.html"
s = hub.read_text(encoding="utf-8"); o = s
s = re.sub(
    r'const isOpen\s*=\s*d\s*=>\s*preview[^\n]*\n',
    PREP + 'const isOpen = d => preview || PREP || (inDec && (d < today || (d === today && now.getHours() >= OPEN_HOUR))) || (afterDec && d <= 31);\n',
    s, count=1)
s = re.sub(
    r'const last\s*=\s*preview\s*\?\s*31\s*:',
    'const last = (preview || PREP) ? 31 :',
    s, count=1)
if s != o:
    hub.write_text(s, encoding="utf-8"); changed += 1; print("✔", hub)
print(f"Готово, изменено файлов: {changed}")
