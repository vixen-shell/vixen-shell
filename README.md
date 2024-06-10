# ![](assets/vixen_logo_md.png) Vixen Shell Project

## Presentation

The Vixen Shell project is an initiative dedicated to creating a highly customizable desktop environment for [Wayland](https://wayland.freedesktop.org/) users on Linux. Designed with a focus on development, it allows users to code the various components necessary to build their own desktop environment. This project is particularly useful for users of window managers such as [Sway](https://swaywm.org/) or [Hyprland](https://hyprland.org/).

Vixen Shell stands out by using [Python](https://www.python.org/) for the back-end, while the user interface (front-end) is developed with modern web technologies such as [React](https://fr.legacy.reactjs.org/), [TypeScript](https://www.typescriptlang.org/) and CSS.

The project was initially intended for [Hyprland](https://hyprland.org/), but during its development, its flexibility has allowed it to be adapted to other window managers. This is why, as you will discover by reading this documentation, there are pre-existing features dedicated to [Hyprland](https://hyprland.org/) in Vixen Shell's extras and many references and examples related to [Hyprland](https://hyprland.org/).

### Prerequisites

Before getting started with Vixen Shell, make sure you have the following:

1. **Operating System**:
    - A Linux distribution compatible with Wayland (e.g., Ubuntu, Fedora, Arch Linux, [Manjaro Linux](https://manjaro.org/)).

2. **Window Manager**:
    - Sway, Hyprland, or any other window manager compatible with Wayland.

3. **Languages and Technologies**:
    - **Python**: Ensure Python is installed (version 3.8 or higher).
    - **yarn**: For managing dependencies and building front-end components.

4. **Development Tools**:
    - A code editor or IDE (Visual Studio Code is recommended).
    - Git for version control (Recommended).

5. **Permissions and Access**:
    - Administrator or superuser access to install certain dependencies and perform system configurations.

## Installation

### Yarn

- Before proceeding with the installation, ensure that Yarn is installed on your system. You can check if Yarn is installed by running the following command in your terminal:

    ``` bash
    yarn --version
    ```

- If Yarn is not installed or if the command returns an error, you can install Yarn using the appropriate method for your system.

    ``` bash title="Arch Linux based distribution"
    sudo pacman -S yarn
    ```

### Vixen Shell

- Go to the [Vixen Shell GitHub](https://github.com/vixen-shell/vixen-shell) page and download the project archive in ZIP format, or download it [here](https://github.com/vixen-shell/vixen-shell/archive/refs/heads/main.zip).

- Once the download is complete, locate the ZIP file in your download folder. Right-click on the archive and select the option to extract the files. You can also use the command line:

    ``` bash
    unzip vixen-shell-main.zip
    ```

- After extracting the files, navigate to the newly created directory:

    ``` bash
    cd vixen-shell-main
    ```

- In the extracted directory, run the installation script as an administrator with the following command:

    ``` bash
    sudo ./install
    ```
    Confirm your choice and this script will install Vixen Shell on your system.

## Basic commands

* `vxm --help` - Show Vixen Shell help commands.
* `vxm --shell {open, close}` - Start / Close Vixen Shell.
* `vxm --setup {update, remove}` - Update / Remove Vixen Shell.

## Advanced commands

* `vxm --env {install, uninstall}` - Environment controls.
* `vxm --dev {run, new}` - Development controls.
* `vxm --features {names, add, remove}` - Features controls.
* `vxm --frames {ids, toggle, open, close}` - Feature frames controls.

## Uninstall

- To uninstall Vixen Shell from your system, simply type the following command:

    ``` bash
    sudo vxm --setup remove
    ```
    Confirm your choice and Vixen Shell will be completely uninstalled (or not depending on your choice :smile:)
