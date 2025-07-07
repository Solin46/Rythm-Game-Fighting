import pygame as pg
import os
import Datagame

Datagame.load_progress()

WIDTH, HEIGHT = 1200, 700
FPS = 60

CATEGORIES = ["kick", "snare", "hihat", "background"]

CATEGORY_FOLDERS = {
    "kick": "kick",
    "snare": "snare",
    "hihat": "hihat",
    "background": "background"
}

CATEGORY_DISPLAY_NAMES = {
    "kick": "Kick",
    "snare": "Snare",
    "hihat": "HiHat",
    "background": "Background"
}

BASE_PRICE = {
    "kick": 100,
    "snare": 100,
    "hihat": 100,
    "background": 120
}

def get_price_for_item(category, item_id, index):
    if item_id == "0" or item_id.endswith("0"):
        return 0
    if category == "background":
        return BASE_PRICE[category]
    return BASE_PRICE[category] + 50 * index

def load_assets_for_category(category):
    base_path = os.path.join("img", "imgUnconstant")
    if category == "background":
        category_path = os.path.join(base_path, "background")
        items = []
        if os.path.isdir(category_path):
            for file in sorted(os.listdir(category_path)):
                if file.lower() == "background0.jpg":
                    continue
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    item_id = os.path.splitext(file)[0]
                    path = os.path.join(category_path, file)
                    items.append((item_id, path))
        return items
    else:
        heroes_path = os.path.join(base_path, "heros")
        folder_name = CATEGORY_FOLDERS[category]
        items = []
        if os.path.isdir(heroes_path):
            folders = [f for f in os.listdir(heroes_path) if f.startswith(folder_name)]
            for folder in sorted(folders):
                item_id = folder[len(folder_name):]
                if item_id == "0":
                    continue
                folder_path = os.path.join(heroes_path, folder)
                if os.path.isdir(folder_path):
                    items.append((item_id, folder_path))
        return items


def draw_text(surface, text, size, x, y, color=(74, 59, 32)):
    font = pg.font.Font(None, size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x,y))

def store_screen(screen):
    pg.mouse.set_visible(True)
    clock = pg.time.Clock()
    running = True

    category_index = 0
    selected_index = 0

    preview_anim_time = 0
    preview_frame_index = 0
    PREVIEW_FRAME_DELAY = 777

    def get_items(cat):
        return load_assets_for_category(cat)

    items = get_items(CATEGORIES[category_index])

    while running:
        dt = clock.tick(FPS)
        preview_anim_time += dt

        if preview_anim_time >= PREVIEW_FRAME_DELAY:
            preview_anim_time = 0
            preview_frame_index += 1

        screen.fill((234, 205, 171))
        draw_text(screen, "МАГАЗИН", 64, WIDTH//2 - 100, 20, (74, 59, 32))

        cat = CATEGORIES[category_index]
        draw_text(screen, f"Категория: {CATEGORY_DISPLAY_NAMES[cat]}", 36, 50, 100)
        draw_text(screen, f"Монеты: {Datagame.money}", 28, WIDTH - 220, 20, (74, 59, 32))

        for i, (item_id, path) in enumerate(items):
            y = 150 + i * 50
            color = (255, 255, 0) if i == selected_index else (74, 59, 32)

            if cat == "background":
                unlocked = item_id in Datagame.unlocked_backgrounds
                is_selected = item_id == Datagame.selected_bg
            else:
                unlocked = item_id in Datagame.unlocked_heroes[cat]
                is_selected = (
                    (cat == "kick" and item_id == Datagame.selected_kick) or
                    (cat == "snare" and item_id == Datagame.selected_snare) or
                    (cat == "hihat" and item_id == Datagame.selected_hihat)
                )

            price = get_price_for_item(cat, item_id, i)

            if unlocked:
                status = "(Куплено, Выбрано)" if is_selected else "(Куплено)"
            else:
                status = f"(Цена: {price})"

            draw_text(screen, f"{item_id} {status}", 28, 100, y, color)

        preview_rect = pg.Rect(WIDTH - 350, 150, 189, 297)
        pg.draw.rect(screen, (74, 59, 32), preview_rect)

        if items:
            sel_item_id, sel_path = items[selected_index]
            try:
                if cat == "background":
                    img = pg.image.load(sel_path).convert()
                    img = pg.transform.scale(img, (preview_rect.width - 20, preview_rect.height - 20))
                    screen.blit(img, (preview_rect.x + 10, preview_rect.y + 10))
                else:
                    imgs = sorted([f for f in os.listdir(sel_path) if f.lower().endswith((".png", ".jpg"))])
                    if imgs:
                        frame_count = len(imgs)
                        current_frame = preview_frame_index % frame_count
                        img_path = os.path.join(sel_path, imgs[current_frame])
                        img = pg.image.load(img_path).convert_alpha()
                        img = pg.transform.scale(img, (preview_rect.width - 40, preview_rect.height - 40))
                        screen.blit(img, (preview_rect.x + 20, preview_rect.y + 20))
            except Exception:
                pass

        for event in pg.event.get():
            if event.type == pg.QUIT:
                Datagame.save_progress()
                running = False
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_TAB:
                    category_index = (category_index + 1) % len(CATEGORIES)
                    items = get_items(CATEGORIES[category_index])
                    selected_index = 0
                    preview_frame_index = 0
                    preview_anim_time = 0
                elif event.key == pg.K_UP:
                    selected_index = (selected_index - 1) % len(items)
                    preview_frame_index = 0
                    preview_anim_time = 0
                elif event.key == pg.K_DOWN:
                    selected_index = (selected_index + 1) % len(items)
                    preview_frame_index = 0
                    preview_anim_time = 0
                elif event.key == pg.K_RETURN and items:
                    sel_item_id, _ = items[selected_index]

                    if cat == "background":
                        unlocked = sel_item_id in Datagame.unlocked_backgrounds
                    else:
                        unlocked = sel_item_id in Datagame.unlocked_heroes[cat]

                    price = get_price_for_item(cat, sel_item_id, selected_index)

                    if not unlocked:
                        if Datagame.money >= price:
                            Datagame.money -= price
                            if cat == "background":
                                Datagame.unlocked_backgrounds.add(sel_item_id)
                            else:
                                Datagame.unlocked_heroes[cat].add(sel_item_id)
                            Datagame.save_progress()
                            print(f"[ПОКУПКА] Разблокирован {cat}: {sel_item_id}")
                            items = get_items(cat)
                        else:
                            print("[ПОКУПКА] Недостаточно монет!")
                    else:
                        if cat == "background":
                            Datagame.selected_bg = sel_item_id
                        elif cat == "kick":
                            Datagame.selected_kick = sel_item_id
                        elif cat == "snare":
                            Datagame.selected_snare = sel_item_id
                        elif cat == "hihat":
                            Datagame.selected_hihat = sel_item_id
                        Datagame.save_progress()
                        items = get_items(cat)
                elif event.key == pg.K_ESCAPE:
                    Datagame.save_progress()
                    running = False

        pg.display.flip()
