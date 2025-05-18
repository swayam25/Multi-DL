import json
import os
import platformdirs
from dataclasses import dataclass
from typing import TypedDict

config_path = platformdirs.user_config_dir("multidl")
DEFAULT_CONFIG_PATH = os.path.join(config_path, "config.json")
MULTIDL_CONFIG = os.environ.get("MULTIDL_CONFIG", DEFAULT_CONFIG_PATH)


@dataclass
class SpotifyCredentials(TypedDict):
    client_id: str
    client_secret: str


@dataclass
class ConfigSchema(TypedDict):
    spotify_credentials: SpotifyCredentials
    spotify_tos: bool


class Config:
    """Handles the configuration for multidl."""

    def __init__(self):
        self.default_config: ConfigSchema = {
            "spotify_credentials": {"client_id": "", "client_secret": ""},
            "spotify_tos": False,
        }
        if not os.path.exists(MULTIDL_CONFIG):
            self.create()

    def create(self) -> None:
        """Creates the config file with default values."""
        os.makedirs(os.path.dirname(MULTIDL_CONFIG), exist_ok=True)
        with open(MULTIDL_CONFIG, "a") as f:
            json.dump(self.default_config, f, indent=4)

    def reset(self) -> None:
        """Reset the config file to default values."""
        os.remove(MULTIDL_CONFIG)
        self.create()

    def load(self) -> ConfigSchema:
        """Loads config from the config file."""
        with open(MULTIDL_CONFIG) as f:
            config = json.load(f)

        def merge(d, default) -> ConfigSchema:
            for k, v in default.items():
                if k not in d:
                    d[k] = v
                elif isinstance(v, dict) and isinstance(d[k], dict):
                    merge(d[k], v)
            return d

        return merge(config, self.default_config)

    def save(self, config: ConfigSchema) -> None:
        """
        Save the config to the config file.

        Args:
            config: The config to save.
        """
        with open(MULTIDL_CONFIG, "w") as f:
            json.dump(config, f, indent=4)

    def set_spotify_credentials(self, client_id: str, client_secret: str) -> ConfigSchema:
        """
        Set Spotify credentials in the config file.

        Args:
            client_id: The Spotify client ID.
            client_secret: The Spotify client secret.
        """
        config = self.load()
        config["spotify_credentials"] = {
            "client_id": client_id,
            "client_secret": client_secret,
        }
        self.save(config)
        return config

    def accept_spotify_tos(self, accept: bool) -> ConfigSchema:
        """
        Accept Spotify TOS in the config file.

        Args:
            accept: Whether to accept the Spotify TOS.
        """
        config = self.load()
        config["spotify_tos"] = accept
        self.save(config)
        return config
