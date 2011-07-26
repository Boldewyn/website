

import unittest
import os
import tempfile
import shutil
from website._webtools.bootstrap import bootstrap
from website._webtools.build import build


class BootstrapTestCase(unittest.TestCase):
    """Test various bootstrapping scenarios"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.baseConfig = {
          "URL": "localhost",
          "TITLE": "Example",
          "DEFAULTS": {
              "AUTHOR": "John Doe",
          }
        }

    def test_existing_empty_target(self):
        """Bootstrap in an existing empty target"""
        os.mkdir(os.path.join(self.tmpdir, "empty_target"))
        bootstrap(os.path.join(self.tmpdir, "empty_target"), {})

    def test_existing_nonempty_target(self):
        """Bootstrap in an existing non-empty target"""
        os.mkdir(os.path.join(self.tmpdir, "nonempty_target"))
        open(os.path.join(self.tmpdir, "nonempty_target/x"), 'w').close()
        self.assertRaises(ValueError, bootstrap, os.path.join(self.tmpdir, "nonempty_target"), {})

    def test_noconf(self):
        """Bootstrap with empty config"""
        bootstrap(os.path.join(self.tmpdir, "noconf"), None)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "noconf/_config.py")))

    def test_minimal(self):
        """Bootstrap with a minimal config"""
        bootstrap(os.path.join(self.tmpdir, "minimal"), self.baseConfig)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "minimal/_config.py")))

    def test_usual(self):
        """Test with all usual config options set"""
        cfg = self.baseConfig
        cfg["EMAIL"] = "info@localhost"
        cfg["LANGUAGE"] = "en"
        cfg["DISQUS_NAME"] = "__test__"
        bootstrap(os.path.join(self.tmpdir, "usual"), cfg)
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "usual/_config.py")))

    def test_in_docroot(self):
        """Bootstrap with URL path set to '/'"""
        bootstrap(os.path.join(self.tmpdir, "in_docroot"), {
          "URL": "localhost",
          "TITLE": "Example",
          "DEFAULTS": {
              "AUTHOR": "John Doe",
          }
        })
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "in_docroot/robots.txt")))
        self.assertTrue(os.path.isfile(os.path.join(self.tmpdir, "in_docroot/humans.txt")))

    def test_below_docroot(self):
        """Bootstrap with URL path set to '/foo/'"""
        bootstrap(os.path.join(self.tmpdir, "below_docroot"), {
          "URL": "localhost/foo/",
          "TITLE": "Example",
          "DEFAULTS": {
              "AUTHOR": "John Doe",
          }
        })
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, "below_docroot/robots.txt")))
        self.assertFalse(os.path.isfile(os.path.join(self.tmpdir, "below_docroot/humans.txt")))

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class BuildTestCase(unittest.TestCase):
    """Test, when the resulting web site is built"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmpdir)
        bootstrap(self.tmpdir, {
          "URL": "localhost",
          "TITLE": "Example",
          "DEFAULTS": {
              "AUTHOR": "John Doe",
          }
        })

    def test_initial_build(self):
        """Check, if building directly after bootstrap works"""
        build()

    def test_empty_build(self):
        """Check, if building w/o articles works"""
        shutil.rmtree(os.path.join(self.tmpdir, "_articles"))
        os.mkdir(os.path.join(self.tmpdir, "_articles"))
        build()

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

