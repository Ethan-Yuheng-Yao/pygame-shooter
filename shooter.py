import pygame
import math
import random
from sys import exit

pygame.init()

boss_spawned = False

screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("Shooter")

health = 7
score = 0
wave = 0
enemies_to_spawn = 0
enemies_spawned = 0
time_since_last_spawn = 0
spawn_timer = 0
running = True

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.Surface((int(screen_width * 0.05), int(screen_height * 0.025)), pygame.SRCALPHA)
        self.original_image.fill((255, 255, 255))
        pygame.draw.circle(self.original_image, (255, 0, 0), (int(screen_width * 0.05), int(screen_height * 0.015)), int(screen_width * 0.008))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(int(screen_width * 0.08), int(screen_height * 0.5)))

    def update(self, mouse_pos):
        rel_x, rel_y = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        angle = math.degrees(math.atan2(-rel_y, rel_x))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        self.image = pygame.Surface((int(screen_width * 0.02), int(screen_width * 0.02)))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)

    def update(self, bullets_group):
        global score, health, running
        self.rect.x -= int(screen_width * 0.001)
        bullet_hits = pygame.sprite.spritecollide(self, bullets_group, True)
        if bullet_hits:
            self.kill()
            score += 1
        if self.rect.colliderect(end_point_rect):
            self.kill() 
            health -= 1
            if health <= 0:
                running = False

class Boss(pygame.sprite.Sprite):
    def __init__(self, pos, life):
        super().__init__()
        self.image = pygame.Surface((int(screen_width * 0.05), int(screen_width * 0.05)))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect(center=pos)
        self.health = life

    def update(self, bullets_group):
        global score, boss_spawned, health, running
        self.rect.x -= int(screen_width * 0.001)
        bullet_hits = pygame.sprite.spritecollide(self, bullets_group, True)
        if bullet_hits:
            self.health -= 1
        if self.health <= 0:
            self.kill()
            boss_spawned = False
            score += self.health
            start_new_wave()
        if self.rect.colliderect(end_point_rect):
            self.kill()
            health -= 3
            if health <= 0:
                running = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.image = pygame.Surface((int(screen_width * 0.015), int(screen_width * 0.015)), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 255), (int(screen_width * 0.006), int(screen_width * 0.006)), int(screen_width * 0.006))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(int(screen_width * 0.01), 0).rotate(angle)

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos

close_button = pygame.Surface((int(screen_width * 0.04), int(screen_width * 0.04)))
close_button.fill((255, 0, 0))
pygame.draw.line(close_button, (255, 255, 255), (0, 0), (int(screen_width * 0.04), int(screen_width * 0.04)), 5)
pygame.draw.line(close_button, (255, 255, 255), (0, int(screen_width * 0.04)), (int(screen_width * 0.04), 0), 5)
close_button_rect = close_button.get_rect(topright=(screen_width - int(screen_width * 0.01), int(screen_width * 0.01)))

end_point = pygame.Surface((int(100), screen_height))
end_point.fill((75, 75, 255))
end_point_rect = end_point.get_rect(topleft=(0, 0))

heart = pygame.image.load("graphics/health.png").convert_alpha()
heart = pygame.transform.scale(heart, (int(screen_width * 0.04), int(screen_width * 0.04)))

player = Player()
player_group = pygame.sprite.GroupSingle(player)
bosses_group = pygame.sprite.Group()
bullets_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()

font = pygame.font.SysFont(None, int(screen_width * 0.03))  
font_ = pygame.font.SysFont(None, int(screen_width * 0.06))
font__ = pygame.font.SysFont(None, int(screen_width * 0.1))

end_text = font_.render('Game Over!', True, 'Red')
end_text_rect = end_text.get_rect(center=(screen_width // 2, screen_height // 4))

spawn_interval = 1000  
enemy_spawn_interval = 100  

clock = pygame.time.Clock()

def start_new_wave():
    global wave, enemies_to_spawn, enemies_spawned, time_since_last_spawn
    wave += 1
    enemies_to_spawn = random.randint(wave * 3, wave * 5)
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
                    if close_button_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        exit()
                    rel_x, rel_y = mouse_pos[0] - player.rect.centerx, mouse_pos[1] - player.rect.centery
                    angle = math.degrees(math.atan2(-rel_y, -rel_x))
                    angle += 180
                    bullet = Bullet(player.rect.center, angle)
                    bullets_group.add(bullet)
        else:
            screen.fill((255, 255, 255))
            screen.blit(end_text, end_text_rect)
            score_text_end = font__.render(f'Final Score: {score}', True, (255, 0, 0))
            score_text_end_rect = score_text_end.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(score_text_end, score_text_end_rect)
            pygame.display.update()
            continue

    if running:
        x = 110

        wave_text = font.render(f'Wave: {wave}', True, (255, 255, 255))
        wave_text_rect = wave_text.get_rect(center=(screen_width // 2, 30))

        score_text = font.render(f'Score: {score}', True, (255, 255, 255))
        score_text_rect = score_text.get_rect(center=(screen_width - 150, 30))

        mouse_pos = pygame.mouse.get_pos()
        player.update(mouse_pos)

        bullets_group.update()

        screen.fill((0, 0, 0))
        screen.blit(end_point, end_point_rect)
        screen.blit(wave_text, wave_text_rect)
        screen.blit(score_text, score_text_rect)
        screen.blit(close_button, close_button_rect)

        for _ in range(health):
            screen.blit(heart, (x, 15))
            x += 60
        player_group.draw(screen)

        bosses_group.update(bullets_group)
        bosses_group.draw(screen)

        enemies_group.update(bullets_group)
        enemies_group.draw(screen)

        bullets_group.draw(screen)

        pygame.display.update()

        if wave % 5 == 0 and wave != 0:
            if not boss_spawned:
                boss_start_pos = (screen_width, random.randint(15, screen_height - 15))
                boss = Boss(boss_start_pos, wave*2 + 20)
                bosses_group.add(boss)
                boss_spawned = True
            
        elif enemies_spawned < enemies_to_spawn:
            time_since_last_spawn += clock.get_time()
            if time_since_last_spawn >= enemy_spawn_interval:
                enemy_start_pos = (screen_width, random.randint(15, screen_height - 15))
                enemy = Enemy(enemy_start_pos, 'Red')
                enemies_group.add(enemy)
                time_since_last_spawn = 0
                enemies_spawned += 1

        if len(enemies_group) == 0 and enemies_spawned >= enemies_to_spawn:
            spawn_timer += clock.get_time()
            if spawn_timer >= spawn_interval:
                start_new_wave()
                spawn_timer = 0

    clock.tick(60)


