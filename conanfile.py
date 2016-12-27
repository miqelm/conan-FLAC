from conans import ConanFile, os, ConfigureEnvironment
from conans.tools import download, unzip, replace_in_file
import os, subprocess

class FLACConan(ConanFile):
    name = "FLAC"
    version = "1.3.1"
    ZIP_FOLDER_NAME = "%s-%s" % (name.lower(), version)
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    requires = "ogg/1.3.2@coding3d/stable"
    license="BSD"
    exports = "*"
    url = "https://github.com/Outurnate/conan-packages/tree/master/FLAC"

    def source(self):
        zip_name = "%s.tar.xz" % self.ZIP_FOLDER_NAME
        download("http://downloads.xiph.org/releases/flac/%s" % zip_name, zip_name)
        self.run("xz -d %s" % zip_name)
        self.run("gzip -1 %s" % zip_name.replace(".xz", ""))
        unzip(zip_name.replace(".xz", ".gz"))
        os.unlink(zip_name.replace(".xz", ".gz"))

    def build(self):
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        cd_build = "cd %s" % self.ZIP_FOLDER_NAME

        if self.settings.os == "Windows":
            env_line = env.command_line

            if self.options.shared:
                ms_project = "libFLAC_dynamic"
            else:
                ms_project = "libFLAC_static"

            self.run("%s && %s && devenv FLAC.sln /upgrade" % (env_line, cd_build))
            platform = "Win32" if self.settings.arch == "x86" else "x64"
            self.run("%s && %s && msbuild FLAC.sln /t:%s /p:BuildProjectReferences=true /property:Configuration=%s /property:Platform=%s" % (env_line, cd_build, ms_project, self.settings.build_type, platform))
        else:
            debug = " -ggdb3 " if self.settings.build_type == "Debug" else ""
            
            if self.options.fPIC:
                env_line = env.command_line.replace('CFLAGS="', 'CFLAGS="-fPIC ')
            else:
                env_line = env.command_line
            env_line = env_line.replace('CFLAGS="',   'CFLAGS="%s ' %   debug)
            env_line = env_line.replace('CXXFLAGS="', 'CXXFLAGS="%s ' % debug)
            env_line = env_line.replace('LDFLAGS="',  'LDFLAGS="%s ' %  debug)
            
            # TODO SHARED

            arch = '--host=i686-pc-linux-gnu "CFLAGS=-m32" "CXXFLAGS=-m32" "LDFLAGS=-m32"' if self.settings.arch == "x86" else ""
            m32_pref = "setarch i386" if self.settings.arch == "x86" else ""
            self.run('mkdir -p install && %s && chmod +x ./configure && %s %s ./configure --prefix=$(pwd)/../install' % (cd_build, env_line, m32_pref))
            self.run("%s && %s make install" % (cd_build, env_line))

    def package(self):
        self.copy("FindFLAC.cmake", ".", ".")
        self.copy("include/FLAC/*.h", dst=".", src=self.ZIP_FOLDER_NAME, keep_path=True)
        self.copy("include/FLAC++/*.h", dst=".", src=self.ZIP_FOLDER_NAME, keep_path=True)
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
        else:
            if self.options.shared:
                if self.settings.os == "Macos":
                    self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                else:
                    self.copy(pattern="*.so*", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["FLAC", "FLAC++"]
