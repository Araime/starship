import random
import sys
from os import path

import pygame

WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def newmob(mobs):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)


def draw_shield_bar(surface, x, y, pct):
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 10
    fill = (pct / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, GREEN, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


def draw_lives(surface, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surface.blit(img, img_rect)


def pause():
    paused = True

    while paused:

        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False

        draw_text(screen, 'PAUSED', 32, WIDTH / 2, HEIGHT / 2)
        pygame.display.flip()


def show_go_screen():
    screen.blit(bg_img, bg_rect)
    draw_text(screen, 'STARSHIP', 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, 'Arrow keys move, Space to fire', 22, WIDTH / 2, HEIGHT / 2)
    draw_text(screen, 'Press any key to begin', 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True

    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                waiting = False


class Player(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(ship_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()

    def update(self):
        # timeout for powerup
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        # unhide if hidden
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        self.speed_x = 0
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.speed_x -= 5
        if key[pygame.K_RIGHT]:
            self.speed_x += 5
        if key[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speed_x
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_snd.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_snd.play()

    def hide(self):
        # hide the player
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_img)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        # pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speed_y = random.randrange(2, 8)
        self.speed_x = random.randrange(-3, 3)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT + 10 or self.rect.left < -100 or self.rect.right > WIDTH + 100:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 8)
            self.speed_x = random.randrange(-3, 3)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = laser_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed_y = -10

    def update(self):
        self.rect.y += self.speed_y
        # kill it if moves off
        if self.rect.bottom < 0:
            self.kill()


class Pow(pygame.sprite.Sprite):

    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'bolt'])
        self.image = powerup_img[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed_y = 3

    def update(self):
        self.rect.y += self.speed_y
        # kill it if moves off
        if self.rect.top > HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


if __name__ == '__main__':
    img_dir = path.join(path.dirname(__file__), 'img')
    snd_dir = path.join(path.dirname(__file__), 'sound')

    # initialize pygame and create window
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Starship')
    clock = pygame.time.Clock()
    font_name = pygame.font.match_font('arial')

    # load all graphics
    bg_img = pygame.image.load(path.join(img_dir, 'bg.png')).convert()
    bg_rect = bg_img.get_rect()

    ship_img = pygame.image.load(path.join(img_dir, 'ship.png')).convert()
    ship_mini_img = pygame.transform.scale(ship_img, (25, 19))
    ship_mini_img.set_colorkey(BLACK)

    laser_img = pygame.image.load(path.join(img_dir, 'laser.png')).convert()

    meteor_img = [
        pygame.image.load(path.join(img_dir, 'meteor.png')).convert(),
        pygame.image.load(path.join(img_dir, 'meteor2.png')).convert(),
        pygame.image.load(path.join(img_dir, 'meteor3.png')).convert(),
        pygame.image.load(path.join(img_dir, 'meteor4.png')).convert(),
        pygame.image.load(path.join(img_dir, 'meteor5.png')).convert(),
        pygame.image.load(path.join(img_dir, 'meteor6.png')).convert()
    ]

    explosion_anim = {}
    explosion_anim['lg'] = []
    explosion_anim['sm'] = []
    explosion_anim['player'] = []
    for i in range(9):
        filename = f'regularExplosion0{i}.png'
        img = pygame.image.load(path.join(img_dir, filename)).convert()
        img.set_colorkey(BLACK)
        img_lg = pygame.transform.scale(img, (75, 75))
        explosion_anim['lg'].append(img_lg)
        img_sm = pygame.transform.scale(img, (32, 32))
        explosion_anim['sm'].append(img_sm)
        filename = f'sonicExplosion0{i}.png'
        img = pygame.image.load(path.join(img_dir, filename)).convert()
        img.set_colorkey(BLACK)
        explosion_anim['player'].append(img)

    powerup_img = {}
    powerup_img['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
    powerup_img['bolt'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()

    # load all sounds
    pygame.mixer.music.load(path.join(snd_dir, 'music.ogg'))
    pygame.mixer.music.set_volume(0.7)

    shoot_snd = pygame.mixer.Sound(path.join(snd_dir, 'pew.wav'))
    shield_snd = pygame.mixer.Sound(path.join(snd_dir, 'pow4.wav'))
    bolt_snd = pygame.mixer.Sound(path.join(snd_dir, 'pow5.wav'))
    death_snd = pygame.mixer.Sound(path.join(snd_dir, 'rumble.ogg'))

    explosion_snd = [
        pygame.mixer.Sound(path.join(snd_dir, 'expl3.wav')),
        pygame.mixer.Sound(path.join(snd_dir, 'expl6.wav'))
    ]

    # create all sprite groups


    pygame.mixer.music.play(-1)

    running = True
    game_over = True

    # Game loop
    while running:
        if game_over:
            show_go_screen()
            game_over = False

            all_sprites = pygame.sprite.Group()
            mobs = pygame.sprite.Group()
            bullets = pygame.sprite.Group()
            powerups = pygame.sprite.Group()
            player = Player()
            all_sprites.add(player)

            for i in range(12):
                newmob(mobs)

            score = 0
        # keep loop running at the right speed
        clock.tick(FPS)

        # Process input (events)
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause()

        # Update
        all_sprites.update()

        # check mob hit
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        for hit in hits:
            score += 50 - hit.radius
            random.choice(explosion_snd).play()
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.93:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            newmob(mobs)

        # check player hit
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.shield -= hit.radius
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            newmob(mobs)
            if player.shield <= 0:
                death_snd.play()
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                player.hide()
                player.lives -= 1
                player.shield = 100

        # check powerup collection
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                player.shield += random.randrange(20, 50)
                shield_snd.play()
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'bolt':
                player.powerup()
                bolt_snd.play()

        # if player died and explosion has finished
        if player.lives == 0 and not death_explosion.alive():
            game_over = True

        # Draw / render
        screen.fill(BLACK)
        screen.blit(bg_img, bg_rect)
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)
        draw_shield_bar(screen, 5, 5, player.shield)
        draw_lives(screen, WIDTH - 100, 5, player.lives, ship_mini_img)

        # *after* drawing everything, flip the display
        pygame.display.flip()

    pygame.quit()
