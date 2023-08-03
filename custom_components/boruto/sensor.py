import requests
import os
from bs4 import BeautifulSoup
import re
import voluptuous as vol

from homeassistant.const import CONF_FOLDER
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import discovery
from homeassistant.exceptions import HomeAssistantError

DOMAIN = "boruto"
URL = "https://www.dattebane.com/pagina/Boruto%20Download"

SERVICE_DOWNLOAD_EPISODE = "download_episode"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_FOLDER): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


def setup(hass, config):
    """Set up the Boruto component."""
    conf = config[DOMAIN]

    coordinator = BorutoDataUpdateCoordinator(hass, conf[CONF_FOLDER])
    hass.data[DOMAIN] = coordinator

    def download_episode_service(call):
        """Handle the download_episode service."""
        coordinator.download_episode()

    async_register_admin_service(hass, DOMAIN, SERVICE_DOWNLOAD_EPISODE, download_episode_service)

    return True


class BorutoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Boruto data."""

    def __init__(self, hass, save_folder):
        """Initialize."""
        self.save_folder = save_folder

        def fetch_data():
            """Fetch data from Boruto website."""
            last_episode_url, cronograma = self.get_last_episode_url()
            return {"last_episode_url": last_episode_url, "cronograma": cronograma}

        super().__init__(
            hass, hass.loop, name=DOMAIN, update_interval=3600, update_method=fetch_data
        )

    def get_last_episode_url(self):
        url = URL

        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            last_episode_url = soup.select_one(
                'body > div.fundo > div.postagens > div.pagina > table:last-child > tr:last-child > td:nth-child(4) > div > a:nth-child(2)'
            )
            if last_episode_url:
                last_episode_url = last_episode_url.get('href')
            else:
                print('Last episode URL not found.')

            cronograma_items = soup.select(
                'body > div.fundo > div.cabecalho > div > div.CronogramaNews > div.CronogramaNewsNome1 > div.Cronograma > li'
            )[:5]
            cronograma = [item.text.strip() for item in cronograma_items]

            return last_episode_url, cronograma

        return None, None

    def download_episode(self):
        """Download the latest episode."""
        last_episode_url = self.data.get("last_episode_url")

        if last_episode_url:
            try:
                download_and_save_file(last_episode_url, self.save_folder)
            except HomeAssistantError as ex:
                raise UpdateFailed(f"Failed to download: {ex}")
        else:
            raise UpdateFailed("Failed to retrieve data")


def download_and_save_file(url, save_folder):
    # The same function as before, omitted for brevity.
    pass
