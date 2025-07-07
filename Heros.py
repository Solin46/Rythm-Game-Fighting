import pygame as pg
import Datagame
import os
from Setting import *

HEAL_FOLDER = os.path.join("img", "heal")

class Heros(pg.sprite.Sprite):
    def __init__(self, images, index):
        super().__init__()
        self.images = images
        self.index = index
        self.image = self.images[0]
        self.current_base_image = self.images[0]
        self.rect = self.image.get_rect()

        self.rect.x = 177 + index * 64
        self.rect.y = 388 + (index * 0.7) * 100

        self.missed_notes = 0
        self.success_notes = 0
        self.success_timer = 0
        self.success_duration = 0.2
        self.failed_state = False

        self.is_healing = False
        self.heal_images = []
        self.heal_index = 0
        self.heal_timer = 0
        self.heal_duration = 1.0
        self.heal_frame_time = 0.25
        self.heal_frame_timer = 0

        for i in range(1, 3):
            path = os.path.join(HEAL_FOLDER, f"heal{i}.png")
            if os.path.exists(path):
                img = pg.image.load(path).convert_alpha()
                self.heal_images.append(pg.transform.scale(img, self.rect.size))

    def update(self, dt):
        if self.success_timer > 0:
            self.success_timer -= dt
            self.current_base_image = self.images[1]
        elif self.failed_state:
            self.current_base_image = self.images[2]
        else:
            self.current_base_image = self.images[0]

        if self.is_healing and self.heal_images:
            self.heal_timer += dt
            self.heal_frame_timer += dt
            if self.heal_frame_timer >= self.heal_frame_time:
                self.heal_index = (self.heal_index + 1) % len(self.heal_images)
                self.heal_frame_timer = 0
            if self.heal_timer >= self.heal_duration:
                self.is_healing = False
                self.heal_timer = 0

    def draw(self, surface):
        surface.blit(self.current_base_image, self.rect)
        if self.is_healing and self.heal_images:
            heal_image = self.heal_images[self.heal_index]
            surface.blit(heal_image, self.rect)

    def catch_note_success(self):
        self.success_timer = self.success_duration
        self.missed_notes = 0
        self.success_notes += 1

        if self.success_notes >= 5:
            self.failed_state = False
            self.success_notes = 0

        if not self.failed_state:
            Datagame.balance += 5
            Datagame.money += Datagame.balance

    def miss_note(self):
        if not self.failed_state:
            self.missed_notes += 1
            self.success_notes = 0

            if self.missed_notes >= 5:
                self.failed_state = True
                Datagame.balance = 0
                self.missed_notes = 0

    def update_state(self, success: bool):
        if success:
            self.catch_note_success()
        else:
            self.miss_note()

    def start_heal_animation(self):
        if self.heal_images:
            self.is_healing = True
            self.heal_timer = 0
            self.heal_index = 0
            self.heal_frame_timer = 0
