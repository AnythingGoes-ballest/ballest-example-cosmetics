# Example Cosmetics

A plugin for the [Ballest plugin manager](https://github.com/AnythingGoes-ballest/ballest-plugin-manager): examples of
each kind of custom cosmetic, added to the **Customize** page through
[Cosmetic Kit](https://github.com/AnythingGoes-ballest/ballest-cosmetic-kit).

| Tab | Cosmetic | Shows |
|---|---|---|
| balls | smiley | a texture only |
| balls | AnythingGoes | a photo on the ball, projected so it isn't stretched |
| balls | morph ball | a model with depth: raised armour seams and glowing lights |
| balls | saw meatball | a model that moves: a saw blade spinning around the ball, kept level as it rolls |
| balls | T-rex | a 3D model file (glTF) in a clear ball: its own colours, running faster as the ball speeds up and idling when it stops |
| balls | skeleton | a 3D model file with a texture and glowing eyes, running inside a clear ball |
| hats | fruit basket | a hat that is a model |
| hats | baseball cap | a hat that is a 3D model file, turned upright with its brim forward |
| bfx | confetti | one of the game's goal explosions with the game's confetti burst and confetti-gun sound |

## Install

In the game: footer **plugins** > **browse** > Example Cosmetics > **install** (Cosmetic Kit comes with it).
Needs the plugin manager host 0.16.0 or newer.

## Files

- `main.as`: adds the cosmetics.
- `models/`: the models, one text file each (the format is in the plugin manager's
  [custom cosmetics guide](https://anythinggoes-ballest.github.io/ballest-plugin-manager/guides/cosmetics/)), and the
  3D model files they place (`.glb`). `trex.glb` and `skeleton.glb` keep only the animations used (run and idle) to
  stay small.
- `make_model_previews.py`: draws the 3D models' tile pictures, posed by the plugin manager's own model reader.
- `*.png`: the ball textures and tile pictures, made by `make_images.py` from `anythinggoes_profile.jpg` and code (Python with NumPy and Pillow). The textures
  are drawn on the sphere, so the smiley isn't stretched and the meatball has no seam.

## Credits

The 3D models are other people's work, used under their licences:

- `models/trex.glb`: "T-Rex" from the Animated Dinosaur Pack by [Quaternius](https://quaternius.com), CC0 (public
  domain). Trimmed to its run and idle animations.
- `models/skeleton.glb`: "Skeleton Minion" from the
  [KayKit Character Pack: Skeletons](https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Skeletons-1.0) by
  Kay Lousberg, CC0 (public domain). Trimmed to its Running_A and Idle animations.
- `models/cap.glb`: "Baseball Cap" by Jarlan Perez ([Poly Pizza](https://poly.pizza/m/2uKEHjO_QL0)), licensed under
  [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).

## License

MIT for the code and the other images. The 3D models keep their own licences (above).
