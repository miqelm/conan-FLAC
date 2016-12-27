from conans import ConanFile, CMake
import os

# This easily allows to copy the package in other user or channel
channel = os.getenv("CONAN_CHANNEL", "testing")
username = os.getenv("CONAN_USERNAME", "demo")

class FLACReuseConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "FLAC/1.3.1@%s/%s" % (username, channel)

    def build(self):
        self.run('echo %s' % (self.conanfile_directory))

    def test(self):
        self.run('echo %s' % (self.conanfile_directory))

