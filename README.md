Shiny-Scizor GRUB Theme

A custom GRUB bootloader theme. Clone this repo and run one script to install it.

Requirements
An OS using GRUB as its bootloader (Ubuntu, Debian, Fedora, Arch, openSUSE, Mint, Pop!_OS, etc.)
Python 3
sudo access

This does not work on systemd-boot, rEFInd, or Windows Boot Manager. GRUB themes only skin the GRUB menu itself.

Install
bash
git clone https://github.com/SatyamR986/Shiny-Scizor-custom-GRUB-theme.git
cd grub-theme-installer
python3 install.py

The script will ask for your sudo password if not already run as root.

Before you run it, check your screen resolution

The theme is set to 1920x1080x32 by default. If your monitor uses a different resolution, edit install.py before running it:

python
DESIRED_SETTINGS = {
    "GRUB_DISABLE_OS_PROBER": "false",
    "GRUB_GFXMODE": "1920x1080x32",   ------> change this to match your resolution
    "GRUB_THEME": None,
}

If you're not sure what resolutions your system supports, you can check from inside GRUB itself. At the GRUB menu, press c for the command line, then type vbeinfo and press Enter. It'll list supported modes. Press Esc to return to the menu, or reboot.

If the theme text/layout looks off-center or cut off after installing, this is almost always a resolution mismatch. Fix GRUB_GFXMODE and re-run the script (or manually edit /etc/default/grub and run sudo update-grub).

What this script does
Backs up your existing GRUB theme folder and /etc/default/grub (with a timestamp) before changing anything
Copies the theme files into your system's GRUB themes directory
Enables OS detection so dual-boot entries (e.g. Windows) show up correctly
Sets the theme and resolution in /etc/default/grub
Regenerates your GRUB config

It does not reboot your machine automatically. Reboot manually afterward to see the theme.

If something goes wrong

Every file this script touches is backed up first, with a .bak.<timestamp> suffix, in the same location as the original. To roll back:

bash
# Restore the GRUB default config
sudo cp /etc/default/grub.bak.<timestamp> /etc/default/grub

# Restore the old theme folder (if one existed)
sudo rm -rf /boot/grub/themes/mytheme
sudo mv /boot/grub/themes/mytheme.bak.<timestamp> /boot/grub/themes/mytheme

# Regenerate config
sudo update-grub

Worst case, this only affects the GRUB menu appearance. It does not touch your kernel, bootloader installation, or partition table, so there's no risk of an unbootable system from running this script.

Uninstall / revert to default GRUB look
bash
sudo sed -i '/GRUB_THEME=/d' /etc/default/grub
sudo update-grub
