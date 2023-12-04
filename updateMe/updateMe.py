import os
import json
import requests
from pyaxmlparser import APK
import re
from urllib.request import urlopen
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class APKInfo:
    version: str
    link: str

    @property
    def toDict(self):
        return {"version": self.version, "link": self.link}

    def __eq__(self, other):
        return self.version == other.version and self.link == other.link


@dataclass
class AppInfo:
    package: str
    apkInfo: APKInfo

    @property
    def toDict(self):
        return {
            "package": self.package,
            "version": self.apkInfo.version,
            "link": self.apkInfo.link,
        }


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


class COLORS:
    RED: str = "\033[1;31m"
    GREEN: str = "\033[1;32m"
    YELLOW: str = "\033[1;33m"
    BLUE: str = "\033[1;34m"
    WHITE: str = "\033[1;37m"
    RESET: str = "\033[0;0m"


PATHS = {
    MACROS.SPOTIFY: DIRS.SPOTIFY + "/spotify.apk",
    MACROS.HDO: DIRS.HDO + "/hdo.apk",
    MACROS.YOUTUBE: DIRS.YOUTUBE + "/youtube.apk",
    MACROS.YOUTUBE_MUSIC: DIRS.YOUTUBE + "/youtube_music.apk",
    MACROS.YOUTUBE_MICROG: DIRS.YOUTUBE + "/micro_g.apk",
}

PACKAGES = {
    MACROS.HDO: "com.hdobox",
    MACROS.YOUTUBE: "app.revanced.android.youtube",
    MACROS.YOUTUBE_MUSIC: "app.revanced.android.apps.youtube.music",
    MACROS.YOUTUBE_MICROG: "com.mgoogle.android.gms",
    MACROS.SPOTIFY: "com.spotify.music",
}


class Exceptions:
    class InvalidMacro(Exception):
        def __init__(self, macro: str):
            self.macro = macro

        def __str__(self):
            return f"{COLORS.RED}Error{COLORS.RESET} Macro {COLORS.WHITE}{self.macro}{COLORS.RESET} not found in PATHS"

    class InvalidUrl(Exception):
        def __init__(self, url: str):
            self.url = url

        def __str__(self):
            return f"{COLORS.RED}Error{COLORS.RESET} Invalid url {COLORS.WHITE}{self.url}{COLORS.RESET}"

    class InvalidPackage(Exception):
        def __init__(self, macro: str, package: str):
            self.macro = macro
            self.package = package

        def __str__(self):
            return f"{COLORS.RED}Error{COLORS.RESET} Macro {COLORS.WHITE}{self.macro}{COLORS.RESET} has package {COLORS.WHITE}{self.package}{COLORS.RESET} instead of {COLORS.WHITE}{PACKAGES[self.macro]}{COLORS.RESET}"


class AppBase:
    def __init__(self, macro: str, url: str):
        if macro not in PATHS.keys():
            raise Exceptions.InvalidMacro(macro)
        self.macro = macro
        self.get_apk(url)
        apkInfo = self.extract_apk(url)
        self.update_index(apkInfo)

    def get_apk(self, url: str):
        r = requests.get(url)
        with open(PATHS[self.macro], "wb") as apk:
            apk.write(r.content)
        apk = APK(PATHS[self.macro])
        if apk.package != PACKAGES[self.macro]:
            os.remove(PATHS[self.macro])
            raise Exceptions.InvalidPackage(self.macro, apk.package)

    def extract_apk(self, url: str):
        apk = APK(PATHS[self.macro])
        os.remove(PATHS[self.macro])
        return APKInfo(apk.version_name, url)

    def update_index(self, new: APKInfo):
        index = None
        with open(GLOBAL.INDEX_PATH, "r") as index_file:
            index = json.load(index_file)
        try:
            oldAPKInfo = APKInfo(
                index[self.macro]["version"], index[self.macro]["link"]
            )
        except:
            oldAPKInfo = APKInfo("", "")
        if oldAPKInfo == new:
            print(
                f"{COLORS.GREEN}Success{COLORS.RESET} No update for {COLORS.WHITE}{self.macro}{COLORS.RESET}"
            )
            return
        old_version = oldAPKInfo.version
        index[self.macro]["version"] = new.version
        index[self.macro]["link"] = new.link
        index_dump = json.dumps(index, indent=4)
        with open(GLOBAL.INDEX_PATH, "w") as index_file:
            index_file.write(index_dump)
        print(
            f"{COLORS.GREEN}Success{COLORS.RESET} Updated {COLORS.WHITE}{self.macro}{COLORS.RESET} from {COLORS.WHITE}{old_version}{COLORS.RESET} to {COLORS.WHITE}{new.version}{COLORS.RESET}"
        )


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


def updateHDO():
    link = "https://hdo.app/download"
    try:
        AppBase(MACROS.HDO, link)
    except Exception as e:
        print(e)
        return


def updateMicroG():
    scrapper = GithubScrapping(
        GITHUB_DATA[MACROS.YOUTUBE_MICROG]["user"],
        GITHUB_DATA[MACROS.YOUTUBE_MICROG]["repo"],
    )
    latest = scrapper.getVersions()[0]
    link = scrapper.link(latest, [".apk"])[0]
    try:
        AppBase(MACROS.YOUTUBE_MICROG, link)
    except Exception as e:
        print(e)
        return


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
    try:
        AppBase(MACROS.YOUTUBE, link)
    except Exception as e:
        print(e)
        return


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
    try:
        AppBase(MACROS.YOUTUBE_MUSIC, link)
    except Exception as e:
        print(e)
        return


def updateSpotifyRaw():
    while True:
        link = input("Enter the link to the spotify apk: ")
        print(f"\n\n{link}\nIs this the correct link? (y/n)")
        if input().lower() == "y":
            break
    try:
        AppBase(MACROS.SPOTIFY, link)
    except Exception as e:
        print(e)
        return


def updateSpotifySelenium():
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get("https://spotifygeek.tricksnation.com/link/download/1/")
    elements = driver.find_elements(By.XPATH, "//a[@href]")
    link = None
    for element in elements:
        if element.get_attribute("href") and element.get_attribute("href").endswith(
            ".apk"
        ):
            link = element.get_attribute("href")
            break
    driver.quit()
    try:
        AppBase(MACROS.SPOTIFY, link)
    except Exception as e:
        print(e)
        return


def main():
    updateHDO()
    updateMicroG()
    updateYoutube()
    updateYoutubeMusic()
    updateSpotifySelenium()


if __name__ == "__main__":
    main()
