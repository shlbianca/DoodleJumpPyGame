import random
from lowPlatform import *
from settings import *
from platforms import *
from enemies import *
from Clouds import *

vec = pygame.math.Vector2
from os import path
from twilio.rest import Client
import time

# ==== CONFIGURARE TWILIO ====
account_sid = 'ACc9c9b0ed84b8cc25a69a3308e2ff8796'
auth_token = '6318040a3abbee9f887eaa48192478d7'
client = Client(account_sid, auth_token)


def send_highscore_via_whatsapp(score):
    message = client.messages.create(
        body=f"🏆 Noul highscore în Doodle Jump: {score} puncte! 🚀",
        from_='whatsapp:+14155238886',
        to='whatsapp:+40748111788'
    )
    print("Mesaj trimis:", message.sid)


# ==== Clasa Mushroom (Ciupercă) ====
class Mushroom(pygame.sprite.Sprite):
    def __init__(self, game, x, platform):
        pygame.sprite.Sprite.__init__(self)
        self.game = game
        self.platform = platform
        self.image = pygame.image.load('mushroom.png').convert_alpha()
        # Redimensionăm ciuperca proporțional cu rezoluția
        self.image = pygame.transform.scale(self.image, (int(self.game.pikachu_size[0] * self.game.scale_factor),
                                                         int(self.game.pikachu_size[1] * self.game.scale_factor)))
        self.rect = self.image.get_rect()
        self.rect.centerx = platform.rect.centerx
        self.rect.bottom = platform.rect.top
        self.game.powerups.add(self)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 5000

    def update(self):
        if self.platform:
            self.rect.centerx = self.platform.rect.centerx
            self.rect.bottom = self.platform.rect.top
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()
            print("Ciupercă expirată și eliminată!")


# ==== Clasa Game ====
class Game:
    def __init__(self, display_width, display_height):
        pygame.init()
        self.display_width = display_width
        self.display_height = display_height
        self.scale_factor = self.display_width / 800  # Definim scale_factor ca atribut
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        self.gameDisplay.fill(white)
        pygame.display.set_caption("Doodle Jump!")
        self.clock = pygame.time.Clock()
        self.img_pikachu = pygame.sprite.Sprite()
        self.img_pikachu.image = pygame.image.load('pikachu.png').convert_alpha()
        # Dimensiune de bază pentru Pikachu
        self.pikachu_size = (50, 50)  # Dimensiune de referință la 800x600
        self.pikachu_size = (
        int(self.pikachu_size[0] * self.scale_factor), int(self.pikachu_size[1] * self.scale_factor))
        self.img_pikachu.image = pygame.transform.scale(self.img_pikachu.image, self.pikachu_size)
        self.img_pikachu.rect = self.img_pikachu.image.get_rect()
        self.img_mario = pygame.image.load('mario.png').convert_alpha()
        self.img_mario = pygame.transform.scale(self.img_mario, self.pikachu_size)
        self.current_image = self.img_pikachu.image
        self.background = pygame.image.load('blue_back.jpg').convert()
        self.background = pygame.transform.scale(self.background, (self.display_width, self.display_height))
        self.font = pygame.font.SysFont(None, int(25 * self.scale_factor))
        self.gameExit = False
        self.pos = vec(self.display_width - self.pikachu_size[0], self.display_height)
        self.img_pikachu.rect.topleft = [self.pos.x, self.pos.y]
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.playerSprite = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()
        self.playerSprite.add(self.img_pikachu)
        # Platforme inițiale scalate proporțional
        p1 = lowPlatform(0, self.display_height - int(40 * self.scale_factor), self.display_width,
                         int(40 * self.scale_factor))
        platform_obj = Platform(self)
        self.platform_images = platform_obj.getImages()
        p2 = Platform(self)
        p2.getPlatform(self.display_width / 2 - int(50 * self.scale_factor),
                       self.display_height - int(150 * self.scale_factor), self.platform_images)
        p3 = Platform(self)
        p3.getPlatform(self.display_width / 2 - int(100 * self.scale_factor),
                       self.display_height - int(300 * self.scale_factor), self.platform_images)
        p4 = Platform(self)
        p4.getPlatform(self.display_width / 2, self.display_height - int(450 * self.scale_factor), self.platform_images)
        p5 = Platform(self)
        p5.getPlatform(0, self.display_height - int(600 * self.scale_factor), self.platform_images)
        self.platforms.add(p1, p2, p3, p4, p5)
        self.score = 0
        self.font_name = pygame.font.match_font(Font_Name)
        self.load_data()
        self.enemies_timer = 0
        self.mushroom_timer = 0
        self.is_mario = False
        for i in range(8):
            c = Cloud(self)
            c.rect.y += int(600 * self.scale_factor)

    def load_data(self):
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, hs_file), 'r+') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        cloud_dir = path.join(self.dir, 'clouds_img')
        self.cloud_images = []
        for i in range(1, 4):
            img = pygame.image.load(path.join(cloud_dir, 'cloud{}.png'.format(i))).convert()
            img = pygame.transform.scale(img, (
            int(img.get_width() * self.scale_factor), int(img.get_height() * self.scale_factor)))
            self.cloud_images.append(img)
        self.sound_dir = path.join(self.dir, 'sound')
        self.jump_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'jump.ogg'))
        self.jump_sound.set_volume(0.1)
        self.pow_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'pow.wav'))
        self.mushroom_sound = pygame.mixer.Sound(path.join(self.sound_dir, 'mushroom_collect.wav'))
        self.mushroom_sound.set_volume(0.5)

    def updateScreen(self):
        now_time = pygame.time.get_ticks()
        if now_time - self.enemies_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.enemies_timer = now_time
            Enemies(self)

        if random.randrange(1000) < 5 and len(self.powerups) < 3:
            platform = random.choice([p for p in self.platforms if p.rect.top < self.display_height])
            Mushroom(self, platform.rect.centerx, platform)
            print("Ciupercă generată!")

        enemies_hits = pygame.sprite.spritecollide(self.img_pikachu, self.enemies, False, pygame.sprite.collide_mask)
        if enemies_hits:
            self.gameOver = True

        powerup_hits = pygame.sprite.spritecollide(self.img_pikachu, self.powerups, True)
        for powerup in powerup_hits:
            if isinstance(powerup, Mushroom):
                self.mushroom_sound.play()
                self.is_mario = True
                self.mushroom_timer = now_time
                self.current_image = self.img_mario
                self.img_pikachu.image = self.current_image
                print("Ciupercă colectată și eliminată!")
            else:
                self.pow_sound.play()
                self.vel.y = power_up_boost

        if self.is_mario and now_time - self.mushroom_timer > 10000:
            self.is_mario = False
            self.current_image = pygame.image.load('pikachu.png').convert_alpha()
            self.current_image = pygame.transform.scale(self.current_image, (
            int(self.pikachu_size[0] * self.scale_factor), int(self.pikachu_size[1] * self.scale_factor)))
            self.img_pikachu.image = self.current_image
            print("Revenit la Pikachu!")

        self.img_pikachu.rect.midbottom = [self.pos.x, self.pos.y]
        if self.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.img_pikachu, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.pos.x < lowest.rect.right + int(30 * self.scale_factor) and self.pos.x > lowest.rect.left - int(
                        30 * self.scale_factor):
                    if self.pos.y < lowest.rect.centery:
                        self.pos.y = lowest.rect.top
                        self.vel.y = 0

        if self.img_pikachu.rect.top <= self.display_height / 4:
            if random.randrange(100) < 99:
                Cloud(self)
            self.pos.y += abs(self.vel.y)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.vel.y / 2), 2)
            for platform in self.platforms:
                platform.rect.y += abs(self.vel.y)
                if platform.rect.top >= self.display_height:
                    platform.kill()
                    self.score += 10
            for enemy in self.enemies:
                enemy.rect.y += abs(self.vel.y)

        if self.img_pikachu.rect.bottom > self.display_height:
            self.gameOver = True
            for sprite in self.platforms:
                sprite.rect.y -= max(self.vel.y, 10)

        while len(self.platforms) < 6:
            width = random.randrange(int(50 * self.scale_factor), int(100 * self.scale_factor))
            p = Platform(self)
            p.getPlatform(random.randrange(0, self.display_width - width),
                          random.randrange(-int(50 * self.scale_factor), -int(30 * self.scale_factor)),
                          self.platform_images)
            self.platforms.add(p)

        self.gameDisplay.fill(black)
        self.enemies.update()
        self.powerups.update()
        self.platforms.update()
        self.clouds.update()
        self.playerSprite.update()
        self.gameDisplay.blit(self.background, (0, 0))
        self.clouds.draw(self.gameDisplay)
        self.platforms.draw(self.gameDisplay)
        self.powerups.draw(self.gameDisplay)
        self.enemies.draw(self.gameDisplay)
        self.playerSprite.draw(self.gameDisplay)
        self.messageToScreen("SCORE: " + str(self.score), int(25 * self.scale_factor), white, self.display_width / 2,
                             15)
        pygame.display.update()

    def run(self):
        self.score = 0
        self.gameOver = False
        while not self.gameExit:
            self.checkEvent()
            self.acc.x += self.vel.x * player_Fric
            self.vel += self.acc
            self.pos += self.vel + 0.5 * self.acc
            self.checkHorizontalCrossing()
            self.updateScreen()
            self.clock.tick(fps)
            if self.gameOver:
                self.gameOverScreen()
        pygame.quit()
        quit()

    def checkHorizontalCrossing(self):
        if self.pos.x > self.display_width:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = self.display_width
        if self.pos.y == self.display_height:
            self.gameOver = True
        if self.pos.y == -50:
            self.pos.y = self.display_height

    def checkEvent(self):
        self.acc = vec(0, gravity)
        self.jump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameExit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.acc.x = -player_Acc
                if event.key == pygame.K_RIGHT:
                    self.acc.x = player_Acc
                if event.key == pygame.K_SPACE:
                    self.jump()

    def messageToScreen(self, msg, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(msg, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.gameDisplay.blit(text_surface, text_rect)

    def jump(self):
        if self.vel.y > 0:
            self.img_pikachu.rect.y += 1
            hits = pygame.sprite.spritecollide(self.img_pikachu, self.platforms, False)
            self.img_pikachu.rect.y -= 1
            if hits:
                self.jump_sound.play()
                self.vel.y = -10

    def startScreen(self):
        resolutions = [(800, 600), (1024, 768), (1280, 720)]
        selected_index = 0
        selecting = True
        scale_factor = 1  # Pentru meniul temporar

        while selecting:
            self.gameDisplay.fill(orange)
            self.messageToScreen("DOODLE JUMP", int(40 * scale_factor), white, self.display_width / 2,
                                 self.display_height / 3)
            self.messageToScreen("Selecteaza rezolutia:", int(25 * scale_factor), white, self.display_width / 2,
                                 self.display_height / 2 - 50)

            for i, (width, height) in enumerate(resolutions):
                color = yellow if i == selected_index else white
                self.messageToScreen(f"{width}x{height}", int(25 * scale_factor), color, self.display_width / 2,
                                     self.display_height / 2 + i * 40)

            self.messageToScreen("Apasa SUS/JOS pentru a selecta, ENTER pentru a confirma", int(20 * scale_factor),
                                 white, self.display_width / 2, self.display_height - 100)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(resolutions)
                    if event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(resolutions)
                    if event.key == pygame.K_RETURN:
                        display_width, display_height = resolutions[selected_index]
                        self.__init__(display_width, display_height)
                        selecting = False
                        self.run()

    def gameOverScreen(self):
        self.gameDisplay.fill(orange)
        self.messageToScreen("OOPS!...SFÂRȘITUL JOCULUI", int(40 * self.scale_factor), white, self.display_width / 2,
                             int(180 * self.scale_factor))
        self.messageToScreen("Score: " + str(self.score), int(40 * self.scale_factor), white, self.display_width / 2,
                             self.display_height / 2 - int(100 * self.scale_factor))
        self.messageToScreen("Apasă orice tastă pentru a incepe din nou...", int(30 * self.scale_factor), white,
                             self.display_width / 2 + int(50 * self.scale_factor),
                             self.display_height / 2 + int(50 * self.scale_factor))
        if self.score > self.highscore:
            self.highscore = self.score
            self.messageToScreen("FELICITARI!!! HIGH SCORE NOU!", int(30 * self.scale_factor), white,
                                 self.display_width / 2, self.display_height / 2 - int(30 * self.scale_factor))
            with open(path.join(self.dir, hs_file), 'w') as f:
                f.write(str(self.score))
            send_highscore_via_whatsapp(self.highscore)
        else:
            self.messageToScreen("High Score: " + str(self.highscore), int(30 * self.scale_factor), white,
                                 self.display_width / 2, self.display_height / 2 - int(30 * self.scale_factor))
        pygame.display.update()
        self.waitForKeyPress()
        self.startScreen()

    def waitForKeyPress(self):
        waiting = True
        while waiting:
            self.clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.gameExit = True
                if event.type == pygame.KEYUP:
                    waiting = False
                    self.gameOver = False
                    self.gameExit = False


# Inițializare temporară pentru meniul principal
pygame.init()
temp_display = pygame.display.set_mode((1024, 768))
g = Game(1024, 768)
g.startScreen() 