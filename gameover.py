
import pygame as pg
from Setting import *

def show_game_over(screen):
    pg.mixer.music.stop()
    screen.blit(menu[2],(0,0))

    sub_font = pg.font.Font(None, 40)
    sub_text = sub_font.render("Нажми любую кнопку для выхода в меню", True, (255, 255, 255))
    sub_rect = sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    screen.blit(sub_text, sub_rect)

    pg.display.flip()


    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                waiting = False