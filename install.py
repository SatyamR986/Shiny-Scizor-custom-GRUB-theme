#!/usr/bin/env python3
"""
S-Scizor GRUB Theme Installer
Clone the repo, run this script as root, and it sets up the theme for you.
"""

import os
import re
import shutil
import subprocess
import sys
import platform
from datetime import datetime

THEME_NAME = "mytheme"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_THEME_DIR = os.path.join(SCRIPT_DIR, "mytheme")

GRUB_DEFAULT_PATH = "/etc/default/grub"

# The exact settings this theme needs in /etc/default/grub
DESIRED_SETTINGS = {
    "GRUB_DISABLE_OS_PROBER": "false",
    "GRUB_GFXMODE": "1920x1080x32",
    "GRUB_THEME": None,  # filled in at runtime with the real install path
}


def die(msg):
    print(f"[ERROR] {msg}")
    sys.exit(1)


def info(msg):
    print(f"[*] {msg}")


def ensure_root():
    if os.geteuid() != 0:
        print("This needs root access to write to /boot and /etc/default/grub.")
        print("Re-running with sudo...")
        os.execvp("sudo", ["sudo", sys.executable] + sys.argv)


def detect_os():
    system = platform.system()
    if system == "Windows":
        die(
            "GRUB theming isn't applicable from Windows.\n"
            "Boot into your Linux side and run this script there."
        )
    if system != "Linux":
        die(f"Unsupported OS: {system}")
    return system


def detect_bootloader():
    if os.path.isdir("/boot/grub") or os.path.isdir("/boot/grub2"):
        return "grub"
    if os.path.isdir("/boot/efi/loader") or os.path.isdir("/boot/loader"):
        return "systemd-boot"
    return "unknown"


def get_distro_family():
    """Best-effort distro family detection, but we mainly trust which
    binaries actually exist (has_command) rather than this."""
    try:
        with open("/etc/os-release") as f:
            content = f.read().lower()
    except FileNotFoundError:
        return "unknown"

    if "ubuntu" in content or "debian" in content:
        return "debian"
    if "fedora" in content or "rhel" in content or "centos" in content:
        return "fedora"
    if "arch" in content:
        return "arch"
    if "opensuse" in content or "suse" in content:
        return "opensuse"

    for line in content.splitlines():
        if line.startswith("id_like"):
            like = line.split("=", 1)[1].strip('"')
            if "debian" in like:
                return "debian"
            if "fedora" in like or "rhel" in like:
                return "fedora"
            if "arch" in like:
                return "arch"
    return "unknown"


def has_command(cmd):
    return shutil.which(cmd) is not None


def get_theme_install_root():
    """Where /boot/grub vs /boot/grub2 lives determines the theme path."""
    if os.path.isdir("/boot/grub"):
        return "/boot/grub/themes"
    if os.path.isdir("/boot/grub2"):
        return "/boot/grub2/themes"
    die("Could not find /boot/grub or /boot/grub2 — is GRUB actually installed?")


def get_update_command(family):
    """Prefer checking actual binaries over distro-family guessing."""
    if has_command("update-grub"):
        return ["update-grub"]
    if has_command("grub2-mkconfig"):
        # Figure out the right output path
        if os.path.isdir("/boot/efi/EFI"):
            # UEFI systems sometimes need the efi grub.cfg path; grub2-mkconfig
            # detects this itself in most distros, -o is still required though.
            cfg_path = "/boot/grub2/grub.cfg"
        else:
            cfg_path = "/boot/grub2/grub.cfg"
        return ["grub2-mkconfig", "-o", cfg_path]
    if has_command("grub-mkconfig"):
        return ["grub-mkconfig", "-o", "/boot/grub/grub.cfg"]
    die(
        "No known GRUB config generator found (update-grub / grub-mkconfig / "
        "grub2-mkconfig). Is GRUB installed on this system?"
    )


def backup_file(path):
    if not os.path.exists(path):
        return None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = f"{path}.bak.{timestamp}"
    shutil.copy2(path, backup_path)
    info(f"Backed up {path} -> {backup_path}")
    return backup_path


def backup_dir(path):
    if not os.path.isdir(path):
        return None
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = f"{path}.bak.{timestamp}"
    shutil.copytree(path, backup_path)
    info(f"Backed up {path} -> {backup_path}")
    return backup_path


def install_theme_files(theme_root):
    dest = os.path.join(theme_root, THEME_NAME)

    if not os.path.isdir(SOURCE_THEME_DIR):
        die(f"Theme source folder not found at {SOURCE_THEME_DIR}")

    os.makedirs(theme_root, exist_ok=True)

    if os.path.isdir(dest):
        backup_dir(dest)
        shutil.rmtree(dest)

    shutil.copytree(SOURCE_THEME_DIR, dest)
    info(f"Installed theme files to {dest}")
    return os.path.join(dest, "theme.txt")


def patch_grub_config(theme_txt_path):
    if not os.path.exists(GRUB_DEFAULT_PATH):
        die(f"{GRUB_DEFAULT_PATH} not found — is this really a GRUB system?")

    backup_file(GRUB_DEFAULT_PATH)

    settings = dict(DESIRED_SETTINGS)
    settings["GRUB_THEME"] = theme_txt_path

    with open(GRUB_DEFAULT_PATH, "r") as f:
        lines = f.readlines()

    keys_found = set()
    new_lines = []

    for line in lines:
        matched = False
        for key, value in settings.items():
            # Match both active and commented-out versions of the key
            pattern = rf'^\s*#?\s*{re.escape(key)}\s*='
            if re.match(pattern, line):
                new_lines.append(f'{key}="{value}"\n')
                keys_found.add(key)
                matched = True
                break
        if not matched:
            new_lines.append(line)

    # Append any settings that weren't present in the file at all
    for key, value in settings.items():
        if key not in keys_found:
            new_lines.append(f'{key}="{value}"\n')

    with open(GRUB_DEFAULT_PATH, "w") as f:
        f.writelines(new_lines)

    info(f"Patched {GRUB_DEFAULT_PATH} with theme settings")


def regenerate_grub_config(family):
    cmd = get_update_command(family)
    info(f"Regenerating GRUB config with: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        die("GRUB config regeneration failed. Your backups are safe — check the error above.")
    info("GRUB config regenerated successfully.")


def main():
    detect_os()
    ensure_root()

    bootloader = detect_bootloader()
    if bootloader != "grub":
        die(
            f"Detected bootloader: {bootloader}. This installer currently "
            "only supports GRUB theming."
        )

    family = get_distro_family()
    info(f"Detected distro family: {family}")

    theme_root = get_theme_install_root()
    info(f"Theme install directory: {theme_root}")

    theme_txt_path = install_theme_files(theme_root)
    patch_grub_config(theme_txt_path)
    regenerate_grub_config(family)

    print()
    print("=" * 50)
    print(" Theme installed successfully!")
    print(" Reboot to see it in action.")
    print("=" * 50)


if __name__ == "__main__":
    main()
