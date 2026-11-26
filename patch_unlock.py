import re, sys, pathlib

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
PREP = "const PREP = now < new Date(2026, 11, 1, 19, 0, 0); // режим подготовки: замки сняты"

files = sorted(root.glob("day*/index.html"))
hub = root / "index.html"
if hub.exists():
    files.append(hub)
if not files:
    print(f"❌ В папке {root.resolve()} не найдено ни day*/index.html, ни index.html.")
    print("Запускай скрипт из корня сайта: cd advent-sites && python patch_unlock.py")
    sys.exit(1)

total = 0
for f in files:
    src = f.read_text(encoding="utf-8")
    lines = src.splitlines()
    out, prep_added, log = [], False, []

    for ln in lines:
        t = ln.strip()

        if t.startswith("const PREP"):
            prep_added = True
            out.append(ln)
            continue

        if not prep_added and (t.startswith("const now=") or t.startswith("const now =")):
            out.append(ln)
            out.append(PREP)
            prep_added = True
            log.append("PREP")
            continue

        if t.startswith("const open"):
            out.append('const open = q.has("all") || PREP || (inDec && (DAY < today || (DAY === today && now.getHours() >= 19)));')
            log.append("open")
            continue

        if t.startswith("const past"):
            out.append('const past = !q.has("all") && (inDec && DAY < today);')
            log.append("past")
            continue

        if t.startswith("else if") and "|| past)" in t and ("solved()" in t or "daySolved()" in t):
            m = re.search(r"else if\s*\(\s*([\w$]+\(\)\s*\|\|\s*past)\s*\)", t)
            if m:
                out.append(t.replace(m.group(0), f'else if (!q.has("all") && ({m.group(1)}))'))
                log.append("архив-ветка")
                continue
            out.append(ln)
            continue

        if t.startswith("const isOpen"):
            out.append('const isOpen = d => preview || PREP || (inDec && (d < today || (d === today && now.getHours() >= OPEN_HOUR))) || (afterDec && d <= 31);')
            log.append("isOpen")
            continue

        if t.startswith("const last") and "preview" in t and "?31" in t.replace(" ", ""):
            out.append('const last = (preview || PREP) ? 31 : (inDec || afterDec ? Math.min(31, grownDays) : 0);')
            log.append("журнал")
            continue

        out.append(ln)

    if not prep_added:
        log.append("⚠️ НЕ нашёл строку const now= — PREP не вставлен")
    if log:
        f.write_text("\n".join(out) + "\n", encoding="utf-8")
        total += 1
        print(f"✔ {f.name if f.parent == root else f.parent.name + '/' + f.name}: " + ", ".join(log))
    else:
        print(f"… {f.parent.name}/{f.name}: изменений не потребовалось")

print(f"\nГотово, обработано файлов: {total} из {len(files)}")
print("Теперь: git add . && git commit -m 'unlock prep' && git push — и сайт обновится.")