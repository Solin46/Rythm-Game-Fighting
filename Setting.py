import os
import pygame as pg
import Spnotes as sp

SETTINGS_FILE = "settings_save.txt"

music_volume = 0.5
note_speed_factor = 1.0

def save_settings():
    with open(SETTINGS_FILE, "w") as f:
        f.write(f"{music_volume}\n")
        f.write(f"{note_speed_factor}\n")

def load_settings():
    global music_volume, note_speed_factor
    if not os.path.exists(SETTINGS_FILE):
        save_settings()
    else:
        with open(SETTINGS_FILE, "r") as f:
            lines = f.readlines()
            try:
                if len(lines) >= 2:
                    music_volume = float(lines[0].strip())
                    note_speed_factor = float(lines[1].strip())
            except:
                pass

WIDTH, HEIGHT = 1200, 700
FPS = 60

all_sprites = pg.sprite.Group()
heros = pg.sprite.Group()
enemies = pg.sprite.Group()
notes = pg.sprite.Group()

x = [347, 577, 810]

TITLE = "Rythm game fighting"

game_folder = os.path.dirname(__file__)
img = os.path.join(game_folder, "img")
img_folder=os.path.join(img,"imgUnconstant")
Constant_img=os.path.join(img,"Constant")

backgrounds = []
enemies_image = []
heros_image = []
notes_image = []
menu = []

hero_order = [1, 2, 3]
enemy_order = [1, 2, 3, 4]

def find_image_by_order(files, order_num):

    for f in files:
        if f.lower().endswith((".png", ".jpg", ".jpeg")) and str(order_num) in f:
            return f
    return None


heros_image_dict = {
    "kick": {},
    "snare": {},
    "hihat": {}
}

def load_images():
    global backgrounds, enemies_image, heros_image, menu, notes_image

    backgrounds.clear()
    enemies_image.clear()
    heros_image.clear()
    menu.clear()
    notes_image.clear()

    menu_f = os.path.join(img_folder, "menu")
    for file in sorted(os.listdir(menu_f)):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
            path = os.path.join(menu_f, file)
            image = pg.image.load(path).convert()
            image = pg.transform.scale(image, (WIDTH, HEIGHT))
            menu.append(image)


    enemies_f = os.path.join(img_folder, "Enemies")
    for folder in sorted(os.listdir(enemies_f)):
        folder_path = os.path.join(enemies_f, folder)
        if os.path.isdir(folder_path):
            files = os.listdir(folder_path)
            images = []
            for num in enemy_order:
                filename = find_image_by_order(files, num)
                if filename is None:
                    break
                full_path = os.path.join(folder_path, filename)
                img = pg.image.load(full_path).convert_alpha()
                images.append(img)
            if len(images) == len(enemy_order):
                enemies_image.append(images)

    heros_f = os.path.join(img_folder, "Heros")
    for folder in sorted(os.listdir(heros_f)):
        folder_path = os.path.join(heros_f, folder)
        if os.path.isdir(folder_path):
            if folder.startswith("kick"):
                role = "kick"
            elif folder.startswith("snare"):
                role = "snare"
            elif folder.startswith("hihat"):
                role = "hihat"
            else:
                continue

            hero_id = folder[len(role):]
            files = os.listdir(folder_path)
            images = []
            for num in hero_order:
                filename = find_image_by_order(files, num)
                if filename is None:
                    break
                full_path = os.path.join(folder_path, filename)
                img = pg.image.load(full_path).convert_alpha()
                images.append(img)
            if len(images) == len(hero_order):
                heros_image_dict[role][hero_id] = images

    notes_f = os.path.join(img_folder, "Notes")
    for i in range(3):
        note_folder = os.path.join(notes_f, f"Note{i+1}")
        found = False
        if os.path.isdir(note_folder):
            for file in sorted(os.listdir(note_folder)):
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    image_path = os.path.join(note_folder, file)
                    notes_image.append(image_path)
                    found = True
                    break


coin=os.path.join(Constant_img,"coinGold.png")
levels = [
    {
        "unlocked": True,
        "enemy_index": 0,
        "enemy_health": 2290,
        "note_speed": 5,
    },
    {
        "unlocked": False,
        "enemy_index": 1,
        "enemy_health": 2000,
        "note_speed": 6,
    },
    {
        "unlocked": False,
        "enemy_index": 2,
        "enemy_health": 2000,
        "note_speed": 7,
    },
    {
        "unlocked": False,
        "enemy_index": 3,
        "enemy_health": 2000,
        "note_speed": 10,
    },
]



