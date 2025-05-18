<div align="center">

![Multi DL](./assets/banner.png)

A cli tool for downloading media from various platforms

</div>

## 🎯 Features

- Supports `YouTube` & `Spotify` (*more platforms coming soon*).
- Obtain information about any video, music, playlist, album, channel, etc...
- Ability to download whole youtube channel.
- Supports parallel downloads.
- Supports beautiful search system for downloading and obtaining information.

## 🚩 Installation

> [!IMPORTANT]
> You must have `FFmpeg` installed on your system. You can download it from [here](https://ffmpeg.org/download.html).

- **Supported Python version:** 3.13 or higher

- Build from source
    ```sh
    pip install git+https://github.com/swayam25/Multi-DL
    ```

- Install via `pip`
    ```sh
    pip install multidl
    ```

- Install via `uv`
    ```sh
    uv tool install multidl
    ```

## ⚙️ Configuration

- Default Config File Path
    - Linux: `~/.config/multidl/config.json`
    - MacOS: `~/Library/Application Support/multidl/config.json`
    - Windows: `%APPDATA%/multidl/config.json`

- Config file path can be overridden by setting the `MULTIDL_CONFIG` environment variable.

- Config file structure
    ```json
    {
        "spotify_credentials": {
            "client_id": "your_client_id",
            "client_secret": "your_client_secret"
        },
        "spotify_tos": true // Set to true if you agree to Spotify's TOS
    }
    ```

- Run the following command for more information
    ```sh
    multidl config --path
    ```


## ❤️ Contributing

- Things to keep in mind
    - Follow our commit message convention.
    - Write meaningful commit messages.
    - Keep the code clean and readable.
    - Make sure the app is working as expected.

- Use [`uv`](https://docs.astral.sh/uv/) package manager for development.

- Code Formatting
    - Use [`ruff`](https://docs.astral.sh/ruff/) for formatting and linting.
    - Use [`pyright`](https://microsoft.github.io/pyright/#/) for type checking.
    - Install [`ruff`](https://docs.astral.sh/ruff/editors/) and [`pyright`](https://microsoft.github.io/pyright/#/installation) extensions in your code editor and format the code before committing.
