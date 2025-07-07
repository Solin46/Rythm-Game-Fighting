import pygame as pg
from Setting import WIDTH, HEIGHT

class Enemy(pg.sprite.Sprite):
    def __init__(self, images, health=100, max_health=100):
        super().__init__()
        self.images = images
        self.health = health
        self.max_health = max_health
        self.state = "normal"
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - 400
        self.rect.y = 352
        self.hit_timer = 0
        self.is_hit = False

    def update(self, dt):
        if self.state == "dead":
            self.image = self.images[3]
        else:
            if self.is_hit:
                self.hit_timer += dt
                self.image = self.images[1]
                if self.hit_timer >= 0.2:
                    self.is_hit = False
                    self.hit_timer = 0
            elif self.health <= self.max_health / 2:
                self.image = self.images[2]
            else:
                self.image = self.images[0]

    def take_damage(self, amount):
        if self.health > 0:
            self.health -= amount
            if self.health <= 0:
                self.state = "dead"
                return True
            self.is_hit = True
            self.hit_timer = 0
            return False

    def draw_health_bar(self, surface):
        bar_width = 100
        bar_height = 10

        fill_width = (self.health / self.max_health) * bar_width
        outline_rect = pg.Rect(self.rect.x, self.rect.bottom + 10, bar_width, bar_height)
        fill_rect = pg.Rect(self.rect.x, self.rect.bottom + 10, fill_width, bar_height)
        pg.draw.rect(surface, (0, 255, 0), fill_rect)

        if fill_width < bar_width:
            missing_rect = pg.Rect(self.rect.x + fill_width, self.rect.bottom + 10, bar_width - fill_width, bar_height)
            pg.draw.rect(surface, (255, 0, 0), missing_rect)
        pg.draw.rect(surface, (255, 255, 255), outline_rect, 2)

        font = pg.font.SysFont(None, 20)
        health_text = font.render(str(self.health), True, (0, 255, 0))
        text_rect = health_text.get_rect(midtop=(
            self.rect.x + bar_width - 10,
            self.rect.bottom - 10
        ))
        surface.blit(health_text, text_rect)
