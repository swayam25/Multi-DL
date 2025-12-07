<div align="center">

![Multi DL](https://github.com/swayam25/Multi-DL/raw/main/assets/banner.png)

A cli tool for downloading media from various platforms

</div>

## 🎯 Features

- Obtain information about any video, music, playlist, album, channel, etc...
- Ability to download whole youtube channel.
- Supports parallel downloads.
- Supports beautiful search system for downloading and obtaining information.

## 🚩 Installation

> [!IMPORTANT]
> You must have `FFmpeg` installed on your system. You can download it from [here](https://ffmpeg.org/download.html).
> Python v3.13 or higher is required.

- Official Packages
    | OS  | Repository                               | Command                   |
    | --- | ---------------------------------------- | ------------------------- |
    | Any | [PyPI](https://pypi.org/project/multidl) | `pip install multidl`     |
    | Any | [PyPI](https://pypi.org/project/multidl) | `uv tool install multidl` |

- Community Packages
    | OS         | Repository                                                                                       | Command          |
    | ---------- | ------------------------------------------------------------------------------------------------ | ---------------- |
    | Arch Linux | [AUR](https://aur.archlinux.org/packages/multidl) (*by [`Daniel`](https://github.com/booo2233)*) | `yay -S multidl` |


## ⚙️ Configuration

- Default Config File Path
    - Linux: `~/.config/multidl/config.toml`
    - MacOS: `~/Library/Application Support/multidl/config.toml`
    - Windows: `%APPDATA%/multidl/config.toml`

- Config file path can be overridden by setting the `MULTIDL_CONFIG` environment variable.

- Config file structure
    ```toml
    spotify-tos = true # Set to true if you have accepted Spotify's TOS

    [spotify-credentials]
    client-id = ""
    client-secret = ""
    ```

- Run the following command for more information
    ```sh
    multidl config --docs
    ```

## ❤️ Contributing

- Things to keep in mind
    - Follow our commit message convention.
    - Write meaningful commit messages.
    - Keep the code clean and readable.
    - Make sure the app is working as expected.

- Use [`uv`](https://docs.astral.sh/uv/) package manager for development.

- Setup `pre-commit` hooks
    ```sh
    pre-commit install
    ```
