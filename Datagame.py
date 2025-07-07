import os

money = 0
balance = 5
total_missed = 0
current_level_index = 0

selected_kick = "0"
selected_snare = "0"
selected_hihat = "0"
selected_bg = "0"

unlocked_heroes = {
    "kick": {"0"},
    "snare": {"0"},
    "hihat": {"0"}
}

unlocked_backgrounds = {"0"}

SAVE_PATH = "save.txt"

def save_progress():
    with open(SAVE_PATH, "w") as f:
        f.write(f"{money}\n")
        f.write(f"{selected_kick},{selected_snare},{selected_hihat},{selected_bg}\n")
        f.write(",".join(unlocked_heroes["kick"]) + "\n")
        f.write(",".join(unlocked_heroes["snare"]) + "\n")
        f.write(",".join(unlocked_heroes["hihat"]) + "\n")
        f.write(",".join(unlocked_backgrounds) + "\n")
    print("[SAVE] Прогресс сохранён!")

def load_progress():
    global money, selected_kick, selected_snare, selected_hihat, selected_bg
    global unlocked_heroes, unlocked_backgrounds

    if not os.path.exists(SAVE_PATH):
        print("[LOAD] Файл сохранения не найден.")
        return

    try:
        with open(SAVE_PATH, "r") as f:
            lines = f.read().splitlines()

        if len(lines) < 6:
            print("[LOAD] Файл сохранения повреждён или не полный.")
            return

        money = int(lines[0])

        sk, ss, sh, sb = lines[1].split(",")
        selected_kick = sk.strip()
        selected_snare = ss.strip()
        selected_hihat = sh.strip()
        selected_bg = sb.strip()

        if selected_bg.startswith("background"):
            selected_bg = selected_bg[len("background"):]

        unlocked_heroes = {
            "kick": set(filter(None, map(str.strip, lines[2].split(",")))) or {"0"},
            "snare": set(filter(None, map(str.strip, lines[3].split(",")))) or {"0"},
            "hihat": set(filter(None, map(str.strip, lines[4].split(",")))) or {"0"},
        }

        bg_list = list(filter(None, map(str.strip, lines[5].split(","))))
        unlocked_backgrounds = set()
        for bg in bg_list:
            bg_clean = bg
            if bg.startswith("background"):
                bg_clean = bg[len("background"):]
            unlocked_backgrounds.add(bg_clean)
        if not unlocked_backgrounds:
            unlocked_backgrounds = {"0"}
        unlocked_backgrounds_sorted = sorted(unlocked_backgrounds, key=int)

        print("[LOAD] Прогресс загружен:")
        print(f"       Деньги: {money}")
        print(f"       Выбран Kick: {selected_kick}")
        print(f"       Выбран Snare: {selected_snare}")
        print(f"       Выбран HiHat: {selected_hihat}")
        print(f"       Выбран Background: {selected_bg}")
        print(f"       Разблокировано Kick: {unlocked_heroes['kick']}")
        print(f"       Разблокировано Snare: {unlocked_heroes['snare']}")
        print(f"       Разблокировано HiHat: {unlocked_heroes['hihat']}")
        print(f"       Разблокировано Backgrounds (множество): {unlocked_backgrounds}")
        print(f"       Разблокировано Backgrounds (отсортировано): {unlocked_backgrounds_sorted}")

    except Exception as e:
        import traceback
        print("[LOAD] Ошибка загрузки прогресса:", e)
        traceback.print_exc()

def load_last_money():
    load_progress()
    return money
