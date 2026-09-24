# The smiley pack's ball texture: 1024x512 equirectangular (u = around the ball, v = from the top pole to the
# bottom), yellow with one black smiley face. The face is drawn in the plane touching the ball at its centre (on the
# equator) and projected onto the sphere, so it is round on the ball rather than stretched like a flat image would be.
import numpy as np
from PIL import Image, ImageDraw

W, H = 1024, 512
YELLOW = np.array([255, 214, 0], float)
BLACK = np.array([12, 12, 12], float)


def direction(u, v):
    lon, col = 2 * np.pi * u, np.pi * v
    return np.stack([np.sin(col) * np.cos(lon), np.sin(col) * np.sin(lon), np.cos(col)], -1)


centre = direction(np.array(0.625), np.array(0.5))
up = np.array([0.0, 0.0, 1.0])
east = np.cross(up, centre)
east /= np.linalg.norm(east)


def ink(u, v):
    d = direction(u, v)
    z = d @ centre
    x = (d @ east) / np.maximum(z, 1e-6)
    y = (d @ up) / np.maximum(z, 1e-6)
    front = z > 0.25
    out = np.zeros_like(u, bool)
    for ex in (-0.27, 0.27):
        out |= front & (((x - ex) / 0.1) ** 2 + ((y - 0.3) / 0.18) ** 2 < 1)
    r = np.hypot(x, y - 0.15)
    out |= front & (np.abs(r - 0.55) < 0.06) & (y < 0.02) & (np.abs(x) < 0.52)
    return out


uu, vv = np.meshgrid((np.arange(W) + 0.5) / W, (np.arange(H) + 0.5) / H)
coverage = np.zeros((H, W))
for dy in (-1 / 3, 0, 1 / 3):                   # 3x3 samples per pixel for smooth edges
    for dx in (-1 / 3, 0, 1 / 3):
        coverage += ink(uu + dx / W, vv + dy / H)
a = (coverage / 9)[..., None]
Image.fromarray((YELLOW * (1 - a) + BLACK * a).clip(0, 255).astype(np.uint8)).save("smiley_ball.png")

# The tile picture: a round smiley.
S, k = 256, 4
im = Image.new("RGBA", (S * k, S * k), (0, 0, 0, 0))
g = ImageDraw.Draw(im)
g.ellipse([8 * k, 8 * k, (S - 8) * k, (S - 8) * k], fill=(255, 214, 0, 255))
for ex in (96, 160):
    g.ellipse([(ex - 13) * k, 70 * k, (ex + 13) * k, 118 * k], fill=(12, 12, 12, 255))
g.arc([62 * k, 70 * k, 194 * k, 200 * k], start=25, end=155, fill=(12, 12, 12, 255), width=15 * k)
im.resize((S, S), Image.LANCZOS).save("smiley_preview.png")

# The party cone's tile picture: a striped cone.
im = Image.new("RGBA", (S * k, S * k), (0, 0, 0, 0))
g = ImageDraw.Draw(im)
top, base_y, half = (128 * k, 24 * k), 222 * k, 78 * k
g.polygon([top, (128 * k - half, base_y), (128 * k + half, base_y)], fill=(150, 150, 158, 255))
for i, t in enumerate((0.35, 0.6, 0.85)):
    y = top[1] + (base_y - top[1]) * t
    w = half * t
    g.line([(128 * k - w, y), (128 * k + w, y)], fill=(95, 95, 102, 255), width=10 * k)
g.ellipse([(128 - 12) * k, 12 * k, (128 + 12) * k, 36 * k], fill=(255, 214, 0, 255))
im.resize((S, S), Image.LANCZOS).save("cone_preview.png")

# The big fire's tile picture: a flame burst.
import math
im = Image.new("RGBA", (S * k, S * k), (0, 0, 0, 0))
g = ImageDraw.Draw(im)
for radius, colour in ((118, (200, 40, 10, 255)), (92, (245, 110, 20, 255)), (62, (255, 200, 40, 255)), (30, (255, 245, 190, 255))):
    points = []
    for i in range(24):
        a = 2 * math.pi * i / 24
        r = radius * (1.0 if i % 2 == 0 else 0.62)
        points.append(((128 + r * math.cos(a)) * k, (128 + r * math.sin(a)) * k))
    g.polygon(points, fill=colour)
im.resize((S, S), Image.LANCZOS).save("big_fire_preview.png")

# The plugin's icon: the smiley.
Image.open("smiley_preview.png").save("icon.png")


# ---------------------------------------------------------------------------------------------------------------
# Textures sampled on the sphere itself (a direction per pixel), so they have no seam and no pinching at the poles.
rng = np.random.default_rng(7)
LATTICE = rng.random((64, 64, 64))


def noise3(p):
    """Smooth value noise at points p (..., 3), period 64."""
    i = np.floor(p).astype(int)
    f = p - i
    f = f * f * (3 - 2 * f)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1]) * (f[..., 2] if dz else 1 - f[..., 2])
                out = out + w * LATTICE[(i[..., 0] + dx) % 64, (i[..., 1] + dy) % 64, (i[..., 2] + dz) % 64]
    return out


def fbm(p, octaves=5):
    total, amp, norm = 0, 1.0, 0
    for o in range(octaves):
        total = total + amp * noise3(p * (2 ** o) + 17.3 * o)
        norm += amp
        amp *= 0.5
    return total / norm


dirs = direction(uu, vv)

# The meatball: browned meat, darker crust in the hollows, a few light specks and some tomato sauce.
n = fbm(dirs * 3.0 + 5)
fine = fbm(dirs * 14.0 + 40, 3)
meat = np.array([118, 62, 36], float)
crust = np.array([62, 30, 18], float)
light = np.array([168, 102, 64], float)
sauce = np.array([150, 28, 18], float)
t = np.clip((n - 0.35) * 2.2, 0, 1)[..., None]
colour = crust * (1 - t) + meat * t
colour = colour + (np.clip((fine - 0.55) * 3, 0, 1)[..., None]) * (light - colour) * 0.8
speck = (fbm(dirs * 30.0 + 90, 2) > 0.8)[..., None]
colour = np.where(speck, np.array([205, 170, 120], float), colour)
s = np.clip((fbm(dirs * 1.6 + 200, 3) - 0.56) * 6, 0, 1)[..., None]
colour = colour * (1 - s * 0.85) + sauce * s * 0.85
Image.fromarray(colour.clip(0, 255).astype(np.uint8)).save("meatball.png")

# The morph ball: orange armour, each of the eight panels (between the seams the model's rings sit on) shaded from
# its centre, with a thin darker groove along every seam.
x, y, z = dirs[..., 0], dirs[..., 1], dirs[..., 2]
orange = np.array([236, 96, 24], float)
dark = np.array([150, 44, 12], float)
edge = np.minimum(np.minimum(np.abs(x), np.abs(y)), np.abs(z))       # distance to the nearest seam plane
centre = np.abs(x * np.sign(x) + y * np.sign(y) + z * np.sign(z)) / np.sqrt(3)
shade = np.clip((centre - 0.6) / 0.4, 0, 1)[..., None]
colour = dark * (1 - shade) + orange * shade
groove = np.clip(1 - edge / 0.06, 0, 1)[..., None]
colour = colour * (1 - groove * 0.6)
colour = colour * (0.92 + 0.16 * fbm(dirs * 8 + 300, 2))[..., None]
Image.fromarray(colour.clip(0, 255).astype(np.uint8)).save("morph_ball.png")


# Tile pictures.
def canvas():
    im = Image.new("RGBA", (S * k, S * k), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def done(im, name):
    im.resize((S, S), Image.LANCZOS).save(name)


# Morph ball: an orange ball, dark seams, glowing lights.
im, g = canvas()
g.ellipse([20 * k, 20 * k, 236 * k, 236 * k], fill=(236, 96, 24, 255))
g.line([(20 * k, 128 * k), (236 * k, 128 * k)], fill=(60, 60, 66, 255), width=12 * k)
g.line([(128 * k, 20 * k), (128 * k, 236 * k)], fill=(60, 60, 66, 255), width=12 * k)
for cx, cy in ((80, 80), (176, 80), (80, 176), (176, 176)):
    g.ellipse([(cx - 20) * k, (cy - 20) * k, (cx + 20) * k, (cy + 20) * k], fill=(60, 60, 66, 255))
    g.ellipse([(cx - 13) * k, (cy - 13) * k, (cx + 13) * k, (cy + 13) * k], fill=(255, 236, 90, 255))
done(im, "morph_preview.png")

# Meatball: a brown ball with a saw blade through it.
im, g = canvas()
teeth = []
for i in range(56):
    a = 2 * math.pi * i / 56
    r = 124 if i % 2 == 0 else 108
    teeth.append(((128 + r * math.cos(a)) * k, (128 + r * math.sin(a)) * k))
g.polygon(teeth, fill=(200, 205, 212, 255))
g.ellipse([40 * k, 40 * k, 216 * k, 216 * k], fill=(118, 62, 36, 255))
for cx, cy, r in ((95, 90, 14), (150, 120, 18), (110, 160, 12), (165, 75, 9)):
    g.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=(70, 34, 20, 255))
g.ellipse([118 * k, 50 * k, 150 * k, 70 * k], fill=(150, 28, 18, 255))
done(im, "meatball_preview.png")

# Fruit basket.
im, g = canvas()
g.arc([56 * k, 40 * k, 200 * k, 190 * k], start=180, end=360, fill=(120, 76, 36, 255), width=10 * k)
for cx, cy, r, c in ((90, 120, 30, (210, 30, 30)), (150, 116, 30, (245, 140, 20)), (120, 96, 26, (120, 200, 40)),
                     (178, 132, 16, (110, 40, 140)), (190, 118, 16, (110, 40, 140))):
    g.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=c + (255,))
g.polygon([(40 * k, 130 * k), (216 * k, 130 * k), (190 * k, 222 * k), (66 * k, 222 * k)], fill=(170, 112, 56, 255))
for yy in range(145, 222, 16):
    g.line([(50 * k, yy * k), (206 * k, yy * k)], fill=(120, 76, 36, 255), width=4 * k)
done(im, "basket_preview.png")

# Confetti.
im, g = canvas()
cols = [(235, 60, 60), (255, 210, 40), (60, 170, 240), (80, 200, 90), (230, 90, 200), (255, 140, 40)]
r2 = np.random.default_rng(3)
for i in range(70):
    a = r2.random() * 2 * math.pi
    d = 20 + r2.random() * 100
    cx, cy = 128 + d * math.cos(a), 128 + d * math.sin(a)
    w, h, rot = 6 + r2.random() * 8, 12 + r2.random() * 10, r2.random() * math.pi
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    pts = [((cx + px * math.cos(rot) - py * math.sin(rot)) * k, (cy + px * math.sin(rot) + py * math.cos(rot)) * k) for px, py in pts]
    g.polygon(pts, fill=cols[i % len(cols)] + (255,))
done(im, "confetti_preview.png")
