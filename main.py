import pygame as pg
import random
import Datagame
import os
import numpy as np
import soundfile as sf
from typing import List, Tuple
import Spnotes
from Heros import *
from Enemy import *
from Notes import *
from Setting import *
from Spnotes import *
from gameover import show_game_over
import datetime
from Shop import *
from Effects import HitEffect


SAVE_FILE = "game_save.txt"

def save_stats():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SAVE_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] money:{Datagame.money} balance:{Datagame.balance} missed:{Datagame.total_missed}\n")

def load_last_money():
    if not os.path.exists(SAVE_FILE):
        return 0
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in reversed(lines):
            if "money:" in line:
                parts = line.strip().split()
                for p in parts:
                    if p.startswith("money:"):
                        return int(p.split(":")[1])
    return Datagame.money

def show_history():
    font_h = pg.font.Font(None, 28)
    if not os.path.exists(SAVE_FILE):
        lines = ["пусто"]
    else:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            raw_lines = f.readlines()

        scored_lines = []
        for line in raw_lines:
            parts = line.strip().split()
            balance = None
            for p in parts:
                if p.startswith("balance:"):
                    try:
                        balance = int(p.split(":")[1])
                    except ValueError:
                        balance = 0
            if balance is not None:
                scored_lines.append((balance, line.strip()))

        scored_lines.sort(key=lambda x: x[0], reverse=True)
        lines = [line for _, line in scored_lines]

    while True:
        screen.fill((234, 205, 171))
        title = font_h.render("Лидерборд:", True, (74, 59, 32))
        screen.blit(title, (60, 40))

        for i, line in enumerate(lines[:15]):
            text = font_h.render(line, True, (74, 59, 32))
            screen.blit(text, (60, 80 + i * 30))

        back = font_h.render("[Esc] Назад", True, (74, 59, 32))
        screen.blit(back, (60, HEIGHT - 60))
        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                return


def level_select_menu():
    font_sel = pg.font.Font(None, 40)
    selected = Datagame.current_level_index
    total_levels = len(levels)

    exit_pos = (WIDTH // 2 + 10, HEIGHT - 75)

    while True:
        screen.blit(menu[1], (0, 0))

        positions = [
            (WIDTH // 4 - 100, HEIGHT // 3 - 30),
            (WIDTH // 4 - 100, HEIGHT // 3 + 190),
            (3 * WIDTH // 4 - 100, HEIGHT // 3 - 30),
            (3 * WIDTH // 4 - 100, HEIGHT // 3 + 190),
        ]

        mouse_pos = pg.mouse.get_pos()

        for i in range(min(4, total_levels)):
            color = (255, 255, 255)
            rect = pg.Rect(*positions[i], 200, 100)
            if rect.collidepoint(mouse_pos):
                color = (255, 255, 180)
                selected = i
            if selected == i:
                color = (255, 255, 0)

            lvl_text = font_sel.render(f"Уровень {i+1}", True, color)
            text_rect = lvl_text.get_rect(center=(positions[i][0] + 100, positions[i][1] + 50))
            screen.blit(lvl_text, text_rect)

        exit_color = (234, 205, 171)
        exit_text_surface = font_sel.render("[Esc] Меню", True, exit_color)
        exit_text_rect = exit_text_surface.get_rect(center=exit_pos)
        screen.blit(exit_text_surface, exit_text_rect)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    return False
                elif event.key == pg.K_RETURN:
                    Datagame.current_level_index = selected
                    return True
                elif event.key == pg.K_LEFT:
                    if selected == 2:
                        selected = 0
                    elif selected == 3:
                        selected = 1
                elif event.key == pg.K_RIGHT:
                    if selected == 0 and total_levels > 2:
                        selected = 2
                    elif selected == 1 and total_levels > 3:
                        selected = 3
                elif event.key == pg.K_UP:
                    if selected in (1, 3):
                        selected -= 1
                elif event.key == pg.K_DOWN:
                    if selected in (0, 2) and selected + 1 < total_levels:
                        selected += 1
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(min(4, total_levels)):
                    rect = pg.Rect(*positions[i], 200, 100)
                    if rect.collidepoint(mouse_pos):
                        Datagame.current_level_index = i
                        return True
                if exit_text_rect.collidepoint(mouse_pos):
                    return False

def show_settings_menu(screen):
    font = pg.font.Font(None, 40)
    selected = 0
    options = ["Громкость: ", "Скорость нот: ", "Назад"]

    global music_volume, note_speed_factor

    while True:
        screen.fill((234, 205, 171))
        for i, option in enumerate(options):
            color = (255, 255, 0) if i == selected else (74, 59, 32)
            value = ""
            if i == 0:
                value = f"{int(music_volume * 100)}%"
            elif i == 1:
                value = f"{note_speed_factor:.1f}x"
            text = font.render(option + value, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pg.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pg.K_LEFT:
                    if selected == 0:
                        music_volume = max(0.0, music_volume - 0.1)
                        pg.mixer.music.set_volume(music_volume)
                    elif selected == 1:
                        note_speed_factor = max(0.5, note_speed_factor - 0.1)
                elif event.key == pg.K_RIGHT:
                    if selected == 0:
                        music_volume = min(1.0, music_volume + 0.1)
                        pg.mixer.music.set_volume(music_volume)
                    elif selected == 1:
                        note_speed_factor = min(2.0, note_speed_factor + 0.1)
                elif event.key == pg.K_RETURN and selected == 2:
                    save_settings()
                    return

pg.init()
pg.mixer.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption("Ритм-игра: Битва")
clock = pg.time.Clock()
font = pg.font.Font(None, 30)

hit_zone = pg.Rect(190, HEIGHT - 390, WIDTH - 400, 83)

load_images()
coin_image = pg.image.load(coin).convert_alpha()
coin_image = pg.transform.scale(coin_image, (32, 32))

all_sprites = pg.sprite.Group()
heros = pg.sprite.Group()
enemies = pg.sprite.Group()
notes = pg.sprite.Group()
spawned_notes = set()
effects_group = pg.sprite.Group()

Datagame.money = load_last_money()
Datagame.balance = 5
Datagame.total_missed = 0

def endless_mode_loop():
    endless_dir = "endless"

    music_path = None
    for ext in [".mp3", ".ogg", ".wav"]:
        candidate = os.path.join(endless_dir, "instr" + ext)
        if os.path.exists(candidate):
            music_path = candidate
            break

    if music_path:
        pg.mixer.music.load(music_path)
        pg.mixer.music.set_volume(music_volume)
        pg.mixer.music.play(-1)
    else:
        print("Музыка для бесконечного режима не найдена")

    bg_path = None
    for ext in [".png", ".jpg", ".jpeg"]:
        candidate = os.path.join(endless_dir, "background" + ext)
        if os.path.exists(candidate):
            bg_path = candidate
            break
    if bg_path:
        background = pg.image.load(bg_path).convert()
        background = pg.transform.scale(background, (WIDTH, HEIGHT))
    else:
        background = pg.Surface((WIDTH, HEIGHT))
        background.fill((20, 20, 20))

    Spnotes.notes = sp.generate_notes_from_parts(
        kick_path=os.path.join(endless_dir, "kick.wav"),
        snare_path=os.path.join(endless_dir, "snare.wav"),
        hihat_closed_path=os.path.join(endless_dir, "hh_closed.wav"),
        hihat_open_path=os.path.join(endless_dir, "hh_open.wav"),
        time_offset=-0.8,
        fall_speed=600.0,
    )

    load_heroes(None)

    all_sprites.empty()
    notes.empty()
    heros.empty()
    effects_group.empty()
    spawned_notes.clear()

    start_time = pg.time.get_ticks() / 1000.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        current_time = pg.time.get_ticks() / 1000.0
        elapsed = current_time - start_time

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False

        for note_data in Spnotes.notes:
            spawn_time = note_data["time"]
            note_type = note_data["type"]
            note_key = (spawn_time, note_type)
            if note_key not in spawned_notes and abs(elapsed - spawn_time) < 0.03:
                spawn_note(note_type)
                spawned_notes.add(note_key)

        all_sprites.update(dt)
        effects_group.update(dt)

        screen.blit(background, (0, 0))
        heros.draw(screen)
        notes.draw(screen)
        pg.draw.rect(screen, (255, 255, 0), hit_zone, 3)
        pg.display.flip()

def show_modes_menu():
    font = pg.font.Font(None, 48)
    small_font = pg.font.Font(None, 32)
    running = True

    selected_index = 0
    modes = ["Бесконечный режим", "Челленджи (скоро)"]

    while running:
        screen.fill((50, 50, 80))
        draw_text(screen, "Режимы игры", 60, WIDTH // 2 - 150, 50, (255, 255, 255))

        for i, mode in enumerate(modes):
            if i == selected_index:
                color = (255, 255, 0)
            else:
                color = (150, 150, 150)

            y_pos = 200 + i * 60
            screen_text = mode if i == 0 else mode + "..."
            draw_text(screen, screen_text, 36, 60, y_pos, color)

        draw_text(screen, "[Enter] - выбрать", 28, 60, HEIGHT - 100, (255, 255, 255))
        draw_text(screen, "[Esc] - назад", 28, 60, HEIGHT - 60, (255, 255, 255))

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_RETURN:
                    if selected_index == 0:
                        endless_mode_loop()
                elif event.key in (pg.K_UP, pg.K_DOWN):
                    pass


def load_level(level_index):
    level = levels[level_index]
    bg_path = None
    bg_dir = os.path.join("img", "imgUnconstant", "background")
    for ext in [".jpg", ".png", ".jpeg"]:
        candidate = os.path.join(bg_dir, f"background{Datagame.selected_bg}{ext}")
        if os.path.exists(candidate):
            bg_path = candidate
            break

    if bg_path:
        background = pg.image.load(bg_path).convert()
        background = pg.transform.scale(background, (WIDTH, HEIGHT))
    else:
        background = pg.Surface((WIDTH, HEIGHT))
        background.fill((0, 0, 0))  # fallback фон
    enemy_images = enemies_image[level["enemy_index"]]
    new_enemy = Enemy(enemy_images, level["enemy_health"], level["enemy_health"])
    note_speed = level["note_speed"] * note_speed_factor
    Spnotes.notes = generate_notes_from_parts(
        kick_path=f"{Datagame.current_level_index}/kick.wav",
        snare_path=f"{Datagame.current_level_index}/snare.wav",
        hihat_closed_path=f"{Datagame.current_level_index}/hh_closed.wav",
        hihat_open_path=f"{Datagame.current_level_index}/hh_open.wav",
        fall_speed=600.0,
        time_offset=-0.8,
    )
    return background, new_enemy, note_speed

def load_heroes(level_index):
    for h in heros.sprites():
        all_sprites.remove(h)
    heros.empty()

    hero_ids = [
        Datagame.selected_kick,
        Datagame.selected_snare,
        Datagame.selected_hihat,
    ]

    heros_list = []
    categories = ["kick", "snare", "hihat"]

    for idx, hero_id in enumerate(hero_ids):
        category = categories[idx]
        hero_images = heros_image_dict[category].get(str(hero_id), [])
        if not hero_images:
            print(f"Ошибка: нет изображений для героя {category}{hero_id}")
            continue
        hero = Heros(hero_images, idx)
        heros.add(hero)
        all_sprites.add(hero)
        heros_list.append(hero)
    Notes.set_heros_group(heros_list)

def spawn_note(num):
    image_path = notes_image[num]
    image = pg.image.load(image_path).convert_alpha()
    note = Notes(x[num], image, hit_zone, num, note_speed * -1)
    all_sprites.add(note)
    notes.add(note)

def draw_money(surface, font):
    coin_x = 25
    coin_y = HEIGHT - 211
    surface.blit(coin_image, (coin_x, coin_y))
    money_text = font.render(str(Datagame.money), True, (255, 255, 255))
    surface.blit(money_text, (coin_x + 30, coin_y + 10))

def main_menu():
    title_font = pg.font.Font(None, 70)
    menu_font = pg.font.Font(None, 40)
    selected_index = 0
    buttons = [
        {"text": "Выбор уровня", "pos": (WIDTH // 3.2, 250), "action": lambda: "level_transition"},
        {"text": "Магазин", "pos": (WIDTH // 3.2, 390), "action": lambda: (Datagame.load_progress(), store_screen(screen), "menu")[2]},
        {"text": "Настройки", "pos": (WIDTH // 3.2, 530), "action": lambda: (show_settings_menu(screen), "menu")[1]},
        {"text": "Режимы", "pos": (2 * WIDTH // 3, 250), "action": lambda: (show_modes_menu(), "menu")[1]},
        {"text": "Лидерборд", "pos": (2 * WIDTH // 3, 390), "action": lambda: (show_history(), "menu")[1]},
        {"text": "Инструкция", "pos": (2 * WIDTH // 3, 530), "action": lambda: (show_help(), "menu")[1]},
        {"text": "Выйти", "pos": (WIDTH // 2, 640), "action": lambda: "exit"}
    ]
    grid = [
        [0, 3],
        [1, 4],
        [2, 5],
        [6, 6]
    ]
    index_to_grid = {idx: (i, j) for i, row in enumerate(grid) for j, idx in enumerate(row)}
    grid_to_index = {(i, j): idx for i, row in enumerate(grid) for j, idx in enumerate(row)}

    while True:
        screen.fill((10, 10, 30))
        screen.blit(menu[0], (0, 0))
        mouse_pos = pg.mouse.get_pos()

        for i, button in enumerate(buttons):
            color = (234, 205, 171)
            text_surface = menu_font.render(button["text"], True, color)
            rect = text_surface.get_rect(center=button["pos"])

            if rect.collidepoint(mouse_pos):
                selected_index = i
                text_surface = menu_font.render(button["text"], True, (255, 255, 200))
            elif i == selected_index:
                text_surface = menu_font.render(button["text"], True, (255, 255, 200))

            screen.blit(text_surface, rect)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if selected_index in index_to_grid:
                    i, j = index_to_grid[selected_index]
                    if event.key == pg.K_LEFT and (i, j - 1) in grid_to_index:
                        selected_index = grid_to_index[(i, j - 1)]
                    elif event.key == pg.K_RIGHT and (i, j + 1) in grid_to_index:
                        selected_index = grid_to_index[(i, j + 1)]
                    elif event.key == pg.K_UP and (i - 1, j) in grid_to_index:
                        selected_index = grid_to_index[(i - 1, j)]
                    elif event.key == pg.K_DOWN and (i + 1, j) in grid_to_index:
                        selected_index = grid_to_index[(i + 1, j)]
                    elif event.key == pg.K_RETURN:
                        result = buttons[selected_index]["action"]()
                        if result == "exit":
                            return "exit"
                        elif result == "level_transition":
                            Datagame.load_progress()
                            return "level_transition"

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                for i, button in enumerate(buttons):
                    text_surface = menu_font.render(button["text"], True, (234, 205, 171))
                    rect = text_surface.get_rect(center=button["pos"])
                    if rect.collidepoint(mouse_pos):
                        result = button["action"]()
                        if result == "exit":
                            return "exit"
                        elif result == "level_transition":
                            Datagame.load_progress()
                            return "level_transition"
                        break

def character_selection_menu(screen):
    font = pg.font.Font(None, 36)
    selected_kick = Datagame.selected_kick
    selected_snare = Datagame.selected_snare
    selected_hihat = Datagame.selected_hihat
    selected_bg = Datagame.selected_bg

    categories = ["kick", "snare", "hihat", "background"]

    selections = {
        "kick": selected_kick,
        "snare": selected_snare,
        "hihat": selected_hihat,
        "background": selected_bg
    }

    unlocked = {
        "kick": sorted(Datagame.unlocked_heroes["kick"], key=int),
        "snare": sorted(Datagame.unlocked_heroes["snare"], key=int),
        "hihat": sorted(Datagame.unlocked_heroes["hihat"], key=int),
        "background": sorted(Datagame.unlocked_backgrounds, key=int)
    }

    cat_index = 0
    preview_anim_time = 0
    preview_frame_index = 0
    PREVIEW_FRAME_DELAY = 777
    clock = pg.time.Clock()

    while True:
        dt = clock.tick(60)
        preview_anim_time += dt

        if preview_anim_time >= PREVIEW_FRAME_DELAY:
            preview_anim_time = 0
            preview_frame_index += 1

        screen.fill((234, 205, 171))
        cat = categories[cat_index]
        draw_text(screen, "Выбор состава", 48, WIDTH//2 - 140, 30, (74, 59, 32))
        draw_text(screen, f"Категория: {CATEGORY_DISPLAY_NAMES[cat]}", 36, 60, 100)
        draw_text(screen, "[Tab] Переключить категорию", 24, 60, HEIGHT - 100)
        draw_text(screen, "[Up][Down] Переключить предмет", 24, 60, HEIGHT - 70)
        draw_text(screen, "[Enter] Подтвердить выбор", 24, 60, HEIGHT - 40)

        options = unlocked[cat]
        if options:
            selected = selections[cat]
            selected_idx = options.index(selected) if selected in options else 0
            for i, opt in enumerate(options):
                color = (255, 255, 0) if i == selected_idx else (74, 59, 32)
                draw_text(screen, f"{opt}", 28, 100, 160 + i * 40, color)

            selections[cat] = options[selected_idx]

            preview_rect = pg.Rect(WIDTH - 350, 150, 189, 297)
            pg.draw.rect(screen, (74, 59, 32), preview_rect)

            if cat == "background":
                bg_path = None
                bg_dir = os.path.join("img", "imgUnconstant", "background")
                for ext in [".png", ".jpg", ".jpeg"]:
                    candidate = os.path.join(bg_dir, f"background{options[selected_idx]}{ext}")
                    if os.path.exists(candidate):
                        bg_path = candidate
                        break
                if bg_path:
                    try:
                        img = pg.image.load(bg_path).convert()
                        img = pg.transform.scale(img, (preview_rect.width - 20, preview_rect.height - 20))
                        screen.blit(img, (preview_rect.x + 10, preview_rect.y + 10))
                    except Exception as e:
                        print(f"Ошибка предпросмотра фона: {e}")
            else:
                folder = f"{cat}{options[selected_idx]}"
                hero_path = os.path.join("img", "imgUnconstant", "heros", folder)
                if os.path.isdir(hero_path):
                    frames = sorted([
                        f for f in os.listdir(hero_path)
                        if f.lower().endswith((".png", ".jpg", ".jpeg"))
                    ])
                    if frames:
                        frame_count = len(frames)
                        current_frame = preview_frame_index % frame_count
                        frame_path = os.path.join(hero_path, frames[current_frame])
                        try:
                            img = pg.image.load(frame_path).convert_alpha()
                            img = pg.transform.scale(img, (preview_rect.width - 40, preview_rect.height - 40))
                            screen.blit(img, (preview_rect.x + 20, preview_rect.y + 20))
                        except Exception as e:
                            print(f"Ошибка предпросмотра героя: {e}")

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_TAB:
                    cat_index = (cat_index + 1) % len(categories)
                    preview_frame_index = 0
                elif event.key == pg.K_UP:
                    if options:
                        idx = options.index(selections[cat]) if selections[cat] in options else 0
                        idx = (idx - 1) % len(options)
                        selections[cat] = options[idx]
                        preview_frame_index = 0
                elif event.key == pg.K_DOWN:
                    if options:
                        idx = options.index(selections[cat]) if selections[cat] in options else 0
                        idx = (idx + 1) % len(options)
                        selections[cat] = options[idx]
                        preview_frame_index = 0
                elif event.key == pg.K_RETURN:
                    Datagame.selected_kick = selections["kick"]
                    Datagame.selected_snare = selections["snare"]
                    Datagame.selected_hihat = selections["hihat"]
                    Datagame.selected_bg = selections["background"]
                    Datagame.save_progress()
                    return True
                elif event.key == pg.K_ESCAPE:
                    return None


def start_level_from_selection():
    while True:
        start_game = level_select_menu()
        if not start_game:
            return None

        result = character_selection_menu(screen)
        if result is None:
            return None

        trans_result = level_transition_screen(Datagame.current_level_index)
        if trans_result == "menu":
            return None

        result = game_loop()

        while result == "level_complete":
            if Datagame.current_level_index >= len(levels):
                return True
            trans_result = level_transition_screen(Datagame.current_level_index)
            if trans_result == "menu":
                return None
            result = game_loop()

        if result == "game_over" or result == "exit_to_menu":
            return True


def show_help():
    
    help_font = pg.font.Font(None, 30)

    while True:
        screen.fill((234, 205, 171))
        lines = [
            "Rythm Game Fighting — ритм-игра, в которой герои с помощью барабана, басс-барабана и тарелок",
            "сражаются против врагов. Ваша задача помочь им, попадая по блокам, когда они достигают",
            "выделенного поля.",
            "Управление:",
            "- Нажатие клавиши А активирует удар по блоку в левой дорожке.",
            "- Нажатие клавиши S активирует удар по блоку в средней дорожке.",
            "- Нажатие клавиши D активирует удар по блоку в правой дорожке.",
            "Инструкция:",
            "- Каждый пойманный блок увеличивает счёт ритмичности и денег.",
            "- 5 пропущенных блоков расстраивает героев, и ритмичность обнуляется.",
            "- Накопленные 200 очков ритмичности можно потратить на усиление удара, активировав нажатием на пробел.",
            "- Заработанные монеты можно потратить в магазине на новые скины или бэкгрануды.",
            "",
            "Нажми 'esc', чтобы вернуться к стартовому окну."
        ]

        for i, line in enumerate(lines):
            text = help_font.render(line, True, (74, 59, 32))
            screen.blit(text, (60, 80 + i * 40))
        pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
        clock.tick(60)

def level_transition_screen(level_index):
    trans_font = pg.font.Font(None, 50)
    small_font = pg.font.Font(None, 30)
    save_stats()

    while True:
        screen.fill((234, 205, 171))
        level_text = trans_font.render(f"Уровень {level_index + 1}", True, (74, 59, 32))
        sub_text = small_font.render("Нажмите [Enter], чтобы начать", True, (74, 59, 32))
        esc_text = small_font.render("Нажмите [Esc], чтобы выйти в меню", True, (74, 59, 32))
        balance_info = small_font.render(f"Баланс: {Datagame.balance}", True, (0, 255, 0))
        money_info = small_font.render(f"Монеты: {Datagame.money}", True, (255, 255, 0))
        missed_info = small_font.render(f"Пропущено: {Datagame.total_missed}", True, (255, 100, 100))

        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 180))
        screen.blit(balance_info, (WIDTH // 2 - balance_info.get_width() // 2, 240))
        screen.blit(money_info, (WIDTH // 2 - money_info.get_width() // 2, 280))
        screen.blit(missed_info, (WIDTH // 2 - missed_info.get_width() // 2, 320))
        screen.blit(sub_text, (WIDTH // 2 - sub_text.get_width() // 2, 380))
        screen.blit(esc_text, (WIDTH // 2 - esc_text.get_width() // 2, 420))
        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN:
                    return "start"
                elif event.key == pg.K_ESCAPE:
                    return "menu"

        clock.tick(60)

def pause_menu(screen):
    font = pg.font.Font(None, 50)
    options = ["Продолжить", "Настройки", "Выход в меню"]
    selected = 0

    while True:
        screen.fill((234, 205, 171))
        pause_title = font.render("Пауза", True, (74, 59, 32))
        screen.blit(pause_title, (WIDTH // 2 - pause_title.get_width() // 2, 100))

        for i, option in enumerate(options):
            color = (255, 255, 200) if i == selected else (74, 59, 32)
            text = font.render(option, True, color)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200 + i * 60))

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pg.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pg.K_RETURN:
                    if selected == 0:
                        return "resume"
                    elif selected == 1:
                        show_settings_menu(screen)
                    elif selected == 2:
                        return "exit"

def countdown(screen,seconds=3):
    font_count = pg.font.Font(None, 80)
    start_ticks = pg.time.get_ticks()
    while True:
        screen.fill((234, 205, 171))
        elapsed = (pg.time.get_ticks() - start_ticks) / 1000
        remaining = max(0, seconds - int(elapsed))
        if remaining == 0:
            break
        count_text = font_count.render(str(remaining), True, (74, 59, 32))
        screen.blit(count_text, (WIDTH // 2 - count_text.get_width() // 2, HEIGHT // 2 - count_text.get_height() // 2))
        pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
        clock.tick(60)

HIT_EFFECT_CONFIG = {
    "kick":   {"pos": (352, HEIGHT - 352), "angle": -10},
    "snare":  {"pos": (552, HEIGHT - 352), "angle": -17},
    "hihat_open": {"pos": (732, HEIGHT - 352), "angle": -33},
}

class SuperMode:
    def __init__(self, activation_balance=200, duration=25):
        self.activation_balance = activation_balance
        self.duration = duration
        self.active = False
        self.timer = 0
        self.available = False

    def update(self, dt):
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.deactivate()
        else:
            self.available = Datagame.balance >= self.activation_balance

    def try_activate(self):
        if self.available and not self.active:
            Datagame.balance -= 200
            self.active = True
            self.timer = self.duration
            self.available = False
            return True
        return False

    def deactivate(self):
        self.active = False
        self.timer = 0

    def draw(self, surface, font):
        if self.available and not self.active:
            text = font.render("Нажмите [Пробел] для суперудара!", True, (255, 255, 0))
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))
        elif self.active:
            text = font.render(f"Суперрежим активен: {int(self.timer)} сек", True, (0, 255, 255))
            surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 100))

def game_loop():
    load_settings()
    print("Загружена громкость:", music_volume)
    pg.mixer.music.set_volume(music_volume)
    song_duration = pg.mixer.Sound(f"{Datagame.current_level_index}/instr.wav").get_length()
    global background, enemy, note_speed
    background, enemy, note_speed = load_level(Datagame.current_level_index)

    for en in enemies.sprites():
        all_sprites.remove(en)
    enemies.empty()
    load_heroes(Datagame.current_level_index)
    enemies.add(enemy)
    all_sprites.add(enemy)
    load_settings()
    pg.mixer.music.set_volume(music_volume)
    pg.mixer.music.load(f"{Datagame.current_level_index}/instr.wav")
    pg.mixer.music.play()

    start_time = pg.time.get_ticks() / 1000.0
    spawned_notes.clear()
    Datagame.money = load_last_money()
    Datagame.balance = 5
    Datagame.total_missed = 0
    enemy_dead_wait_time = 0
    enemyisdead = False

    super_mode = SuperMode()
    font = pg.font.SysFont(None, 30)

    while True:
        dt = clock.tick(FPS) / 1000
        current_time = pg.time.get_ticks() / 1000.0
        scnd = current_time - start_time

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    paused_at = pg.time.get_ticks() / 1000.0
                    pg.mixer.music.pause()
                    action = pause_menu(screen)
                    if action == "exit":
                        pg.mixer.music.stop()
                        return "exit_to_menu"
                    elif action == "resume":
                        countdown(screen)
                        resumed_at = pg.time.get_ticks() / 1000.0
                        pause_duration = resumed_at - paused_at
                        start_time += pause_duration
                        pg.mixer.music.unpause()

                elif event.key == pg.K_SPACE:
                    if super_mode.try_activate():
                        print("Суперрежим активирован!")

                else:
                    if not enemyisdead:
                        key_note_map = {
                            pg.K_a: "kick",
                            pg.K_s: "snare",
                            pg.K_d: "hihat_open",
                        }
                        if event.key in key_note_map:
                            expected_type = key_note_map[event.key]
                            for note in notes:
                                if expected_type == note.type and note.is_in_hitzone():
                                    config = HIT_EFFECT_CONFIG.get(note.type)
                                    if config:
                                        start_pos = config["pos"]
                                        angle = config["angle"]

                                        hero_index = None
                                        for hero in heros:
                                            if (expected_type == "kick" and hero.index == 0) or \
                                               (expected_type == "snare" and hero.index == 1) or \
                                               (expected_type.startswith("hihat") and hero.index == 2):
                                                hero_index = hero.index
                                                break

                                        if hero_index is not None:
                                            if super_mode.active:
                                                heros.sprites()[hero_index].catch_note_success()
                                            else:
                                                heros.sprites()[hero_index].update_state(True)

                                        if note.type.startswith("hihat"):
                                            if heros:
                                                target_pos = heros.sprites()[0].rect.center if super_mode.active else enemy.rect.center
                                                effect = HitEffect(note.type, start_pos, target_pos, angle, super_mode_active=super_mode.active)
                                                all_sprites.add(effect)
                                                effects_group.add(effect)
                                                note.kill()
                                        else:
                                            effect = HitEffect(note.type, start_pos, enemy.rect.center, angle, super_mode_active=super_mode.active)
                                            all_sprites.add(effect)
                                            effects_group.add(effect)
                                            note.kill()
                                    break

        for note_data in Spnotes.notes:
            spawn_time = note_data["time"]
            note_type = note_data["type"]
            note_key = (spawn_time, note_type)
            if note_key not in spawned_notes and abs(scnd - spawn_time) < 0.03:
                spawn_note(note_type)
                spawned_notes.add(note_key)

        super_mode.update(dt)

        all_sprites.update(dt)
        effects_group.update(dt)

        if scnd < song_duration and enemy.state == "dead":
            save_stats()
            Datagame.current_level_index += 1
            Spnotes.notes = []
            return "level_complete"

        if scnd >= song_duration:
            save_stats()
            if enemy.state != "dead":
                show_game_over(screen)
                Spnotes.notes = []
                return "game_over"
            else:
                Datagame.current_level_index += 1
                Spnotes.notes = []
                return "level_complete"

        if Datagame.total_missed >= 30:
            save_stats()
            show_game_over(screen)
            return "game_over"

        if any(hero.failed_state for hero in heros):
            Datagame.balance = 0
        elif Datagame.balance == 0:
            Datagame.balance = 5

        screen.blit(background, (0, 0))
        for sprite in all_sprites:
            if not isinstance(sprite, Heros):
                screen.blit(sprite.image, sprite.rect)

        for hero in heros:
            hero.draw(screen)
        effects_group.draw(screen)

        enemy.draw_health_bar(screen)
        pg.draw.rect(screen, (255, 230, 55), hit_zone, 3)
        draw_money(screen, font)
        balance_text = font.render(f"Ритмичность: {Datagame.balance}", True, (0, 255, 0))
        screen.blit(balance_text, (11, HEIGHT - 277))
        missed_text = font.render(f"Пропущено: {Datagame.total_missed}", True, (255, 0, 0))
        screen.blit(missed_text, (11, HEIGHT - 122))
        super_mode.draw(screen, font)
        pg.display.flip()

save_stats()
game_state = "menu"
game_state = "menu"

while True:
    if game_state == "menu":
        result = main_menu()
        if result == "exit":
            break
        elif result == "level_transition":
            game_state = "level_transition"

    elif game_state == "level_transition":
        result = start_level_from_selection()
        if result is None:
            game_state = "menu"
        else:
            game_state = "menu"
