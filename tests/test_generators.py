"""Contract tests for every generator module and for the build's manifest."""
import inspect
import json
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import generators
from build import GROUP_DESCRIPTIONS

MODS = generators.discover()
# The instrument kits added as motif categories: each ships exactly 25 sounds.
MOTIF_KITS = ("guitar", "ebass", "piano", "epiano", "strings",
              "mallets", "harp", "organ", "choir", "flute")


class TestDiscovery(unittest.TestCase):
    def test_finds_every_module_that_declares_a_category(self):
        files = {f[:-3] for f in os.listdir(os.path.join(ROOT, "generators"))
                 if f.endswith(".py") and not f.startswith("_")}
        self.assertEqual({m.__name__.split(".")[-1] for m in MODS}, files)

    def test_skips_private_modules(self):
        # _music.py is shared machinery, not a category
        self.assertNotIn("_music", [m.__name__.split(".")[-1] for m in MODS])
        self.assertTrue(os.path.exists(os.path.join(ROOT, "generators", "_music.py")))

    def test_is_sorted_by_category(self):
        cats = [m.CATEGORY for m in MODS]
        self.assertEqual(cats, sorted(cats))

    def test_every_motif_kit_is_present(self):
        cats = {m.CATEGORY for m in MODS}
        for kit in MOTIF_KITS:
            self.assertIn(kit, cats)


class TestModuleContract(unittest.TestCase):
    def test_declares_the_required_attributes(self):
        for m in MODS:
            with self.subTest(module=m.CATEGORY):
                self.assertIsInstance(m.CATEGORY, str)
                self.assertIsInstance(m.DESCRIPTION, str)
                self.assertIn(m.GROUP, GROUP_DESCRIPTIONS)
                self.assertTrue(m.__doc__, "module needs a docstring")

    def test_category_is_a_safe_folder_name(self):
        for m in MODS:
            with self.subTest(module=m.CATEGORY):
                self.assertRegex(m.CATEGORY, r"^[a-z][a-z0-9_]*$")

    def test_sounds_entries_are_well_formed(self):
        for m in MODS:
            for entry in m.SOUNDS:
                with self.subTest(module=m.CATEGORY, entry=entry[0]):
                    self.assertEqual(len(entry), 3)
                    name, desc, fn = entry
                    self.assertRegex(name, r"^[a-z][a-z0-9_]*$")
                    self.assertTrue(desc.strip())
                    self.assertTrue(callable(fn))
                    self.assertNotEqual(getattr(fn, "__name__", ""), "<lambda>")

    def test_motif_kit_sounds_are_documented(self):
        """`build.py --list` prints the SOUNDS blurb, but the docstring is what
        a reader of the module sees; the instrument kits carry both."""
        for m in MODS:
            if m.CATEGORY not in MOTIF_KITS and m.CATEGORY != "brass":
                continue
            for name, _, fn in m.SOUNDS:
                with self.subTest(module=m.CATEGORY, sound=name):
                    self.assertTrue(fn.__doc__, "%s needs a docstring" % name)

    def test_sound_names_are_unique_within_a_category(self):
        for m in MODS:
            names = [n for n, _, _ in m.SOUNDS]
            with self.subTest(module=m.CATEGORY):
                self.assertEqual(len(names), len(set(names)))

    def test_sound_names_are_unique_across_the_whole_pack(self):
        seen = {}
        for m in MODS:
            for name, _, _ in m.SOUNDS:
                self.assertNotIn(name, seen,
                                 "%s appears in %s and %s" % (name, seen.get(name),
                                                              m.CATEGORY))
                seen[name] = m.CATEGORY

    def test_motif_kit_names_are_prefixed_with_their_category(self):
        for m in MODS:
            if m.CATEGORY not in MOTIF_KITS and m.CATEGORY != "brass":
                continue
            for name, _, _ in m.SOUNDS:
                with self.subTest(module=m.CATEGORY, sound=name):
                    self.assertTrue(name.startswith(m.CATEGORY + "_"))

    def test_each_motif_kit_ships_exactly_25_sounds(self):
        for m in MODS:
            if m.CATEGORY in MOTIF_KITS:
                with self.subTest(module=m.CATEGORY):
                    self.assertEqual(len(m.SOUNDS), 25)

    def test_no_dead_generator_functions(self):
        """Every public sound function is registered in SOUNDS.

        Compared against fn.__name__, not the registered name: the two are
        allowed to differ (typing registers space_bar as "space"), and the
        older modules do not prefix their functions with the category.
        """
        for m in MODS:
            src = inspect.getsource(m)
            defined = {d for d in re.findall(r"^def (\w+)", src, re.M)
                       if not d.startswith("_")}
            built = {fn.__name__ for _, _, fn in m.SOUNDS}
            with self.subTest(module=m.CATEGORY):
                self.assertEqual(defined - built, set(), "defined but never built")
                self.assertEqual(built - defined, set(), "built but not defined here")


class TestManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "output", "manifest.json")
        if not os.path.exists(path):
            raise unittest.SkipTest("run build.py first")
        with open(path) as f:
            cls.man = json.load(f)

    def test_sample_rate_is_44100(self):
        self.assertEqual(self.man["sample_rate"], 44100)

    def test_total_matches_the_sum_of_its_parts(self):
        total = sum(len(c["sounds"]) for g in self.man["groups"]
                    for c in g["categories"])
        self.assertEqual(self.man["total_sounds"], total)

    def test_lists_every_discovered_category(self):
        listed = {c["name"] for g in self.man["groups"] for c in g["categories"]}
        self.assertEqual(listed, {m.CATEGORY for m in MODS})

    def test_categories_are_sorted_within_each_group(self):
        for g in self.man["groups"]:
            names = [c["name"] for c in g["categories"]]
            self.assertEqual(names, sorted(names))

    def test_every_referenced_file_exists(self):
        for g in self.man["groups"]:
            for c in g["categories"]:
                for s in c["sounds"]:
                    p = os.path.join(ROOT, s["files"]["wav"])
                    with self.subTest(sound=s["name"]):
                        self.assertTrue(os.path.exists(p), p)

    def test_durations_are_present_and_sane(self):
        for g in self.man["groups"]:
            for c in g["categories"]:
                for s in c["sounds"]:
                    with self.subTest(sound=s["name"]):
                        self.assertGreater(s["duration_s"], 0.0)
                        self.assertLess(s["duration_s"], 5.0)


if __name__ == "__main__":
    unittest.main()
