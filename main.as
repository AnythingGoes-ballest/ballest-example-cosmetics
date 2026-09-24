// Example Cosmetics: examples of each kind of custom cosmetic, added to the Customize page through Cosmetic Kit (a
// dependency: see info.toml).
//   balls   a smiley (just a texture), a morph ball (raised seams and glowing lights: a model with depth) and a saw
//           meatball (a spinning saw blade: a model that moves)
//   hat     a basket of fruit (a model)
//   bfx     confetti (the game's confetti burst and confetti gun sound)

import bool AddBall(const string &in, const string &in, const string &in, const string &in, const string &in) from "cosmetic-kit";
import bool AddHat(const string &in, const string &in, const string &in, double, const string &in, const string &in) from "cosmetic-kit";
import bool AddBfx(const string &in, const string &in, const string &in, double, const string &in, const string &in, const string &in) from "cosmetic-kit";

void Main()
{
    string f = Plugins::Folder();
    AddBall("example-cosmetics.smiley", "smiley", f + "smiley_ball.png", f + "smiley_preview.png", "");
    AddBall("example-cosmetics.morph-ball", "morph ball", f + "morph_ball.png", f + "morph_preview.png", f + "models/morph_ball.txt");
    AddBall("example-cosmetics.saw-meatball", "saw meatball", f + "meatball.png", f + "meatball_preview.png", f + "models/saw_ball.txt");
    AddHat("example-cosmetics.fruit-basket", "fruit basket", "", 1.0, f + "basket_preview.png", f + "models/fruit_basket.txt");
    AddBfx("example-cosmetics.confetti", "confetti", "/Game/Art/DataAssets/GoalExplosions/Fire1/DA_Fire1.DA_Fire1", 1.0,
           f + "confetti_preview.png", "/Game/Art/NS_BallExplosion.NS_BallExplosion", "/Game/Sound/Menus/SFX_ConfettiGun.SFX_ConfettiGun");
}
