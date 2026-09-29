"""Tile pictures for the 3D model cosmetics: each model drawn flat-shaded in its own colours (texture colours sampled
per face, glowing parts at full brightness), placed as its model file places it, on a transparent 256x256 tile; the
balls inside a pale glass disc, like the other ball tiles.

The posed models come from the plugin manager's model reader (tools/tests/meshfile_test.cpp, built with its
llvm-mingw), so the pictures show what the game builds:
    python make_model_previews.py <path to ballest-plugin-manager>
"""
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TOOL = Path(sys.argv[1]) / "build" / "meshfile_test.exe"
SIZE, SCALE = 256, 4                    # drawn 4x larger, then scaled down (smooth edges)


def load_obj(path):
    v, vt, faces, mat = [], [], [], None
    materials = {}
    for line in open(path):
        p = line.split()
        if not p:
            continue
        if p[0] == "mtllib":
            materials = load_mtl(path.parent / " ".join(p[1:]))
        elif p[0] == "v":
            v.append([float(x) for x in p[1:4]])
        elif p[0] == "vt":
            vt.append([float(x) for x in p[1:3]])
        elif p[0] == "usemtl":
            mat = p[1]
        elif p[0] == "f":
            faces.append(([int(c.split("/")[0]) - 1 for c in p[1:4]], [int(c.split("/")[1]) - 1 for c in p[1:4]], mat))
    return np.array(v), np.array(vt) if vt else np.zeros((len(v), 2)), faces, materials


def load_mtl(path):
    out, cur = {}, None
    for line in open(path):
        p = line.split()
        if not p:
            continue
        if p[0] == "newmtl":
            cur = out.setdefault(p[1], {"Kd": (0.8, 0.8, 0.8), "Ke": (0, 0, 0), "tex": None})
        elif p[0] in ("Kd", "Ke"):
            cur[p[0]] = tuple(float(x) for x in p[1:4])
        elif p[0] == "map_Kd":
            cur["tex"] = np.asarray(Image.open(line.split(None, 1)[1].strip()).convert("RGB"), float) / 255
    return out


def turn(rot, p):
    """The engine's rotator turn (FRotationMatrix), as models.cpp applies "rot"."""
    sp, cp = math.sin(math.radians(rot[0])), math.cos(math.radians(rot[0]))
    sy, cy = math.sin(math.radians(rot[1])), math.cos(math.radians(rot[1]))
    sr, cr = math.sin(math.radians(rot[2])), math.cos(math.radians(rot[2]))
    x = np.array([cp * cy, cp * sy, sp])
    y = np.array([sr * sp * cy - cr * sy, sr * sp * sy + cr * cy, -sr * cp])
    z = np.array([-(cr * sp * cy + sr * sy), cy * sr - cr * sp * sy, cr * cp])
    return p[:, 0:1] * x + p[:, 1:2] * y + p[:, 2:3] * z


def place(v, size, rot=(0, 0, 0), at=(0, 0, 0)):
    """As models.cpp places a mesh: longest side "size", turned, bottom of the bounds (centred) on "at"."""
    k = size / (v.max(axis=0) - v.min(axis=0)).max()
    p = turn(rot, v * k)
    lo, hi = p.min(axis=0), p.max(axis=0)
    stand = np.array([(lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, lo[2]])
    return p + (np.array(at) - stand)


def srgb(c):
    return np.clip(np.power(np.clip(c, 0, 1), 1 / 2.2), 0, 1)


def draw(model, glass_ball, out, azimuth=35, elevation=15, extent=60, centre_z=0):
    v, vt, faces, mats = model
    az, el = math.radians(azimuth), math.radians(elevation)
    view = np.array([math.cos(az) * math.cos(el), math.sin(az) * math.cos(el), math.sin(el)])     # towards the camera
    f = -view
    right = np.array([-f[1], f[0], 0.0])                # the game's space is left-handed
    right /= np.linalg.norm(right)
    up = np.array([0.0, 0.0, 1.0]) - f[2] * f
    up /= np.linalg.norm(up)
    light = view * 0.6 + np.array([0.0, 0.0, 0.8])
    light /= np.linalg.norm(light)
    px = SIZE * SCALE

    def to_screen(p):
        return np.stack([px / 2 + (p @ right) / extent * px / 2, px / 2 - ((p @ up) - centre_z) / extent * px / 2], -1)

    img = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    if glass_ball:                                      # the ball's back half
        r = 50 / extent * px / 2
        c = to_screen(np.zeros((1, 3)))[0]
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(205, 225, 240, 90))
    tris = np.array([v[i] for i, _, _ in faces])
    depth = tris.mean(axis=1) @ view
    for n in np.argsort(depth):
        idx, tidx, mat = faces[n]
        m = mats.get(mat, {"Kd": (0.8, 0.8, 0.8), "Ke": (0, 0, 0), "tex": None})
        t = tris[n]
        normal = np.cross(t[1] - t[0], t[2] - t[0])
        length = np.linalg.norm(normal)
        if length == 0:
            continue
        shade = 0.45 + 0.55 * abs(normal @ light) / length
        if m["tex"] is not None:
            u, w = vt[tidx].mean(axis=0)
            tex = m["tex"]
            colour = tex[min(int(w % 1 * tex.shape[0]), tex.shape[0] - 1), min(int(u % 1 * tex.shape[1]), tex.shape[1] - 1)] ** 2.2
        else:
            colour = np.array(m["Kd"])
        if max(m["Ke"]) > 0.01:
            rgb = srgb(np.array(m["Ke"]) / max(m["Ke"]))
        else:
            rgb = srgb(colour * shade)
        s = to_screen(t)
        d.polygon([tuple(p) for p in s], fill=tuple(int(c * 255) for c in rgb) + (255,))
    if glass_ball:                                      # the front of the ball: a rim and a highlight
        r = 50 / extent * px / 2
        c = to_screen(np.zeros((1, 3)))[0]
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=(230, 240, 250, 200), width=SCALE * 5)
        d.arc([c[0] - r * 0.8, c[1] - r * 0.8, c[0] + r * 0.8, c[1] + r * 0.8], 200, 250, fill=(255, 255, 255, 170), width=SCALE * 6)
    img.resize((SIZE, SIZE), Image.LANCZOS).save(out)
    print("wrote", out.name)


def posed(model_file, animation, seconds, work):
    obj = work / (model_file.stem + ".obj")
    subprocess.run([str(TOOL), str(model_file), animation, str(seconds), str(obj)], check=True, capture_output=True)
    return load_obj(obj)


with tempfile.TemporaryDirectory() as tmp:
    work = Path(tmp)
    v, vt, faces, mats = posed(HERE / "models" / "trex.glb", "run", 0.23, work)
    draw((place(v, 85, at=(0, 0, -44)), vt, faces, mats), True, HERE / "trex_preview.png", azimuth=-60, extent=58)
    v, vt, faces, mats = posed(HERE / "models" / "skeleton.glb", "running_a", 0.2, work)
    draw((place(v, 80, at=(0, 0, -45)), vt, faces, mats), True, HERE / "skeleton_preview.png", azimuth=25, extent=58)
    v, vt, faces, mats = posed(HERE / "models" / "cap.glb", "", 0, work)
    draw((place(v, 36, rot=(-10.7, -141.9, 8.5)), vt, faces, mats), False, HERE / "cap_preview.png", azimuth=-40, elevation=20,
         extent=24, centre_z=10)
