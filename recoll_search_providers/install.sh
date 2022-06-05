#!/bin/bash


#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Instalation script for Recoll Gnome desktop scripts and search providers




# System-wide installation

printf "\n\nInstalling Recoll Categorized search providers...\n"

printf "\nDesktop files... "
mapfile -t FILES < <(find . -name '*.desktop')
for FILE in "${FILES[@]}"; do
    TARGET="/usr/share/applications/$(basename "$FILE")"
    sudo cp "$FILE" "$TARGET"
    sudo chown root:root "$TARGET"
    sudo chmod 644 "$TARGET" 
done
printf "Done.\n"

printf "\nINI files... "
mapfile -t FILES < <(find . -name '*.ini')
for FILE in "${FILES[@]}"; do
    TARGET="/usr/share/gnome-shell/search-providers/$(basename "$FILE")"
    sudo cp "$FILE" "$TARGET"
    sudo chown root:root "$TARGET"
    sudo chmod 644 "$TARGET" 
done
printf "Done.\n"

printf "\nService files... "
mapfile -t FILES < <(find . -name '*.service')
for FILE in "${FILES[@]}"; do
    TARGET="/usr/share/dbus-1/services/$(basename "$FILE")"
    sudo cp "$FILE" "$TARGET"
    sudo chown root:root "$TARGET"
    sudo chmod 644 "$TARGET"
done
printf "Done.\n"


printf "Installing scripts... "
sudo cp ./gssp-recoll.py /usr/bin/gssp-recoll.py
sudo chown root:root /usr/bin/gssp-recoll.py
sudo chmod 755 /usr/bin/gssp-recoll.py

sudo cp ./gssp-recoll-www-extractor.py /usr/lib/gssp-recoll-www-extractor.py
sudo chown root:root /usr/lib/gssp-recoll-www-extractor.py
sudo chmod 755 /usr/lib/gssp-recoll-www-extractor.py

sudo cp ./gssp-www-extractor.pl /usr/lib/gssp-www-extractor.pl
sudo chown root:root /usr/lib/gssp-www-extractor.pl
sudo chmod 755 /usr/lib/gssp-www-extractor.pl

printf "Done.\n"



printf "Installing configuration and icons... "
sudo mv /usr/share/recoll/examples/mimeconf /usr/share/recoll/examples/mimeconf.bak
sudo mv /usr/share/recoll/examples/mimemap /usr/share/recoll/examples/mimemap.bak

sudo cp ./recoll_config/mimeconf /usr/share/recoll/examples/mimeconf
sudo cp ./recoll_config/mimemap /usr/share/recoll/examples/mimemap
sudo chown root:root /usr/share/recoll/examples/mimeconf /usr/share/recoll/examples/mimemap
sudo chmod 644 /usr/share/recoll/examples/mimeconf /usr/share/recoll/examples/mimemap

if [[ "$1" != "no_icons" && "$2" != "no_icons" ]]; then
    
    sudo mkdir -p /use/share/recoll/images/backup_recoll
    sudo cp /usr/share/recoll/images/*.png /use/share/recoll/images/backup_recoll/
    sudo cp ./recoll_icons/* /usr/share/recoll/images/
    sudo chown root:root /usr/share/recoll/images/*
    sudo chmod 644 /usr/share/recoll/images/*
fi

sudo cp ./theme_icons/*.svg /usr/share/icons/hicolor/symbolic/apps
sudo chmod 644 /usr/share/icons/hicolor/symbolic/apps/*.svg
sudo chown root:root /usr/share/icons/hicolor/symbolic/apps/*.svg

printf "Done.\n"



if [[ "$1" != "no_deps" && "$2" != "no_deps" ]]; then

    printf "Installing dependencies... "    
    sudo apt-get install libdbi-perl libdbd-sqlite3 libclass-dbi-sqlite-perl python-recoll python3-recoll
    printf "Done.\n"
fi


 