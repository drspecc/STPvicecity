import math
import random
import sys

import pygame


WIDTH, HEIGHT = 1280, 720
FPS = 60
CELL = 620
ROAD = 112
TAU = math.tau

PASTELS = [(235, 139, 143), (247, 181, 133), (224, 166, 191),
           (139, 190, 189), (234, 205, 143), (169, 164, 208)]
NEON_PINK = (255, 72, 166)
NEON_CYAN = (78, 230, 238)
INK = (27, 29, 52)


def seeded(ix, iy, salt=0):
    return random.Random((ix * 92837111 + iy * 689287499 + salt * 283923481) & 0xffffffff)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def mix(a, b, t):
    return tuple(round(a[i] * (1 - t) + b[i] * t) for i in range(3))


def world_to_screen(x, y, camera):
    return int(x - camera[0]), int(y - camera[1])


def draw_palm(surface, x, y, scale=1, shade=(37, 89, 92)):
    x, y = int(x), int(y)
    rect = tuple(int(v) for v in (x - 13*scale, y + 8*scale, 28*scale, 10*scale))
    pygame.draw.ellipse(surface, (30, 42, 60), rect)
    pygame.draw.line(surface, (117, 92, 73), (x, y), (int(x + 2*scale), int(y - 49*scale)), max(2, int(5*scale)))
    crown = (int(x + 2*scale), int(y - 47*scale))
    for ang in (-165, -130, -95, -55, -20, 15):
        rad = math.radians(ang)
        end = (int(crown[0] + math.cos(rad)*30*scale), int(crown[1] + math.sin(rad)*20*scale))
        pygame.draw.line(surface, shade, crown, end, max(2, int(4*scale)))
        for t in (0.35, 0.58, 0.77):
            px = int(crown[0] + (end[0]-crown[0])*t)
            py = int(crown[1] + (end[1]-crown[1])*t)
            pygame.draw.line(surface, shade, (px, py), (int(px + math.sin(rad)*7*scale), int(py + math.cos(rad)*8*scale)), max(1, int(2*scale)))


class City:
    def __init__(self):
        self.cache = {}

    def block_data(self, ix, iy):
        key = (ix, iy)
        if key not in self.cache:
            rng = seeded(ix, iy)
            kind = rng.choices(("buildings", "park", "plaza", "beach"), (57, 22, 14, 7))[0]
            buildings = []
            count = rng.randint(1, 4) if kind == "buildings" else rng.randint(0, 2)
            for _ in range(count):
                w, h = rng.randint(108, 235), rng.randint(92, 230)
                bx = rng.randint(18, max(19, CELL-ROAD-w-24))
                by = rng.randint(18, max(19, CELL-ROAD-h-24))
                buildings.append((bx, by, w, h, rng.choice(PASTELS), rng.randint(0, 3)))
            self.cache[key] = (kind, buildings, rng.randint(0, 999999))
        return self.cache[key]

    def draw(self, surface, camera):
        surface.fill((236, 184, 160))
        minx = math.floor(camera[0] / CELL) - 1
        maxx = math.floor((camera[0] + WIDTH) / CELL) + 1
        miny = math.floor(camera[1] / CELL) - 1
        maxy = math.floor((camera[1] + HEIGHT) / CELL) + 1
        self.cache = {key: value for key, value in self.cache.items()
                      if minx-2 <= key[0] <= maxx+2 and miny-2 <= key[1] <= maxy+2}
        for iy in range(miny, maxy+1):
            for ix in range(minx, maxx+1):
                self.draw_cell(surface, camera, ix, iy)

    def draw_cell(self, surface, camera, ix, iy):
        kind, buildings, _ = self.block_data(ix, iy)
        ox, oy = int(ix*CELL-camera[0]), int(iy*CELL-camera[1])
        road_rect = pygame.Rect(int(ox), int(oy), CELL, CELL)
        pygame.draw.rect(surface, (61, 69, 86), road_rect)
        pygame.draw.rect(surface, (92, 95, 111), (ox+ROAD-7, oy+ROAD, CELL-ROAD, CELL-ROAD))
        pygame.draw.rect(surface, (92, 95, 111), (ox+ROAD, oy+ROAD-7, CELL-ROAD, CELL-ROAD))
        pygame.draw.line(surface, (240, 188, 138), (ox+ROAD, oy+ROAD), (ox+CELL, oy+ROAD), 3)
        pygame.draw.line(surface, (240, 188, 138), (ox+ROAD, oy+ROAD), (ox+ROAD, oy+CELL), 3)
        for dx in range(ROAD+25, CELL, 65):
            pygame.draw.line(surface, (180, 168, 145), (ox+dx, oy+ROAD//2-5), (ox+dx+27, oy+ROAD//2-5), 2)
        for dy in range(ROAD+25, CELL, 65):
            pygame.draw.line(surface, (180, 168, 145), (ox+ROAD//2-5, oy+dy), (ox+ROAD//2-5, oy+dy+27), 2)
        inner = pygame.Rect(int(ox+ROAD+5), int(oy+ROAD+5), CELL-ROAD-10, CELL-ROAD-10)
        if kind == "park":
            pygame.draw.rect(surface, (123, 174, 139), inner, border_radius=8)
            pygame.draw.rect(surface, (221, 201, 150), inner.inflate(-60, -60), 4, border_radius=18)
            rng = seeded(ix, iy, 2)
            for _ in range(13):
                tx = rng.randint(inner.left+20, inner.right-20)
                ty = rng.randint(inner.top+20, inner.bottom-20)
                pygame.draw.circle(surface, (59, 125, 103), (tx, ty), rng.randint(12, 21))
                pygame.draw.circle(surface, (83, 154, 119), (tx-4, ty-5), 8)
            pygame.draw.rect(surface, (58, 130, 157), (inner.centerx-35, inner.centery-22, 70, 44), border_radius=18)
        elif kind == "beach":
            pygame.draw.rect(surface, (231, 207, 153), inner)
            pygame.draw.rect(surface, (88, 179, 193), (inner.right-46, inner.top, 46, inner.height))
            for i in range(5):
                yy = inner.top + i*90
                pygame.draw.arc(surface, (190, 231, 222), (inner.right-50, yy, 56, 48), 0, math.pi, 3)
            rng = seeded(ix, iy, 3)
            for _ in range(5):
                draw_palm(surface, ox+rng.randint(ROAD+45, CELL-75), oy+rng.randint(ROAD+45, CELL-75), .62, (45, 120, 102))
        elif kind == "plaza":
            pygame.draw.rect(surface, (210, 177, 160), inner)
            for xx in range(inner.left+12, inner.right, 24):
                pygame.draw.line(surface, (224, 196, 170), (xx, inner.top), (xx, inner.bottom), 1)
            for yy in range(inner.top+12, inner.bottom, 24):
                pygame.draw.line(surface, (224, 196, 170), (inner.left, yy), (inner.right, yy), 1)
            pygame.draw.circle(surface, (80, 166, 184), inner.center, 45)
            pygame.draw.circle(surface, (228, 220, 181), inner.center, 30)
        else:
            pygame.draw.rect(surface, (199, 172, 152), inner)
        for bx, by, bw, bh, color, floors in buildings:
            rect = pygame.Rect(int(ox+ROAD+bx), int(oy+ROAD+by), bw, bh)
            if rect.right > ox+CELL-12 or rect.bottom > oy+CELL-12:
                continue
            pygame.draw.rect(surface, (54, 54, 73), rect.move(8, 9), border_radius=5)
            pygame.draw.rect(surface, color, rect, border_radius=5)
            pygame.draw.rect(surface, mix(color, (255, 231, 190), .42), rect.inflate(-12, -12), 3, border_radius=4)
            pygame.draw.rect(surface, mix(color, (255, 245, 219), .6), (rect.x+10, rect.y+8, rect.width-20, 12), border_radius=3)
            cols = max(2, bw//30)
            rows = max(2, bh//30)
            for row in range(rows):
                for col in range(cols):
                    wx = rect.x+13+col*max(22, (bw-25)//cols)
                    wy = rect.y+30+row*max(22, (bh-35)//rows)
                    if wx < rect.right-7 and wy < rect.bottom-7:
                        pygame.draw.rect(surface, (70, 117, 137), (wx, wy, 9, 12), border_radius=2)
                        pygame.draw.line(surface, (218, 223, 196), (wx+4, wy), (wx+4, wy+12), 1)
            if floors:
                pygame.draw.rect(surface, (255, 221, 137), (rect.centerx-13, rect.y+9, 26, 7), border_radius=3)


class Resident:
    SHAPES = ("square", "triangle", "circle")
    COLORS = [(90, 188, 190), (236, 176, 108), (196, 129, 171), (115, 151, 204), (231, 210, 149), (225, 133, 119)]

    def __init__(self, x, y, rng):
        self.x, self.y = x, y
        self.shape = rng.choice(self.SHAPES)
        self.color = rng.choice(self.COLORS)
        self.angle = rng.random()*TAU
        self.walk_timer = rng.uniform(.5, 3)
        self.aggressive = False
        self.health = 45
        self.attack_timer = 0
        self.alive = True
        self.hit_flash = 0

    def hurt(self, amount):
        if not self.alive:
            return False
        first_attack = not self.aggressive
        self.health -= amount
        self.aggressive = True
        self.hit_flash = .16
        if self.health <= 0:
            self.alive = False
        return first_attack

    def update(self, dt, player):
        if not self.alive:
            return
        self.hit_flash = max(0, self.hit_flash-dt)
        dx, dy = player.x-self.x, player.y-self.y
        dist = math.hypot(dx, dy) or 1
        if self.aggressive and dist < 560:
            self.angle = math.atan2(dy, dx)
            speed = 74
            if dist > 34:
                self.x += math.cos(self.angle)*speed*dt
                self.y += math.sin(self.angle)*speed*dt
            self.attack_timer -= dt
            if dist < 38 and self.attack_timer <= 0:
                player.health = max(0, player.health-7)
                self.attack_timer = .85
        else:
            self.walk_timer -= dt
            if self.walk_timer <= 0:
                self.angle += random.uniform(-1.7, 1.7)
                self.walk_timer = random.uniform(.7, 2.8)
            self.x += math.cos(self.angle)*22*dt
            self.y += math.sin(self.angle)*22*dt

    def draw(self, surface, camera):
        if not self.alive:
            return
        sx, sy = world_to_screen(self.x, self.y, camera)
        if not (-35 <= sx <= WIDTH+35 and -35 <= sy <= HEIGHT+35):
            return
        col = (255, 65, 83) if self.aggressive else self.color
        if self.hit_flash:
            col = (255, 241, 193)
        pygame.draw.ellipse(surface, (45, 46, 58), (sx-9, sy+8, 19, 8))
        if self.shape == "square":
            pygame.draw.rect(surface, col, (sx-8, sy-8, 16, 16), border_radius=3)
        elif self.shape == "circle":
            pygame.draw.circle(surface, col, (sx, sy), 9)
        else:
            pygame.draw.polygon(surface, col, ((sx, sy-11), (sx-10, sy+8), (sx+10, sy+8)))
        pygame.draw.circle(surface, (255, 226, 190), (sx+2, sy-2), 2)


WEAPONS = [
    {"name": "Без зброї", "kind": "none", "damage": 0, "rate": .3, "ammo": "∞"},
    {"name": "ГЛОК-17", "kind": "pistol", "damage": 28, "rate": .27, "ammo": "9 mm"},
    {"name": "УЗІ", "kind": "uzi", "damage": 12, "rate": .095, "ammo": "9 mm"},
    {"name": "ДРОБОВИК", "kind": "shotgun", "damage": 46, "rate": .68, "ammo": "12 ga"},
    {"name": "РПГ-7", "kind": "rpg", "damage": 130, "rate": .9, "ammo": "Ракета"},
]


class Player:
    def __init__(self):
        self.x, self.y = CELL*.5, CELL*.5
        self.health = 100
        self.weapon_index = 0
        self.fire_timer = 0
        self.vehicle = None

    @property
    def weapon(self):
        return WEAPONS[self.weapon_index]

    def move(self, keys, dt):
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        length = math.hypot(dx, dy)
        if length:
            self.x += dx/length*225*dt
            self.y += dy/length*225*dt
        self.fire_timer = max(0, self.fire_timer-dt)


CAR_COLORS = [(236, 92, 115), (71, 190, 194), (241, 194, 94), (210, 214, 213),
              (114, 126, 197), (220, 133, 180), (86, 97, 113)]


class Vehicle:
    def __init__(self, x, y, angle, color):
        self.x, self.y, self.angle = x, y, angle
        self.color = color
        self.speed = 0.0
        self.stolen = False
        self.hit_timer = 0.0
        self.health = 100
        self.alive = True

    def take_damage(self, amount):
        if not self.alive:
            return False
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            return True
        return False

    def drive(self, keys, dt):
        throttle = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])
        steer = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        if throttle > 0:
            self.speed = min(360, self.speed+430*dt)
        elif throttle < 0:
            self.speed = max(-155, self.speed-330*dt)
        else:
            self.speed *= max(0, 1-1.05*dt)
        self.hit_timer = max(0, self.hit_timer-dt)
        if steer:
            turn = (1.5 + min(abs(self.speed)/140, 1.15)) * dt
            self.angle += steer*turn*(1 if self.speed >= 0 else -1)
        self.x += math.cos(self.angle)*self.speed*dt
        self.y += math.sin(self.angle)*self.speed*dt

    def draw(self, surface, camera, police=False):
        if not self.alive:
            return
        sx, sy = world_to_screen(self.x, self.y, camera)
        if not (-75 <= sx <= WIDTH+75 and -75 <= sy <= HEIGHT+75):
            return
        car = pygame.Surface((62, 34), pygame.SRCALPHA)
        pygame.draw.rect(car, (36, 39, 54), (3, 4, 56, 27), border_radius=10)
        pygame.draw.rect(car, (240, 240, 224) if police else self.color, (3, 2, 56, 27), border_radius=9)
        pygame.draw.rect(car, (67, 107, 129), (17, 5, 26, 20), border_radius=6)
        pygame.draw.line(car, (205, 225, 214), (30, 6), (30, 24), 2)
        pygame.draw.rect(car, (255, 230, 169), (55, 7, 3, 5), border_radius=1)
        pygame.draw.rect(car, (255, 230, 169), (55, 19, 3, 5), border_radius=1)
        pygame.draw.rect(car, (42, 43, 53), (12, 0, 11, 4), border_radius=2)
        pygame.draw.rect(car, (42, 43, 53), (12, 28, 11, 4), border_radius=2)
        pygame.draw.rect(car, (42, 43, 53), (43, 0, 11, 4), border_radius=2)
        pygame.draw.rect(car, (42, 43, 53), (43, 28, 11, 4), border_radius=2)
        if police:
            pygame.draw.rect(car, (74, 143, 247), (25, 0, 7, 4))
            pygame.draw.rect(car, (245, 61, 86), (32, 0, 7, 4))
        rotated = pygame.transform.rotate(car, -math.degrees(self.angle))
        surface.blit(rotated, rotated.get_rect(center=(sx, sy)))


class Wanted:
    def __init__(self):
        self.heat = 0
        self.stars = 0
        self.escape_timer = 0.0

    def add_crime(self, points=1):
        self.heat += points
        self.stars = min(6, (self.heat+1)//2)
        self.escape_timer = 0

    def update(self, dt, player, police):
        if self.stars <= 0:
            self.escape_timer = 0
            return
        far = all(math.hypot(unit.x-player.x, unit.y-player.y) > 620 for unit in police)
        if far:
            self.escape_timer += dt
            if self.escape_timer >= 3.2:
                self.heat = max(0, self.heat-2)
                self.stars = min(6, (self.heat+1)//2)
                self.escape_timer = 0
        else:
            self.escape_timer = 0


class PoliceUnit:
    def __init__(self, x, y, helicopter=False):
        self.x, self.y = x, y
        self.helicopter = helicopter
        self.angle = 0
        self.fire_timer = random.uniform(.5, 1.8)
        self.health = 100
        self.alive = True

    def take_damage(self, amount):
        if not self.alive:
            return False
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            return True
        return False

    def update(self, dt, player, wanted, cop_bullets):
        if not self.alive:
            return
        dx, dy = player.x-self.x, player.y-self.y
        dist = math.hypot(dx, dy) or 1
        self.angle = math.atan2(dy, dx)
        speed = (135 + wanted.stars*17) if not self.helicopter else (160+wanted.stars*13)
        if dist > (230 if self.helicopter else 72):
            self.x += math.cos(self.angle)*speed*dt
            self.y += math.sin(self.angle)*speed*dt
        self.fire_timer -= dt
        shooting_range = 760 if self.helicopter else 570
        if dist < shooting_range and self.fire_timer <= 0:
            spread = random.uniform(-.08, .08)
            aim = self.angle+spread
            bullet_speed = 390 if self.helicopter else 340
            cop_bullets.append({"x":self.x, "y":self.y, "vx":math.cos(aim)*bullet_speed,
                                "vy":math.sin(aim)*bullet_speed, "life":2.5,
                                "damage":8 if wanted.stars >= 4 else 5})
            self.fire_timer = max(.38, 1.18-wanted.stars*.11) if not self.helicopter else max(.3, .9-wanted.stars*.09)

    def draw(self, surface, camera, tick):
        if not self.alive:
            return
        sx, sy = world_to_screen(self.x, self.y, camera)
        if not (-100 <= sx <= WIDTH+100 and -100 <= sy <= HEIGHT+100):
            return
        if self.helicopter:
            pygame.draw.ellipse(surface, (34, 39, 54), (sx-18, sy+4, 38, 13))
            pygame.draw.line(surface, (30, 34, 47), (sx-28, sy-9), (sx-1, sy-9), 3)
            pygame.draw.line(surface, (30, 34, 47), (sx+8, sy-14), (sx+8, sy-4), 2)
            pygame.draw.ellipse(surface, (239, 236, 219), (sx-13, sy-7, 27, 16))
            pygame.draw.ellipse(surface, (89, 151, 174), (sx-5, sy-6, 12, 12))
            pygame.draw.polygon(surface, (239, 236, 219), ((sx+12, sy-3), (sx+29, sy-8), (sx+30, sy-3), (sx+12, sy+2)))
            pygame.draw.line(surface, (49, 50, 60), (sx+31, sy-10), (sx+31, sy+5), 2)
            if int(tick*9) % 2:
                pygame.draw.circle(surface, (255, 70, 94), (sx-9, sy-9), 3)
            else:
                pygame.draw.circle(surface, (88, 157, 255), (sx-9, sy-9), 3)
        else:
            vehicle = Vehicle(self.x, self.y, self.angle, (225, 229, 221))
            vehicle.draw(surface, camera, police=True)


def spawn_parked_car(x, y, rng):
    ix, iy = math.floor(x/CELL), math.floor(y/CELL)
    if rng.random() < .5:
        return Vehicle(ix*CELL+rng.randint(170, CELL-45), iy*CELL+ROAD*.52, 0, rng.choice(CAR_COLORS))
    return Vehicle(ix*CELL+ROAD*.52, iy*CELL+rng.randint(170, CELL-45), math.pi/2, rng.choice(CAR_COLORS))


def make_parked_cars(player, rng, count=14):
    cars = []
    for _ in range(count):
        angle = rng.random()*TAU
        distance = rng.uniform(190, 850)
        cars.append(spawn_parked_car(player.x+math.cos(angle)*distance,
                                     player.y+math.sin(angle)*distance, rng))
    return cars


class Explosion:
    def __init__(self, x, y, radius):
        self.x, self.y, self.radius = x, y, radius
        self.age = 0.0
        self.duration = .72
        rng = random.Random(int(x*31+y*17))
        self.smoke = [(rng.random()*TAU, rng.uniform(.35, 1.0), rng.randint(8, 19)) for _ in range(11)]

    def update(self, dt):
        self.age += dt

    def draw(self, surface, camera):
        if self.age >= self.duration:
            return
        sx, sy = world_to_screen(self.x, self.y, camera)
        t = self.age/self.duration
        fade = max(0, 1-t)
        size = int(self.radius*2+16)
        layer = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = cy = size//2
        if self.age < .30:
            p = self.age/.30
            outer = max(4, int(self.radius*(.16+.84*p)))
            pygame.draw.circle(layer, (242, 76, 49, int(220*fade)), (cx, cy), outer)
            pygame.draw.circle(layer, (255, 174, 55, int(235*fade)), (cx, cy), int(outer*.70))
            pygame.draw.circle(layer, (255, 237, 165, int(245*fade)), (cx, cy), int(outer*.37))
            pygame.draw.circle(layer, (255, 255, 223, int(230*fade)), (cx, cy), max(2, int(outer*.16)))
        ring = int(self.radius*(.3+.85*t))
        pygame.draw.circle(layer, (255, 197, 91, int(190*fade)), (cx, cy), ring, max(2, int(7*fade)))
        for angle, speed, base_size in self.smoke:
            drift = self.age*72*speed
            px = int(cx+math.cos(angle)*drift)
            py = int(cy+math.sin(angle)*drift-self.age*34)
            puff = int(base_size*(.35+t))
            pygame.draw.circle(layer, (62, 54, 65, int(135*fade)), (px, py), puff)
        surface.blit(layer, (sx-cx, sy-cy))


def detonate_rocket(bullet, residents, parked_cars, police, wanted, explosions, player):
    x, y, radius = bullet["x"], bullet["y"], bullet["radius"]
    explosions.append(Explosion(x, y, radius))
    for resident in residents:
        distance = math.hypot(resident.x-x, resident.y-y)
        if resident.alive and distance < radius and resident.hurt(bullet["damage"]):
            wanted.add_crime(1)
    for car in parked_cars:
        distance = math.hypot(car.x-x, car.y-y)
        if car.alive and distance < radius:
            damage = bullet["damage"]*(1-.55*distance/radius)
            if car.take_damage(damage):
                explosions.append(Explosion(car.x, car.y, 67))
                wanted.add_crime(1)
    for unit in police:
        distance = math.hypot(unit.x-x, unit.y-y)
        if unit.alive and distance < radius:
            damage = bullet["damage"]*(1-.45*distance/radius)
            if unit.take_damage(damage):
                explosions.append(Explosion(unit.x, unit.y, 78 if not unit.helicopter else 92))
                wanted.add_crime(2)
    if player.vehicle and not player.vehicle.alive:
        player.vehicle = None


def draw_weapon(surface, player, camera, mouse):
    if player.weapon["kind"] == "none":
        return
    px, py = world_to_screen(player.x, player.y, camera)
    angle = math.atan2(mouse[1]-py, mouse[0]-px)
    length = 31 if player.weapon["kind"] != "rpg" else 42
    end = (int(px+math.cos(angle)*length), int(py+math.sin(angle)*length))
    pygame.draw.line(surface, (24, 28, 44), (px, py), end, 9)
    pygame.draw.line(surface, (207, 214, 209), (px, py), end, 5)
    pygame.draw.circle(surface, (255, 195, 118), (int(end[0]), int(end[1])), 4)


def draw_player(surface, player, camera):
    x, y = world_to_screen(player.x, player.y, camera)
    pygame.draw.ellipse(surface, (35, 35, 52), (x-15, y+11, 31, 11))
    pygame.draw.rect(surface, (255, 222, 139), (x-11, y-11, 22, 22), border_radius=4)
    pygame.draw.rect(surface, (255, 93, 168), (x-8, y-8, 16, 16), border_radius=3)


def sky_gradient(surface):
    top, mid, bottom = (247, 135, 157), (251, 165, 126), (255, 207, 139)
    for y in range(HEIGHT):
        t = y/HEIGHT
        color = mix(top, mid, t*2) if t < .5 else mix(mid, bottom, (t-.5)*2)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y))


def menu_background(surface, t):
    sky_gradient(surface)
    pygame.draw.circle(surface, (255, 221, 157), (WIDTH-250, 180), 102)
    pygame.draw.circle(surface, (255, 174, 148), (WIDTH-250, 180), 102, 4)
    rng = random.Random(14)
    x = -10
    while x < WIDTH+40:
        w, h = rng.randint(45, 115), rng.randint(105, 260)
        y = 430-h
        col = rng.choice([(89, 92, 123), (100, 93, 126), (113, 93, 119), (76, 88, 117)])
        pygame.draw.rect(surface, col, (x, y, w, h))
        pygame.draw.rect(surface, mix(col, (250, 198, 158), .35), (x+5, y+8, w-10, 6))
        for wy in range(y+24, 415, 25):
            for wx in range(x+9, x+w-8, 19):
                pygame.draw.rect(surface, (250, 205, 143), (wx, wy, 6, 9))
        x += w + rng.randint(3, 12)
    pygame.draw.rect(surface, (47, 54, 78), (0, 430, WIDTH, HEIGHT-430))
    pygame.draw.rect(surface, (66, 70, 88), (0, 438, WIDTH, 10))
    for i in range(12):
        draw_palm(surface, 42+i*116, 465+(i%2)*12, 1.0+(i%3)*.12)
    pygame.draw.rect(surface, (244, 105, 150), (0, 580, WIDTH, 5))
    for i in range(5):
        pygame.draw.rect(surface, (47, 54, 78), (0, 610+i*20, WIDTH, 5))


def draw_text(surface, font, text, pos, color, center=False, shadow=None):
    image = font.render(text, True, color)
    rect = image.get_rect(center=pos) if center else image.get_rect(topleft=pos)
    if shadow:
        sh = font.render(text, True, shadow)
        surface.blit(sh, rect.move(3, 4))
    surface.blit(image, rect)
    return rect


def main():
    pygame.init()
    pygame.display.set_caption("STP Vice City")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)
    small = pygame.font.SysFont("arial", 15)
    title_font = pygame.font.SysFont("georgia", 76, bold=True, italic=True)
    heading_font = pygame.font.SysFont("arial", 32, bold=True)
    city = City()
    player = Player()
    residents = []
    rng = random.Random()
    for _ in range(54):
        residents.append(Resident(player.x+rng.randint(-730, 730), player.y+rng.randint(-430, 430), rng))
    bullets = []
    cop_bullets = []
    explosions = []
    parked_cars = make_parked_cars(player, rng)
    wanted = Wanted()
    police = []
    mode = "menu"
    menu_button = pygame.Rect(WIDTH//2-130, 504, 260, 62)
    running = True
    while running:
        dt = min(clock.tick(FPS)/1000, .05)
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if mode == "game": mode = "menu"
                    else: running = False
                if mode == "game" and player.health > 0 and event.key == pygame.K_g:
                    mode = "weapons"
                elif mode == "weapons" and event.key == pygame.K_g:
                    mode = "game"
                if mode == "game" and player.health > 0 and event.key == pygame.K_e:
                    if player.vehicle:
                        car = player.vehicle
                        player.x = car.x+math.sin(car.angle)*42
                        player.y = car.y-math.cos(car.angle)*42
                        car.speed = 0
                        player.vehicle = None
                    else:
                        nearby = [car for car in parked_cars
                                  if math.hypot(car.x-player.x, car.y-player.y) < 68]
                        if nearby:
                            car = min(nearby, key=lambda item: math.hypot(item.x-player.x, item.y-player.y))
                            player.vehicle = car
                            if not car.stolen:
                                car.stolen = True
                                wanted.add_crime(2)
                if mode == "weapons" and pygame.K_1 <= event.key <= pygame.K_5:
                    player.weapon_index = event.key-pygame.K_1
                    mode = "game"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mode == "menu" and menu_button.collidepoint(event.pos):
                    player = Player()
                    bullets.clear()
                    cop_bullets.clear()
                    explosions.clear()
                    residents = []
                    for _ in range(54):
                        residents.append(Resident(player.x+rng.randint(-730, 730), player.y+rng.randint(-430, 430), rng))
                    parked_cars = make_parked_cars(player, rng)
                    wanted = Wanted()
                    police = []
                    mode = "game"
                elif mode == "weapons" and event.button == 1:
                    for i in range(len(WEAPONS)):
                        row = pygame.Rect(WIDTH//2-230, 242+i*67, 460, 54)
                        if row.collidepoint(event.pos):
                            player.weapon_index = i
                            mode = "game"
                elif mode == "game" and event.button == 1:
                    pass

        if mode in ("game", "weapons"):
            keys = pygame.key.get_pressed()
            if player.health > 0:
                if player.vehicle:
                    player.vehicle.drive(keys, dt)
                    player.x, player.y = player.vehicle.x, player.vehicle.y
                    player.fire_timer = max(0, player.fire_timer-dt)
                else:
                    player.move(keys, dt)
            camera = (player.x-WIDTH/2, player.y-HEIGHT/2)
            for resident in residents:
                resident.update(dt, player)
                if (player.vehicle and abs(player.vehicle.speed) > 95 and resident.alive
                        and player.vehicle.hit_timer <= 0
                        and math.hypot(resident.x-player.x, resident.y-player.y) < 31):
                    was_crime = resident.hurt(999)
                    if was_crime:
                        wanted.add_crime(1)
                    player.vehicle.hit_timer = .48

            residents = [r for r in residents if r.alive and math.hypot(r.x-player.x, r.y-player.y) < 1200]
            while len(residents) < 54:
                a = rng.random()*TAU
                d = rng.uniform(380, 820)
                residents.append(Resident(player.x+math.cos(a)*d, player.y+math.sin(a)*d, rng))
            if player.health <= 0:
                mode = "game"
            if mode == "game" and player.health > 0 and pygame.mouse.get_pressed()[0] and player.weapon["kind"] != "none" and player.fire_timer <= 0:
                w = player.weapon
                player.fire_timer = w["rate"]
                px, py = world_to_screen(player.x, player.y, camera)
                ang = math.atan2(mouse[1]-py, mouse[0]-px)
                if w["kind"] == "rpg":
                    bullets.append({"x":player.x+math.cos(ang)*43, "y":player.y+math.sin(ang)*43,
                                    "vx":math.cos(ang)*470, "vy":math.sin(ang)*470,
                                    "life":1.25, "damage":w["damage"], "radius":82, "rocket":True})
                else:
                    spread = .23 if w["kind"] == "shotgun" else (.075 if w["kind"] == "uzi" else .025)
                    pellets = 6 if w["kind"] == "shotgun" else 1
                    for _ in range(pellets):
                        a = ang+random.uniform(-spread, spread)
                        maxdist = 460 if w["kind"] == "shotgun" else 670
                        hit = None
                        best = maxdist
                        for resident in residents:
                            if not resident.alive: continue
                            dx, dy = resident.x-player.x, resident.y-player.y
                            along = dx*math.cos(a)+dy*math.sin(a)
                            side = abs(-dx*math.sin(a)+dy*math.cos(a))
                            if 0 < along < best and side < (22 if w["kind"] == "shotgun" else 12):
                                hit, best = resident, along
                        if hit and hit.hurt(w["damage"] if pellets == 1 else w["damage"]//2):
                            wanted.add_crime(1)
                    bullets.append({"x":player.x+math.cos(ang)*24, "y":player.y+math.sin(ang)*24, "vx":math.cos(ang)*410, "vy":math.sin(ang)*410, "life":.08, "damage":0, "radius":0, "rocket":False})
            for bullet in bullets[:]:
                bullet["x"] += bullet["vx"]*dt
                bullet["y"] += bullet["vy"]*dt
                bullet["life"] -= dt
                if bullet["rocket"]:
                    for resident in residents:
                        if resident.alive and math.hypot(resident.x-bullet["x"], resident.y-bullet["y"]) < 22:
                            bullet["life"] = 0
                            break
                    if bullet["life"] > 0:
                        for car in parked_cars:
                            if car.alive and math.hypot(car.x-bullet["x"], car.y-bullet["y"]) < 30:
                                bullet["life"] = 0
                                break
                    if bullet["life"] > 0:
                        for unit in police:
                            if unit.alive and math.hypot(unit.x-bullet["x"], unit.y-bullet["y"]) < 32:
                                bullet["life"] = 0
                                break
                if bullet["life"] <= 0:
                    if bullet["rocket"]:
                        detonate_rocket(bullet, residents, parked_cars, police, wanted, explosions, player)
                    bullets.remove(bullet)

            for explosion in explosions:
                explosion.update(dt)
            explosions = [effect for effect in explosions if effect.age < effect.duration]

            parked_cars = [car for car in parked_cars if car.alive and
                           (car is player.vehicle or math.hypot(car.x-player.x, car.y-player.y) < 1500)]
            while len(parked_cars) < 14:
                a = rng.random()*TAU
                d = rng.uniform(280, 950)
                parked_cars.append(spawn_parked_car(player.x+math.cos(a)*d,
                                                     player.y+math.sin(a)*d, rng))

            wanted.update(dt, player, police)
            ground_count = min(2+wanted.stars, 8) if wanted.stars else 0
            helicopter_count = max(0, wanted.stars-4)
            ground = [unit for unit in police if unit.alive and not unit.helicopter][:ground_count]
            helicopters = [unit for unit in police if unit.alive and unit.helicopter][:helicopter_count]
            while len(ground) < ground_count:
                a = rng.random()*TAU
                d = rng.uniform(460, 760)
                ground.append(PoliceUnit(player.x+math.cos(a)*d, player.y+math.sin(a)*d))
            while len(helicopters) < helicopter_count:
                a = rng.random()*TAU
                d = rng.uniform(570, 850)
                helicopters.append(PoliceUnit(player.x+math.cos(a)*d, player.y+math.sin(a)*d, True))
            police = ground+helicopters
            for unit in police:
                unit.update(dt, player, wanted, cop_bullets)

            
            for bullet in cop_bullets[:]:
                old_x, old_y = bullet["x"], bullet["y"]
                bullet["x"] += bullet["vx"]*dt
                bullet["y"] += bullet["vy"]*dt
                bullet["life"] -= dt
                dx, dy = bullet["x"]-old_x, bullet["y"]-old_y
                length2 = dx*dx+dy*dy or 1
                proj = clamp(((player.x-old_x)*dx+(player.y-old_y)*dy)/length2, 0, 1)
                closest = (old_x+proj*dx, old_y+proj*dy)
                hit_radius = 27 if player.vehicle else 17
                if math.hypot(player.x-closest[0], player.y-closest[1]) < hit_radius:
                    damage = bullet["damage"]*.58 if player.vehicle else bullet["damage"]
                    player.health = max(0, player.health-damage)
                    cop_bullets.remove(bullet)
                elif bullet["life"] <= 0:
                    cop_bullets.remove(bullet)

            city.draw(screen, camera)
            for iy in range(math.floor(camera[1]/CELL)-1, math.floor((camera[1]+HEIGHT)/CELL)+2):
                for ix in range(math.floor(camera[0]/CELL)-1, math.floor((camera[0]+WIDTH)/CELL)+2):
                    r = seeded(ix, iy, 4)
                    for side in range(4):
                        if r.random() < .76:
                            if side == 0: pos=(ix*CELL+ROAD+40, iy*CELL+ROAD+60+r.randint(0,240))
                            elif side == 1: pos=(ix*CELL+CELL-40, iy*CELL+ROAD+50+r.randint(0,240))
                            elif side == 2: pos=(ix*CELL+ROAD+50+r.randint(0,260), iy*CELL+ROAD+38)
                            else: pos=(ix*CELL+ROAD+50+r.randint(0,260), iy*CELL+CELL-40)
                            sx, sy = world_to_screen(*pos, camera)
                            if -30 < sx < WIDTH+30 and -30 < sy < HEIGHT+30: draw_palm(screen, sx, sy, .53, (51, 120, 101))
            for car in parked_cars:
                car.draw(screen, camera)
            for unit in police:
                unit.draw(screen, camera, pygame.time.get_ticks()/1000)
            for b in bullets:
                sx, sy = world_to_screen(b["x"], b["y"], camera)
                color = (255, 163, 76) if b["rocket"] else (255, 245, 179)
                pygame.draw.circle(screen, color, (sx, sy), 7 if b["rocket"] else 3)
                if b["rocket"]: pygame.draw.circle(screen, (247, 93, 103), (sx, sy), 10, 2)
            for b in cop_bullets:
                sx, sy = world_to_screen(b["x"], b["y"], camera)
                pygame.draw.circle(screen, (255, 84, 94), (sx, sy), 4)
            for resident in residents: resident.draw(screen, camera)
            for explosion in explosions:
                explosion.draw(screen, camera)
            if not player.vehicle:
                draw_player(screen, player, camera)
                draw_weapon(screen, player, camera, mouse)
            pygame.draw.rect(screen, (24, 28, 46), (18, 18, 290, 92), border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), (18, 18, 290, 92), 2, border_radius=12)
            draw_text(screen, heading_font, "STP  /  VICE CITY", (34, 27), (255, 131, 174), shadow=(30, 27, 50))
            pygame.draw.rect(screen, (68, 72, 93), (35, 75, 205, 13), border_radius=6)
            pygame.draw.rect(screen, (244, 83, 116), (35, 75, int(205*player.health/100), 13), border_radius=6)
            draw_text(screen, small, f"ЗДОРОВ’Я  {int(player.health)}%", (248, 73), (241, 231, 213))
            draw_text(screen, small, f"ЗБРОЯ  {player.weapon['name']}   •   G — вибір", (22, HEIGHT-37), (255, 239, 213), shadow=(33, 35, 54))
            draw_text(screen, small, "WASD / стрілки — рух     Миша — приціл і вогонь", (WIDTH-413, HEIGHT-37), (255, 239, 213), shadow=(33, 35, 54))
            wanted_panel = pygame.Rect(WIDTH-300, 18, 282, 56)
            pygame.draw.rect(screen, (24, 28, 46), wanted_panel, border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), wanted_panel, 2, border_radius=12)
            draw_text(screen, small, "РОЗШУК", (wanted_panel.x+14, wanted_panel.y+18), (239, 231, 216))
            for i in range(6):
                star_color = (255, 201, 79) if i < wanted.stars else (87, 91, 112)
                draw_text(screen, font, "★", (wanted_panel.x+94+i*28, wanted_panel.y+13), star_color)
            if player.vehicle:
                prompt = f"E — вийти з авто   •   ШВИДКІСТЬ {int(abs(player.vehicle.speed))}"
            else:
                near_car = any(math.hypot(car.x-player.x, car.y-player.y) < 68 for car in parked_cars)
                prompt = "E — викрасти авто" if near_car else "E — сісти в авто поруч"
            draw_text(screen, small, prompt, (WIDTH//2, HEIGHT-37), (255, 226, 160), True, shadow=(33, 35, 54))
            if wanted.stars and wanted.escape_timer > 0:
                draw_text(screen, small, "ВТЕЧИ ВІД ПОЛІЦІЇ, ЩОБ СКИНУТИ РОЗШУК", (WIDTH//2, 28), (255, 219, 147), True, shadow=(33, 35, 54))
            if player.health <= 0:
                pygame.draw.rect(screen, (25, 25, 45), (0, 0, WIDTH, HEIGHT), 150)
                draw_text(screen, title_font, "GAME OVER", (WIDTH//2, HEIGHT//2-20), (255, 100, 151), True, (44, 33, 57))
                draw_text(screen, font, "Натисни Esc, щоб повернутися у меню", (WIDTH//2, HEIGHT//2+58), (255, 239, 213), True)
            if mode == "weapons":
                shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                shade.fill((13, 17, 35, 194))
                screen.blit(shade, (0, 0))
                pygame.draw.rect(screen, (32, 36, 61), (WIDTH//2-265, 142, 530, 438), border_radius=18)
                pygame.draw.rect(screen, NEON_PINK, (WIDTH//2-265, 142, 530, 438), 2, border_radius=18)
                draw_text(screen, heading_font, "ВИБІР ЗБРОЇ", (WIDTH//2, 192), NEON_CYAN, True)
                for i, weapon in enumerate(WEAPONS):
                    row = pygame.Rect(WIDTH//2-230, 242+i*67, 460, 54)
                    active = i == player.weapon_index
                    pygame.draw.rect(screen, (80, 72, 104) if active else (46, 51, 77), row, border_radius=9)
                    pygame.draw.rect(screen, NEON_PINK if active else (89, 101, 125), row, 2, border_radius=9)
                    draw_text(screen, font, f"{i+1}.  {weapon['name']}", (row.x+18, row.y+14), (255, 218, 225) if active else (237, 238, 225))
                    draw_text(screen, small, weapon["ammo"], (row.right-85, row.y+18), (177, 224, 223))
                draw_text(screen, small, "Клікни на зброю або натисни 1–5.  G — назад", (WIDTH//2, 554), (214, 216, 229), True)

        elif mode == "menu":
            menu_background(screen, pygame.time.get_ticks()/1000)
            draw_text(screen, small, "PRESENTS", (WIDTH//2, 150), (240, 229, 208), True)
            draw_text(screen, title_font, "STP", (WIDTH//2, 247), NEON_CYAN, True, (74, 46, 78))
            draw_text(screen, title_font, "Vice City", (WIDTH//2, 334), (255, 106, 164), True, (81, 40, 88))
            draw_text(screen, small, "НЕОНОВІ ВУЛИЦІ. БЕЗКІНЕЧНИЙ ЗАХІД СОНЦЯ.", (WIDTH//2, 420), (255, 239, 213), True)
            pygame.draw.rect(screen, (48, 51, 77), menu_button, border_radius=15)
            pygame.draw.rect(screen, NEON_CYAN, menu_button, 2, border_radius=15)
            draw_text(screen, heading_font, "ПОЧАТИ", menu_button.center, (255, 233, 219), True)
            draw_text(screen, small, "WASD — рух / кермо     E — авто     Миша — приціл     G — зброя", (WIDTH//2, 655), (255, 230, 208), True)

        pygame.display.flip()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
