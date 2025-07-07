import pygame as pg
import Datagame
from Setting import *
class Notes(pg.sprite.Sprite):
    heros_group = None
    balanc = 0
    note_type_to_hero_index = {
        "kick": 0,
        "snare": 1,
        "hihat_open": 2,
    }

    def __init__(self, x, image, hitzone_rect, num, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.type = self.get_type(num)
        self.hitzone = hitzone_rect
        self.missed = False
        self.speed = speed

    def update(self, dt):
        self.rect.y -= self.speed
        if self.rect.top < 0:
            self.kill()

        if not self.missed and self.rect.top >= self.hitzone.bottom - 15:
            self.missed = True
            self.kill()

            hero_index = Notes.note_type_to_hero_index[self.type]
            if Notes.heros_group is not None:
                hero = Notes.heros_group[hero_index]

                if self.type == "hihat_closed":
                    hero.catch_note_success()
                else:
                    Datagame.total_missed += 1
                    hero.miss_note()

    def is_in_hitzone(self):
        return self.rect.colliderect(self.hitzone)

    def get_type(self, num):
        if num == 0:
            return "kick"
        elif num == 1:
            return "snare"
        elif num == 2:
            return "hihat_open"

    def catch(self, enemy):
        self.kill()
        global enemyisdead
        enemyisdead = enemy.take_damage(10)

        if Notes.heros_group is not None:
            hero_index = Notes.note_type_to_hero_index[self.type]
            hero = Notes.heros_group[hero_index]
            hero.update_state(success=True)

    @classmethod
    def set_heros_group(cls, heros):
        cls.heros_group = heros
