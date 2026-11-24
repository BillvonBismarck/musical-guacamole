#!/usr/bin/env python3
"""Build docs/realm-wardens/manifest.json from the Realm Wardens prompt spec."""
import json, os

STYLE = (
    "stylized hand-painted high-fantasy game art, chunky heroic proportions, "
    "oversized hands, shoulders and weapons, bold readable silhouette from a high "
    "top-down camera, low-poly faceted forms with soft painted gradients, saturated "
    "but warm palette, strong color blocking, clean shapes, no fine noise detail, "
    "single centered object, neutral light grey background, even studio lighting"
)
NEG = (
    "photorealistic, gritty realism, thin spindly limbs, tiny details, text, logo, "
    "watermark, signature, multiple objects, ground plane, cast shadow on background, "
    "cropped, cut-off parts, blurry, existing franchise characters, recognizable "
    "trademarked designs or emblems"
)
ADD3D = (
    "game-ready low-poly 3D model, A-pose for characters, feet flat on ground, "
    "whole object visible, simple solid color regions, under 6k triangles"
)

HUMANOID = ["Body", "Head", "ArmL", "ArmR", "LegL", "LegR"]

assets = []


def a(id_, group, prompt, subject="biped", quality="balanced", face=6000,
      size=None, parts=None, concept=True, face_sketch=""):
    assets.append({
        "id": id_, "group": group, "prompt": prompt, "subject_type": subject,
        "quality_tier": quality, "face_limit": face, "size": size,
        "parts": parts or [], "concept": concept, "face_sketch": face_sketch,
    })


# ---------------------------------------------------------------- 2. hero
a("hero", "hero",
  "The Warden, the player's champion: a young knight-commander in plated armor with a "
  "short blue tabard, a large round pauldron on each shoulder, an open-faced helm with a "
  "small crest, a longsword on the hip and a kite shield on the back. Confident stance. "
  "Keep the armor mostly light grey and white with small gold trim, neutral base colors.",
  "biped", "high_quality", 6000, "5.6 x 4.5", HUMANOID)

# ---------------------------------------------------------------- 3. towers
TOWERS = [
    ("archer", "Archer", "6.2 x 4.0", "biped", "balanced",
     "Forest ranger archer in a deep green hood and leather armor with bronze trim, "
     "longbow in the left hand, quiver of fletched arrows on the back, short green cape, alert stance."),
    ("crossbowman", "Crossbowman", "5.7 x 4.6", "biped", "balanced",
     "Stocky crossbowman in a steel cap and padded gambeson, holding a heavy dwarf-forged "
     "arbalest with a crank winch, bolt case on the belt, thick forearms."),
    ("hoplite", "Hoplite", "6.5 x 4.4", "biped", "balanced",
     "Bronze-clad spearman from a sun-baked southern city-state: crested bronze helm, round "
     "bronze shield with a sun motif, long spear, red cloak and greaves."),
    ("mortar", "Mortar", "4.2 x 5.2", "other", "balanced",
     "Squat siege mortar on a round wooden turntable base, fat black-iron barrel angled upward, "
     "brass bands, a small stack of round shells and a powder keg beside it.",
     ["Turret", "Barrel"]),
    ("great_cannon", "Great Cannon", "3.0 x 7.2 long", "other", "balanced",
     "Huge royal bronze cannon on a low reinforced wooden carriage with iron-banded wheels, "
     "long barrel with a lion-mouth muzzle (generic, not an emblem), rammer leaning on the side.",
     ["Turret", "Barrel"]),
    ("rocket_battery", "Rocket Battery", "4.3 x 4.2", "other", "balanced",
     "Ramshackle tinker-guild rocket launcher: a rack of six striped rockets on a swiveling "
     "wooden frame, copper pipes, gauges, a small boiler, smoke-stained metal.",
     ["Turret"]),
    ("arcantech_commando", "Runegunner", "5.6 x 4.6", "biped", "balanced",
     "Elite rifleman in dark blue leather and steel, holding a long rifle etched with glowing "
     "cyan runes and a crystal cartridge magazine, goggles pushed up on the helmet."),
    ("astrapomancer", "Stormcaller", "7.5 x 3.6", "biped", "balanced",
     "Old hermit storm mage with a very long white beard crackling with blue sparks, grey-blue "
     "robes, tall gnarled staff topped with a caged lightning orb, wild hair."),
    ("magei", "Archmage", "6.9 x 4.3", "biped", "balanced",
     "Arch-wizard in rich violet and gold robes with a tall pointed collar, floating open "
     "spellbook at the side, ornate staff with a large amethyst, scholarly and imperious."),
    ("alchemist", "Alchemist", "7.5 x 3.6", "biped", "balanced",
     "Eccentric alchemist with a soot-smudged apron over brown robes, goggles, a bandolier of "
     "bubbling colored potion flasks, holding a smoking green flask overhead."),
    ("aquamancer", "Tidecaller", "6.1 x 4.4", "biped", "balanced",
     "Sea priestess in flowing teal and pearl-white robes, a coral and shell crown, holding a "
     "trident-staff, a swirl of water rising around her lower body."),
    ("stardaughter", "Starwarden", "6.7 x 4.3", "biped", "balanced",
     "Graceful celestial archer in midnight-blue and silver armor sprinkled with tiny glowing "
     "stars, crescent-moon bow, long flowing hair, faint starlight glow."),
    ("oathsworn_revenant", "Deathbound Revenant", "6.9 x 6.7", "biped", "high_quality",
     "Fallen knight in cracked black plate with a tattered dark-red tabard, pale ghostly blue "
     "light leaking from the visor and the armor cracks, huge two-handed greatsword."),
    ("cleric", "Cleric", "6.2 x 3.6", "biped", "balanced",
     "Gentle temple sister in white and pale gold robes with a hood, holding a lantern-topped "
     "staff that glows warm yellow, a small holy book on the belt."),
    ("paladin", "Paladin", "6.8 x 6.3", "biped", "high_quality",
     "Holy knight in polished silver and gold plate with a white tabard bearing a simple "
     "sunburst, large warhammer, glowing golden halo behind the helm."),
    ("grove_warden", "Grovekeeper", "7.3 x 6.3", "biped", "high_quality",
     "Ancient walking tree-spirit: bark body, mossy shoulders, leafy crown, glowing amber eyes, "
     "root-like feet, small flowers and mushrooms growing on it, kindly."),
    ("siphoner", "Soulsiphon", "6.0 x 3.7", "biped", "balanced",
     "Gaunt blood-hermit in dark crimson hooded robes, pale hands, a curved ritual dagger, a "
     "floating red orb of drawn life essence above one palm."),
    ("augur_solis", "Eye of Aurion", "9.3 x 5.2", "other", "high_quality",
     "Sacred sun monument: a carved white-stone pedestal with gold filigree, holding a giant "
     "floating golden eye made of light and sun rays. Divine and serene, not creepy.",
     ["Eye"]),
    ("gold_mine", "Gold Mine", "4.0 x 6.7", "other", "balanced",
     "Small dwarven mine entrance cut into a rocky mound, timber supports, a lantern, a mine-cart "
     "full of gold nuggets on short rails.", ["Cart"]),
    ("farm", "Farm", "3.6 x 5.8", "other", "balanced",
     "Tiny farmstead plot: a little thatched shed, wheat sheaves, a fenced vegetable patch, a "
     "scarecrow and sacks of grain."),
    ("tax_collector", "(reserved tower)", "6.3 x 4.4", "biped", "balanced",
     "Pompous royal tax collector in a red velvet coat with fur trim, a ledger and quill, a "
     "heavy coin purse, a feathered hat."),
]
for row in TOWERS:
    id_, name, size, subject, quality, prompt = row[0], row[1], row[2], row[3], row[4], row[5]
    parts = row[6] if len(row) > 6 else (HUMANOID if subject == "biped" else [])
    a(id_, "tower", prompt, subject, quality, 6000, size, parts)

# ---------------------------------------------------------------- barracks camps
CAMP_BASE = ("small military camp: a pitched canvas tent, a weapon rack, a wooden palisade "
             "corner, a training dummy, and a tall banner pole")
CAMPS = [
    ("barracks_footman", "blue banner, cream canvas, simple swords and round shields"),
    ("barracks_knight", "blue banner, blue canvas, lances and kite shields"),
    ("barracks_berserker", "blood-red banner, hide-and-leather tent, axes, a snowy pelt"),
    ("barracks_defender", "gold banner, steel-grey canvas, tower shields stacked in a wall"),
    ("barracks_dreamknight", "violet banner, deep purple canvas, floating purple motes"),
    ("barracks_king", "gold banner, red-and-gold royal pavilion, a small throne"),
]
for cid, colors in CAMPS:
    a(cid, "barracks_camp", f"{CAMP_BASE}, {colors}.", "other", "balanced", 6000,
      "5.6 x 5.3", ["Banner"])
a("barracks_golem", "barracks_camp",
  "No tent: a carved rune circle with standing stones, glowing blue runes, 3.3 tall and 5.8 wide.",
  "other", "balanced", 6000, "3.3 x 5.8", ["Banner"])

# ---------------------------------------------------------------- barracks units
UNITS = [
    ("unit_footman", "4.5 x 3.2", "balanced",
     "Militia footman in a padded jerkin and kettle helm, short sword and round wooden shield; humble farmhand look."),
    ("unit_knight", "5.5 x 4.2", "balanced",
     "Knight in full blue-enameled plate with a closed helm, kite shield and arming sword."),
    ("unit_berserker", "5.9 x 4.6", "balanced",
     "Bare-chested northern clansman with a fur mantle, war paint, braided beard and two axes, roaring."),
    ("unit_defender", "5.4 x 5.4", "balanced",
     "Heavy guard with a huge rectangular tower shield and a short spear, gold-trimmed steel."),
    ("unit_golem", "6.8 x 6.8", "high_quality",
     "Rune-bound stone golem: boulder body, glowing blue runes, oversized fists, moss on the shoulders."),
    ("unit_dreamknight", "5.5 x 4.7", "balanced",
     "Knight in dark purple armor with a swirling void-galaxy pattern on the cloak, a glowing violet blade."),
    ("unit_king", "6.6 x 6.0", "high_quality",
     "The High King in golden plate with a crown on the helm and a royal red cape, a great sword held high."),
]
for uid, size, quality, prompt in UNITS:
    a(uid, "barracks_unit", prompt, "biped", quality, 6000, size, HUMANOID)

# ---------------------------------------------------------------- enemies
a("dark_peasant", "enemy", "Hunched village cultist in a ragged brown smock with a pale grey hood, "
  "holding a pitchfork, a glowing green eye symbol painted on the chest.", "biped", "balanced", 6000,
  "5.2 x 3.1", HUMANOID)
a("lurker", "enemy", "Low four-legged shadow creature like a lean hound made of smoke and black chitin, "
  "glowing violet eyes, crawling pose.", "quadruped", "balanced", 6000, "3.0 x 5.0 long",
  ["LegL", "LegR", "LegL2", "LegR2"])
a("dreadbat", "enemy", "Giant dusky purple bat with torn wings, glowing red eyes, fangs, wings fully "
  "spread (flying pose).", "other", "balanced", 6000, "2.0 x 7.0 wingspan", ["WingL", "WingR"])
a("risen_corpse", "enemy", "Shambling barrow zombie in rotting burial wraps and rusty armor scraps, "
  "grey-green skin, arms reaching forward.", "biped", "balanced", 6000, "5.0 x 3.2", HUMANOID)
a("bloated_corpse", "enemy", "Grotesquely swollen stitched undead with a huge belly, glowing green "
  "pustules, short legs, comical and gross but not gory.", "biped", "balanced", 6000, "6.9 x 5.7", HUMANOID)
a("wight", "enemy", "Skeletal barrow-knight in a rusted helm and torn cloak, sprinting pose, cold blue "
  "eye-light, notched sword.", "biped", "balanced", 6000, "4.6 x 2.7", HUMANOID)
a("spectral_wight", "enemy", "Translucent pale-cyan ghost knight with no legs (fading wisp tail), "
  "floating, armor outline only.", "biped", "balanced", 6000, "5.3 x 3.7", ["Body", "Head", "ArmL", "ArmR"])
a("necromancer", "enemy", "Gaunt necromancer in black and bone-white robes with a skull-topped staff and "
  "green soul flames swirling around the hands.", "biped", "balanced", 6000, "6.2 x 4.5", HUMANOID)
a("dark_prophet", "enemy", "Tall doom preacher in tattered grey robes and a tall mitre-like hood, holding "
  "a dark book chained to his wrist, pale green halo of doom.", "biped", "balanced", 6000, "7.0 x 5.1", HUMANOID)
a("gronnling", "enemy", "Burly hill ogre mercenary with grey-brown skin, underbite tusks, a fur loincloth "
  "and a big wooden club.", "biped", "balanced", 6000, "5.3 x 5.3", HUMANOID)
a("gronn", "enemy", "Massive ogre warlord with iron shoulder plates, a belt made of captured shields, a "
  "spiked iron club, a scarred face. Twice the bulk of a hill ogre.", "biped", "high_quality", 8000,
  "11.5 x 11.5", HUMANOID)
a("protodrake", "enemy", "Young fire drake with dark red-orange scales, glowing ember cracks, horned head, "
  "wings spread in flight, long tail.", "other", "high_quality", 9000, "4.5 x 13.2 wingspan", ["WingL", "WingR"])
a("wraith_witch", "enemy", "Screaming spectral witch with long flowing white hair, tattered grey-violet "
  "dress fading into mist, floating.", "biped", "balanced", 6000, "6.0 x 5.1", ["Body", "Head", "ArmL", "ArmR"])
a("wraith_lord", "enemy", "Floating hooded knight in cursed black plate with icy blue eye glow, a "
  "frost-rimed greatsword, no visible legs.", "biped", "balanced", 6000, "6.2 x 5.1", ["Body", "Head", "ArmL", "ArmR"])
a("summoner", "enemy", "Towering rift-priest in deep violet robes with a ring of floating stone shards and "
  "a swirling purple portal disc behind him.", "biped", "high_quality", 9000, "10.1 x 7.2", HUMANOID)
a("spawn_of_helloc", "enemy", "Hunched lesser demon with charred black-red skin, glowing sickly-green "
  "cracks, small horns, clawed hands.", "biped", "high_quality", 8000, "8.2 x 7.1", HUMANOID)
a("moloc", "boss", "Colossal winged demon general with heavy black-iron armor, a huge cleaver, a horned "
  "skull-like helm and leathery wings. Ruinous and towering.", "biped", "high_quality", 15000, "16.4 x 21.3",
  HUMANOID + ["WingL", "WingR"])
a("helloc", "boss", "Final demon lord: enormous, horned, red-black skin with bright gold and sickly-green "
  "glowing rune markings for contrast, huge wings, a flaming gate-key staff, a burning aura ring at the feet. "
  "Must read clearly against a dark red lava map.", "biped", "high_quality", 15000, "20.7 x 26.6",
  HUMANOID + ["WingL", "WingR", "Aura"])
a("korlash", "boss", "Giant sea leviathan rising from water: a domed armored head with glowing teal eyes and "
  "eight thick tentacles spread around it, barnacles, deep blue-green.", "other", "high_quality", 15000,
  "9.1 x 17.3", ["T0", "T1", "T2", "T3", "T4", "T5", "T6", "T7"])

# ---------------------------------------------------------------- 5. props
PROPS = [
    ("castle_gate", "16 x 16", "The player's keep gate: twin round stone towers with blue conical roofs, a "
     "big wooden portcullis gate between them, gold banners, crenellations. Proud and friendly."),
    ("spawn_portal", "11 x 10.5", "Menacing enemy spawn portal: a ring of jagged black standing stones around "
     "a swirling purple-green vortex disc, cracked earth."),
    ("tree_oak", "8 x 6.3", "Round leafy oak tree, chunky trunk, puffy faceted canopy."),
    ("tree_pine", "7.3 x 5", "Tall layered pine tree, stylized tiers."),
    ("tree_pine_snow", "7.3 x 5", "Tall layered stylized pine tree with thick snow caps on each tier."),
    ("tree_palm", "7.5 x 6.2", "Curved desert palm with broad fronds and coconuts."),
    ("tree_dead", "5.7 x 4.2", "Twisted leafless dead tree, grey-black bark."),
    ("tree_willow", "6.5 x 5.1", "Drooping swamp willow, mossy, hanging curtains of leaves."),
    ("bush", "1.8 x 3.4", "Round leafy shrub."),
    ("palm_bush", "1.1 x 3.1", "Low spiky desert fern bush."),
    ("rock_a", "2 x 3", "Faceted grey boulder, chunky stylized rock."),
    ("rock_b", "2 x 3", "Faceted grey boulder, wider variant with a flat top."),
    ("rock_snow", "2.1 x 3.8", "Grey boulder with a snow cap."),
    ("rock_sand", "2.9 x 5.3", "Wind-worn sandstone rock, layered orange bands."),
    ("rock_lava", "2.3 x 3.6", "Black volcanic rock with glowing orange cracks."),
    ("crystal_blue", "4 x 2.5", "Cluster of tall glowing blue crystals."),
    ("crystal_pink", "4 x 2.5", "Cluster of tall glowing pink crystals."),
    ("crystal_green", "4 x 2.5", "Cluster of tall glowing green crystals."),
    ("house", "7.4 x 6.8", "Cozy timber-frame village cottage with a red tiled roof and a chimney."),
    ("house_tower", "12.5 x 6.4", "Village watchtower with a stone base, timber top and a pointed roof."),
    ("desert_tent", "3.9 x 6", "Striped desert merchant tent with rugs and pots."),
    ("pillar", "7 x 2-4", "White marble temple column with a simple capital."),
    ("pillar_broken", "3.5 x 2-4", "Broken white marble temple column lying in pieces."),
    ("stone_arch", "7.2 x 9", "Ancient marble archway with worn carvings."),
    ("brazier", "3.8 x 1.8", "Iron brazier with a warm orange flame."),
    ("fel_brazier", "5.3 x 1.9", "Spiky black-iron brazier with a sickly green demonic flame."),
    ("obelisk", "7.3 x 2.4", "Black stone obelisk with glowing red runes."),
    ("mushroom", "1.6 x 2.4", "Cluster of glowing cave mushrooms."),
    ("cactus", "3.6 x 2.5", "Saguaro-style cactus with two arms."),
    ("bones", "0.7 x 2.3", "Scattered bleached bones and a skull, lying flat."),
    ("fence", "1.6 x 4.6", "Short rustic wooden fence section."),
    ("ice_spike", "4.7 x 2.2", "Jagged blue ice spire."),
    ("reeds", "2.8 x 1.6", "Clump of swamp reeds and cattails."),
    ("banner_pole", "6 x 1.7", "Wooden pole with a hanging blue and gold cloth banner."),
    ("lava_pool", "1.8 x 7.4", "Shallow bubbling lava pool with a black rock rim."),
]
PROP_PARTS = {
    "castle_gate": [], "spawn_portal": ["Swirl"], "brazier": ["Flame"], "fel_brazier": ["Flame"],
}
for pid, size, prompt in PROPS:
    a(pid, "prop", prompt, "other", "fast", 1500, size, PROP_PARTS.get(pid, []))

# crop the doc's per-asset size suffix like "5.6 x 4.5" already stored
images = [
    {"id": "key_art", "size": "1920x1080", "ratio": "16:9", "transparent": False,
     "prompt": "Epic key art: a blue-and-gold knight Warden on a hill at dusk, defending a castle gate, "
               "with archers and mages on the walls; below, a pale undead horde with green cult banners "
               "marches along a winding road toward the gate. A huge horned demon silhouette looms in a red "
               "sky far behind. Painterly, heroic, wide composition with an empty top-center area for the logo."},
    {"id": "logo", "size": "1600x600", "ratio": "8:3", "transparent": True,
     "prompt": "Game logo reading REALM WARDENS in carved gold fantasy capitals with a stone-and-steel bevel, "
               "a small sword and shield crest behind it, transparent background."},
]
MAPS = [
    ("meadows", "a green river village with red-roof cottages"),
    ("oasis", "a sandstone desert spring with palms"),
    ("fjord", "frozen glacial switchbacks above a frozen sea"),
    ("caverns", "a dark crystal cave with violet and cyan crystals"),
    ("marrowfen", "a foggy rotting swamp with two causeways"),
    ("requiem", "a moonlit white-marble necropolis"),
    ("ashengate", "burning lava steppes before a giant demon gate"),
]
for mid, desc in MAPS:
    images.append({"id": f"map_{mid}", "size": "800x450", "ratio": "16:9", "transparent": False,
                   "prompt": f"Map card illustration, top-down three-quarter view of a winding road through "
                             f"{desc}, stylized hand-painted fantasy game art, chunky readable shapes, "
                             f"warm saturated palette, no text."})
BADGES = [
    ("first_watch", "a single torch"), ("unbroken_wall", "an intact shield wall"),
    ("warden_five_roads", "five crossing roads"), ("iron_resolve", "an iron fist"),
    ("legend_elderhold", "a laurel crown"), ("long_night", "a moon over a watchtower"),
    ("challenger", "crossed swords"), ("master_trials", "a trophy"),
    ("ten_thousand_fallen", "a skull pile"), ("devoted", "a sunrise calendar"),
]
for bid, motif in BADGES:
    images.append({"id": f"badge_{bid}", "size": "256x256", "ratio": "1:1", "transparent": True,
                   "prompt": f"Round bronze medallion achievement badge featuring {motif}, carved metal, "
                             f"chunky fantasy game icon, centered, transparent background, no text."})

out = {
    "version": 1,
    "style_block": STYLE,
    "negative_block": NEG[:255],
    "negative_full": NEG,
    "add3d_block": ADD3D,
    "assets": assets,
    "images": images,
}

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dest = os.path.join(root, "docs", "realm-wardens", "manifest.json")
os.makedirs(os.path.dirname(dest), exist_ok=True)
with open(dest, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"assets={len(assets)} images={len(images)} -> {dest}")
print("groups:", {g: sum(1 for x in assets if x['group'] == g) for g in sorted({x['group'] for x in assets})})
