# Shiny-Scizor GRUB Theme

A custom GRUB bootloader theme. Clone this repository and run one script to install it.

## Requirements

* An OS using GRUB as its bootloader:

  * Ubuntu
  * Debian
  * Fedora
  * Arch Linux
  * openSUSE
  * Linux Mint
  * Pop!_OS
  * etc.
* Python 3
* `sudo` access

> This does **not** work on systemd-boot, rEFInd, or Windows Boot Manager. GRUB themes only customize the GRUB boot menu itself.

## Installation

Clone the repository:

```bash
git clone https://github.com/SatyamR986/Shiny-Scizor-custom-GRUB-theme.git
```

Enter the project directory:

```bash
cd Shiny-Scizor-custom-GRUB-theme
```

Run the installer:

```bash
python3 install.py
```

The script will ask for your `sudo` password if it is not already running as root.

## Before You Run It

Check your screen resolution before installing.

The theme is set to `1920x1080x32` by default. If your monitor uses a different resolution, edit `install.py` before running it:

```python
DESIRED_SETTINGS = {
    "GRUB_DISABLE_OS_PROBER": "false",
    "GRUB_GFXMODE": "1920x1080x32",  # Change this to match your resolution
    "GRUB_THEME": None,
}
```

If you're not sure which resolutions your system supports, you can check from inside GRUB itself.

At the GRUB menu:

1. Press `c` to open the GRUB command line.
2. Type:

```text
vbeinfo
```

3. Press Enter.

This will list the supported video modes.

Press `Esc` to return to the GRUB menu, or reboot your system.

### Theme Looks Off-Center or Cut Off?

If the theme text or layout looks off-center or gets cut off after installing, this is almost always caused by a resolution mismatch.

Fix the `GRUB_GFXMODE` value and re-run the script.

Alternatively, manually edit:

```text
/etc/default/grub
```

Then regenerate the GRUB configuration:

```bash
sudo update-grub
```

## What the Script Does

The installer:

* Backs up your existing GRUB theme folder and `/etc/default/grub` with a timestamp before changing anything.
* Copies the theme files into your system's GRUB themes directory.
* Enables OS detection so dual-boot entries, such as Windows, show up correctly.
* Sets the GRUB theme and resolution.
* Regenerates your GRUB configuration.

The script **does not automatically reboot your machine**.

Reboot manually afterward to see the theme.

## If Something Goes Wrong

Every file the script modifies is backed up first with a `.bak.` suffix in the same location as the original.

To roll back:

### Restore the GRUB Default Configuration

```bash
sudo cp /etc/default/grub.bak.* /etc/default/grub
```

### Restore the Old Theme Folder

If an old theme folder existed:

```bash
sudo rm -rf /boot/grub/themes/mytheme
sudo mv /boot/grub/themes/mytheme.bak.* /boot/grub/themes/mytheme
```

### Regenerate the GRUB Configuration

```bash
sudo update-grub
```

### Is There a Risk of Making the System Unbootable?

Worst case, this script only affects the appearance and configuration of the GRUB menu.

It does **not** modify:

* Your kernel
* Your bootloader installation
* Your partitions
* Your partition table

So running this script should not put your system at risk of becoming unbootable.

## Uninstall / Revert to the Default GRUB Look

Remove the theme setting:

```bash
sudo sed -i '/GRUB_THEME=/d' /etc/default/grub
```

Then regenerate the GRUB configuration:

```bash
sudo update-grub
```
