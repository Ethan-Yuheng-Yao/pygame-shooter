import pygame
import math
import random
from sys import exit

pygame.init()

health = 5
score = 0
wave = 0
enemies_to_spawn = 0
enemies_spawned = 0
time_since_last_spawn = 0
spawn_timer = 0
x = 0
running = True

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.Surface((60, 15), pygame.SRCALPHA)
        self.original_image.fill((255, 255, 255))
        pygame.draw.circle(self.original_image, (255, 0, 0), (60, 7), 5)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(50, 325))

    def update(self, mouse_pos):
        rel_x, rel_y = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        angle = math.degrees(math.atan2(-rel_y, rel_x))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((15, 15))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=pos)

    def update(self, bullets_group):
        global score, health, running
        self.rect.x -= 1
        bullet_hits = pygame.sprite.spritecollide(self, bullets_group, True)
        if bullet_hits:
            self.kill()
            score += 1
        if self.rect.colliderect(end_point_rect):
            self.kill()  # Ensure the enemy is removed
            health -= 1
            if health <= 0:
                running = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 255), (5, 5), 5)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(5, 0).rotate(angle)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

screen = pygame.display.set_mode((650, 650))
pygame.display.set_caption("Shooter")

end_point = pygame.Surface((50, 650))
end_point.fill((75, 75, 255))
end_point_rect = end_point.get_rect(topleft=(0, 0))

heart = pygame.image.load("graphics/health.png").convert_alpha()
heart = pygame.transform.scale(heart, (45, 45))

player = Player()
player_group = pygame.sprite.GroupSingle(player)

bullets_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()

font = pygame.font.SysFont(None, 36)  
font_ = pygame.font.SysFont(None, 60)
font__ = pygame.font.SysFont(None, 100)

end_text = font_.render('Game Over!', True, 'Red')
end_text_rect = end_text.get_rect(center=(325, 100))

spawn_interval = 1000  
enemy_spawn_interval = 100  

clock = pygame.time.Clock()

def start_new_wave():
    global wave, enemies_to_spawn, enemies_spawned, time_since_last_spawn
    wave += 1
    enemies_to_spawn = random.randint(wave * 2, wave * 4)
    enemies_spawned = 0
    time_since_last_spawn = 0

start_new_wave()

while True:
    if health <= 0:
        running = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
        if running:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    rel_x, rel_y = mouse_pos[0] - player.rect.centerx, mouse_pos[1] - player.rect.centery
                    angle = math.degrees(math.atan2(-rel_y, -rel_x))
                    angle += 180
                    bullet = Bullet(player.rect.center, angle)
                    bullets_group.add(bullet)
        else:
            screen.fill((255, 255, 255))
            screen.blit(end_text, end_text_rect)
            score_text_end = font__.render(f'Final Score: {score}', True, (255, 0, 0))
            score_text_end_rect = score_text_end.get_rect(center=(325, 300))
            screen.blit(score_text_end, score_text_end_rect)
            pygame.display.update()
            continue

    if running:
        x = 200

        wave_text = font.render(f'Wave: {wave}', True, (255, 255, 255))
        wave_text_rect = wave_text.get_rect(center=(100, 30))

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        score_text_rect = score_text.get_rect(center=(500, 30))

        mouse_pos = pygame.mouse.get_pos()
        player.update(mouse_pos)

        bullets_group.update()

        screen.fill((0, 0, 0))
        screen.blit(end_point, end_point_rect)
        screen.blit(wave_text, wave_text_rect)
        screen.blit(score_text, score_text_rect)

        for _ in range(health):
            screen.blit(heart, (x, 15))
            x += 45
        player_group.draw(screen)

        enemies_group.update(bullets_group)
        enemies_group.draw(screen)

        bullets_group.draw(screen)

        pygame.display.update()

        if enemies_spawned < enemies_to_spawn:
            time_since_last_spawn += clock.get_time()
            if time_since_last_spawn >= enemy_spawn_interval:
                enemy_start_pos = (800, random.randint(15, 635))
                enemy = Enemy(enemy_start_pos)
                enemies_group.add(enemy)
                time_since_last_spawn = 0
                enemies_spawned += 1

        if len(enemies_group) == 0 and enemies_spawned >= enemies_to_spawn:
            spawn_timer += clock.get_time()
            if spawn_timer >= spawn_interval:
                start_new_wave()
                spawn_timer = 0

    clock.tick(60)
