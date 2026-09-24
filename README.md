# Example Cosmetics

A plugin for the [Ballest plugin manager](https://github.com/AnythingGoes-ballest/ballest-plugin-manager): examples of
each kind of custom cosmetic, added to the **Customize** page through
[Cosmetic Kit](https://github.com/AnythingGoes-ballest/ballest-cosmetic-kit).

| Tab | Cosmetic | Shows |
|---|---|---|
| balls | smiley | a texture only |
| balls | morph ball | a model with depth: raised armour seams and glowing lights |
| balls | saw meatball | a model that moves: a saw blade spinning around the ball, kept level as it rolls |
| hats | fruit basket | a hat that is a model |
| bfx | confetti | one of the game's goal explosions with the game's confetti burst and confetti-gun sound |

## Install

In the game: footer **plugins** > **open** > **browse** > Example Cosmetics > **install** (Cosmetic Kit comes with it).
Needs the plugin manager host 0.8.0 or newer.

## Files

- `main.as`: adds the cosmetics.
- `models/`: the models, one text file each (the format is in the plugin manager's
  [custom cosmetics guide](https://anythinggoes-ballest.github.io/ballest-plugin-manager/guides/cosmetics/)).
- `*.png`: the ball textures and tile pictures, made by `make_images.py` (Python with NumPy and Pillow). The textures
  are drawn on the sphere, so the smiley isn't stretched and the meatball has no seam.

## License

MIT
