import lzma
import requests
from fgi.logger import Logger


class Downloader:
    def __init__(self, url: str, tagged_url: str):
        self.url = url
        self.tagged_url = tagged_url
        self.tag: str = None

    def _request(self, url: str):
        try:
            Logger.debug(f"Requesting {url}...")
            response = requests.get(url)
        except requests.ConnectionError:
            raise RuntimeError(f"Request to {url} is timed out")
        assert response.status_code == 200, f"Failed making request to {url}, status code is not 200"
        return response

    def get_latest_release_tag(self) -> str:
        if self.tag is None:
            self.tag = self._request(self.url).json().get("tag_name")
        return self.tag

    def get_assets(self) -> list[str]:
        return [asset["browser_download_url"] for asset in self._request(self.tagged_url % self.get_latest_release_tag()).json()["assets"]]

    def get_asset(self, url: str) -> bytes:
        return self._request(url).content

    def decompress(self, data: bytes) -> bytes:
        return lzma.decompress(data)
