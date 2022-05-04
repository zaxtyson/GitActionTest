import os
import re
import gzip
import tarfile
import subprocess
import hashlib
from datetime import datetime
from typing import Dict


class IndexUpdater:

    repo_base = "/www/wwwroot/repo.zaxtyson.cn"
    repo_debian = os.path.join(repo_base, "debian")
    repo_ubuntu = os.path.join(repo_base, "ubuntu")
    repo_centos = os.path.join(repo_base, "centos")
    repo_redhat = os.path.join(repo_base, "redhat")

    archs = ["amd64"]  # "i386", "arm64", "armhf"
    debian_dist_codes = ["stretch", "buster", "bullseye", "bookworm"]
    ubuntu_dist_codes = ["xenial", "bionic", "focal", "jammy"]

    def __init__(self) -> None:
        self.init_repos()

    def init_debian_repo(self):
        if os.path.exists(self.repo_debian):
            return
        print("Create repo for debian")
        os.makedirs(f"{self.repo_debian}/pool/main")
        for dist_code in self.debian_dist_codes:
            for arch in self.archs:
                os.makedirs(
                    f"{self.repo_debian}/dists/{dist_code}/main/binary-{arch}")

    def init_ubuntu_repo(self):
        if os.path.exists(self.repo_ubuntu):
            return
        print("Create repo for ubuntu")
        os.makedirs(f"{self.repo_ubuntu}/pool/main")
        for dist_code in self.ubuntu_dist_codes:
            for arch in self.archs:
                os.makedirs(
                    f"{self.repo_ubuntu}/dists/{dist_code}/main/binary-{arch}")

    def init_repos(self):
        self.init_debian_repo()
        self.init_ubuntu_repo()

    def get_packages_info(self, repo_path: str) -> Dict[str, str]:
        # if your host os is based on redhat
        # pelase exec `yum install dpkg-dev` before using `dpkg-scanpackages`
        packages_cmd = f"dpkg-scanpackages -m {repo_path}/pool/main"
        packages_info = subprocess.check_output(
            packages_cmd, shell=True).decode().split("\n\n")
        packages_info = filter(lambda x: x != "", packages_info)

        packages = {}  # (dist_code, arch): content
        for item in packages_info:
            r = re.search(r"Filename: .+?~(.+?)_(.+?)\.deb", item)
            dist_code, arch = r.group(1), r.group(2)
            key = (dist_code, arch)
            item = item.replace(f"{repo_path}/", "") + "\n\n"
            if not packages.get(key):
                packages[key] = item
            else:
                packages[key] += item
        return packages

    def write_packages_file(self, repo_path: str, dist_code: str, arch: str, content: str) -> None:
        package_file = f"{repo_path}/dists/{dist_code}/main/binary-{arch}/Packages"
        with open(package_file, "w") as f:
            f.write(content)
        print(f"Update {package_file}")

        package_file_gz = f"{package_file}.gz"
        with gzip.open(package_file_gz, "wt", compresslevel=9) as f:
            f.write(content)
        print(f"Update {package_file_gz}")

    @staticmethod
    def get_file_size(file_path: str) -> int:
        return os.path.getsize(file_path)

    @staticmethod
    def get_file_md5(file_path: str) -> str:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    @staticmethod
    def get_file_sha1(file_path: str) -> str:
        with open(file_path, "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()

    @staticmethod
    def get_file_sha256(file_path: str) -> str:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def write_release_file(self, repo_path: str, dist_code: str, arch: str) -> None:
        dist_path = f"{repo_path}/dists/{dist_code}"
        main_path = f"{dist_path}/main"
        now = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')  # rfc 2822
        content = f"""Origin: Deb Repository
Label: third-party
Suite: {dist_code}
Codename: {dist_code}
Version: 1.0
Architectures: {" ".join(self.archs)}
Components: main
Description: A third-party software repository maintained by zaxtyson
Date: {now}
"""
        content += "MD5Sum:\n"
        for dirpath, dirnames, filenames in os.walk(main_path):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                file_path_relative = file_path.replace(f"{dist_path}/", "")
                content += f" {self.get_file_md5(file_path)} {self.get_file_size(file_path)} {file_path_relative}\n"

        content += "SHA1:\n"
        for dirpath, dirnames, filenames in os.walk(main_path):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                file_path_relative = file_path.replace(f"{dist_path}/", "")
                content += f" {self.get_file_sha1(file_path)} {self.get_file_size(file_path)} {file_path_relative}\n"

        content += "SHA256:\n"
        for dirpath, dirnames, filenames in os.walk(main_path):
            for file in filenames:
                file_path = os.path.join(dirpath, file)
                file_path_relative = file_path.replace(f"{dist_path}/", "")
                content += f" {self.get_file_sha256(file_path)} {self.get_file_size(file_path)} {file_path_relative}\n"

        release_file = f"{repo_path}/dists/{dist_code}/Release"
        print(f"Update {release_file}")
        with open(release_file, "w") as f:
            f.write(content)

    def unzip_update_pkg(self, update_pkg: str) -> None:
        if not os.path.exists(update_pkg):
            raise FileNotFoundError("update package not found")

        with tarfile.open(update_pkg, "r:gz") as tar:
            tar.extractall(self.repo_base)

    def update_index(self, updpate_pkg: str) -> None:
        # Unzip
        self.unzip_update_pkg(updpate_pkg)

        # Debian
        packages = self.get_packages_info(self.repo_debian)
        for key, content in packages.items():
            dist_code, arch = key
            self.write_packages_file(
                self.repo_debian, dist_code, arch, content)
            self.write_release_file(self.repo_debian, dist_code, arch)

        # Ubuntu
        packages = self.get_packages_info(self.repo_ubuntu)
        for key, content in packages.items():
            dist_code, arch = key
            self.write_packages_file(
                self.repo_ubuntu, dist_code, arch, content)
            self.write_release_file(self.repo_ubuntu, dist_code, arch)


if __name__ == "__main__":
    updater = IndexUpdater()
    updater.update_index("/tmp/update.tar.gz")
