import pygame as pg
import math
from Enemy import Enemy
from Heros import Heros
import Datagame

normal_effect_paths = {
    "kick": "img/imgUnconstant/effects/normal_kick.png",
    "snare": "img/imgUnconstant/effects/normal_snare.png",
    "hihat_open": "img/imgUnconstant/effects/normal_hihat.png",
}

special_effect_paths = {
    "kick": "img/imgUnconstant/effects/hit_kick.png",
    "snare": "img/imgUnconstant/effects/hit_snare.png",
    "hihat_open": "img/imgUnconstant/effects/hit_hihat.png",
}

class HitEffect(pg.sprite.Sprite):
    COLLISION_RADIUS = 40

    def __init__(self, img_type, start_pos, target_pos, angle, super_mode_active=False):
        super().__init__()
        self.special_mode_active = super_mode_active
        paths = special_effect_paths if super_mode_active else normal_effect_paths

        self.original_image = pg.image.load(paths[img_type]).convert_alpha()
        self.image = pg.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pg.Vector2(start_pos)
        self.target = pg.Vector2(target_pos)
        self.velocity = (self.target - self.pos).normalize() * 600
        self.type = img_type

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        if self.type in ["kick", "snare"] or (self.type.startswith("hihat") and not self.special_mode_active):
            for sprite in self.groups():
                for other in sprite:
                    if isinstance(other, Enemy):
                        distance = self.pos.distance_to(other.rect.center)
                        if distance <= self.COLLISION_RADIUS:
                            damage = 20 if self.special_mode_active else 10
                            other.take_damage(damage)
                            self.kill()
                            return

        elif self.type.startswith("hihat") and self.special_mode_active:
            for sprite in self.groups():
                for other in sprite:
                    if isinstance(other, Heros):
                        distance = self.pos.distance_to(other.rect.center)
                        if distance <= self.COLLISION_RADIUS:
                            print(f"🔥 Хил героя {other.index}")
                            for hero in sprite:
                                if isinstance(hero, Heros):
                                    hero.start_heal_animation()

                            Datagame.total_missed = max(0, Datagame.total_missed - 3)
                            self.kill()
                            return
