import os
import json
import requests
from pyaxmlparser import APK
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup


class GLOBAL:
    ARCHIVE_DIR = "/home/anfreire/Documents/Archive/updateMe"
    INDEX_PATH = ARCHIVE_DIR + "/index.json"


class DIRS:
    YOUTUBE = GLOBAL.ARCHIVE_DIR + "/youtube"
    SPOTIFY = GLOBAL.ARCHIVE_DIR + "/spotify"
    HDO = GLOBAL.ARCHIVE_DIR + "/hdo"


class MACROS:
    SPOTIFY = "SPOTIFY"
    HDO = "HDO"
    YOUTUBE = "YOUTUBE_YOUTUBE"
    YOUTUBE_MUSIC = "YOUTUBE_MUSIC"
    YOUTUBE_MICROG = "YOUTUBE_MICROG"


PATHS = {
    MACROS.SPOTIFY: DIRS.SPOTIFY + "/spotify.apk",
    MACROS.HDO: DIRS.HDO + "/hdo.apk",
    MACROS.YOUTUBE: DIRS.YOUTUBE + "/youtube.apk",
    MACROS.YOUTUBE_MUSIC: DIRS.YOUTUBE + "/youtube_music.apk",
    MACROS.YOUTUBE_MICROG: DIRS.YOUTUBE + "/micro_g.apk",
}


class AppBase:
    def __init__(self, macro: str):
        if macro not in PATHS.keys():
            raise ValueError(f"Macro {macro} not found in PATHS")
        self.macro = macro
        self.path = PATHS[macro]

    def update_apk(self, url: str):
        if url is None:
            raise ValueError("No url provided")
        r = requests.get(url)
        with open(PATHS[self.macro], "wb") as apk:
            apk.write(r.content)

    def update_version(self, url: str):
        index = None
        with open(GLOBAL.INDEX_PATH, "r") as index_file:
            index = json.load(index_file)
        apk = APK(PATHS[self.macro])
        new_version = apk.version_name
        old_version = new_version
        try:
            old_version = index[apk.package]["versions"]["new"]
        except:
            pass
        new_link = url
        old_link = new_link
        try:
            old_link = index[apk.package]["links"]["new"]
        except:
            pass
        index[apk.package] = {
            "versions": {"old": old_version, "new": new_version},
            "links": {"old": old_link, "new": new_link},
        }
        index_dump = json.dumps(index)
        with open(GLOBAL.INDEX_PATH, "w") as index_file:
            index_file.write(index_dump)
        os.remove(PATHS[self.macro])


GITHUB_DATA = {
    MACROS.YOUTUBE_MICROG: {"user": "TeamVanced", "repo": "VancedMicroG"},
    MACROS.YOUTUBE: {"user": "j-hc", "repo": "revanced-magisk-module"},
    MACROS.YOUTUBE_MUSIC: {"user": "j-hc", "repo": "revanced-magisk-module"},
}


class GithubScrapping:
    def __init__(self, user: str, repo: str):
        self.user = user
        self.repo = repo

    @property
    def prefix(self):
        return f"https://github.com/{self.user}/{self.repo}"

    def getVersions(self) -> list:
        page = urlopen(f"{self.prefix}/releases")
        soup = BeautifulSoup(page, "html.parser")
        divs = soup.find_all("div")
        versions = list()
        for div in divs:
            if div.find("svg", attrs={"aria-label": "Tag"}) and div.find("span"):
                try:
                    text = div.find("span").text
                    text = re.sub(r"\s+", "", text)
                    if (
                        text == self.user
                        or text == self.repo
                        or text is None
                        or len(text) == 0
                        or text in versions
                    ):
                        continue
                    versions.append(text)
                except:
                    continue
        return versions

    def link(self, version: str, terms: list) -> list:
        page = urlopen(
            f"https://github.com/{self.user}/{self.repo}/releases/expanded_assets/{version}"
        )
        soup = BeautifulSoup(page, "html.parser")
        lis = soup.find_all("li")
        links = []
        for li in lis:
            div = li.find("div")
            if div and div.find("svg") and div.find("a"):
                href = div.find("a").get("href")
                if href and len(href) != 0 and all(term in href for term in terms):
                    link = (
                        href
                        if href.startswith("https://")
                        else "https://github.com/" + href
                    )
                    if link not in links:
                        links.append(link)
        return links


def getUrl():
    microG = GithubScrapping(
        GITHUB_DATA[MACROS.YOUTUBE]["user"],
        GITHUB_DATA[MACROS.YOUTUBE]["repo"],
    )
    print(microG.link(microG.getVersions()[0], [".apk", "music"]))


def updateHDO():
    link = "https://hdo.app/download"
    hdo = AppBase(MACROS.HDO)
    hdo.update_apk(link)
    hdo.update_version(link)


def updateMicroG():
    scrapper = GithubScrapping(
        GITHUB_DATA[MACROS.YOUTUBE_MICROG]["user"],
        GITHUB_DATA[MACROS.YOUTUBE_MICROG]["repo"],
    )
    latest = scrapper.getVersions()[0]
    link = scrapper.link(latest, [".apk"])[0]
    microG = AppBase(MACROS.YOUTUBE_MICROG)
    microG.update_apk(link)
    microG.update_version(link)


def updateYoutube():
    scrapper = GithubScrapping(
        GITHUB_DATA[MACROS.YOUTUBE]["user"],
        GITHUB_DATA[MACROS.YOUTUBE]["repo"],
    )
    versions = scrapper.getVersions()
    index = 0
    link = None
    while link is None and index < len(versions):
        links = scrapper.link(versions[index], [".apk", "youtube"])
        for _ in links:
            if "extended" in _ or "arm-v7a" in _:
                continue
            link = _
            break
        index += 1
    youtube = AppBase(MACROS.YOUTUBE)
    youtube.update_apk(link)
    youtube.update_version(link)


def updateYoutubeMusic():
    scrapper = GithubScrapping(
        GITHUB_DATA[MACROS.YOUTUBE_MUSIC]["user"],
        GITHUB_DATA[MACROS.YOUTUBE_MUSIC]["repo"],
    )
    versions = scrapper.getVersions()
    index = 0
    link = None
    while link is None and index < len(versions):
        links = scrapper.link(versions[index], [".apk", "music"])
        for _ in links:
            if "extended" in _ or "arm-v7a" in _:
                continue
            link = _
            break
        index += 1
    youtube = AppBase(MACROS.YOUTUBE_MUSIC)
    youtube.update_apk(link)
    youtube.update_version(link)


def main():
    updateHDO()
    updateMicroG()
    updateYoutube()
    updateYoutubeMusic()


if __name__ == "__main__":
    main()
