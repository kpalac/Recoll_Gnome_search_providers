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



printf "\n\nInstalling Recoll Categorized search providers...\n"

printf "\nDesktop files... "
sudo cp org.recoll.RecollFiles.SearchProvider.desktop /usr/share/applications/org.recoll.RecollFiles.SearchProvider.desktop
sudo chown root:root /usr/share/applications/org.recoll.RecollFiles.SearchProvider.desktop
sudo chmod 644 /usr/share/applications/org.recoll.RecollFiles.SearchProvider.desktop

sudo cp org.recoll.RecollMail.SearchProvider.desktop /usr/share/applications/org.recoll.RecollMail.SearchProvider.desktop
sudo chown root:root /usr/share/applications/org.recoll.RecollMail.SearchProvider.desktop
sudo chmod 644 /usr/share/applications/org.recoll.RecollMail.SearchProvider.desktop

sudo cp org.recoll.RecollNews.SearchProvider.desktop /usr/share/applications/org.recoll.RecollNews.SearchProvider.desktop
sudo chown root:root /usr/share/applications/org.recoll.RecollNews.SearchProvider.desktop
sudo chmod 644 /usr/share/applications/org.recoll.RecollNews.SearchProvider.desktop

sudo cp org.recoll.RecollNotes.SearchProvider.desktop /usr/share/applications/org.recoll.RecollNotes.SearchProvider.desktop
sudo chown root:root /usr/share/applications/org.recoll.RecollNotes.SearchProvider.desktop
sudo chmod 644 /usr/share/applications/org.recoll.RecollNotes.SearchProvider.desktop
printf "Done.\n"


printf "Installing INI files... "
sudo cp org.recoll.RecollFiles.search-provider.ini /usr/share/gnome-shell/search-providers/org.recoll.RecollFiles.search-provider.ini
sudo chown root:root /usr/share/gnome-shell/search-providers/org.recoll.RecollFiles.search-provider.ini
sudo chmod 644 /usr/share/gnome-shell/search-providers/org.recoll.RecollFiles.search-provider.ini

sudo cp org.recoll.RecollMail.search-provider.ini /usr/share/gnome-shell/search-providers/org.recoll.RecollMail.search-provider.ini
sudo chown root:root /usr/share/gnome-shell/search-providers/org.recoll.RecollMail.search-provider.ini
sudo chmod 644 /usr/share/gnome-shell/search-providers/org.recoll.RecollMail.search-provider.ini

sudo cp org.recoll.RecollNews.search-provider.ini /usr/share/gnome-shell/search-providers/org.recoll.RecollNews.search-provider.ini
sudo chown root:root /usr/share/gnome-shell/search-providers/org.recoll.RecollNews.search-provider.ini
sudo chmod 644 /usr/share/gnome-shell/search-providers/org.recoll.RecollNews.search-provider.ini

sudo cp org.recoll.RecollNotes.search-provider.ini /usr/share/gnome-shell/search-providers/org.recoll.RecollNotes.search-provider.ini
sudo chown root:root /usr/share/gnome-shell/search-providers/org.recoll.RecollNotes.search-provider.ini
sudo chmod 644 /usr/share/gnome-shell/search-providers/org.recoll.RecollNotes.search-provider.ini
printf "Done.\n"


printf "Installing service files... "

sudo cp org.recoll.RecollFiles.SearchProvider.service /usr/share/dbus-1/services/org.recoll.RecollFiles.SearchProvider.service
sudo chown root:root /usr/share/dbus-1/services/org.recoll.RecollFiles.SearchProvider.service
sudo chmod 644 /usr/share/dbus-1/services/org.recoll.RecollFiles.SearchProvider.service

sudo cp org.recoll.RecollMail.SearchProvider.service /usr/share/dbus-1/services/org.recoll.RecollMail.SearchProvider.service
sudo chown root:root /usr/share/dbus-1/services/org.recoll.RecollMail.SearchProvider.service
sudo chmod 644 /usr/share/dbus-1/services/org.recoll.RecollMail.SearchProvider.service

sudo cp org.recoll.RecollNews.SearchProvider.service /usr/share/dbus-1/services/org.recoll.RecollNews.SearchProvider.service
sudo chown root:root /usr/share/dbus-1/services/org.recoll.RecollNews.SearchProvider.service
sudo chmod 644 /usr/share/dbus-1/services/org.recoll.RecollNews.SearchProvider.service

sudo cp org.recoll.RecollNotes.SearchProvider.service /usr/share/dbus-1/services/org.recoll.RecollNotes.SearchProvider.service
sudo chown root:root /usr/share/dbus-1/services/org.recoll.RecollNotes.SearchProvider.service
sudo chmod 644 /usr/share/dbus-1/services/org.recoll.RecollNotes.SearchProvider.service
printf "Done.\n"




printf "Installing script... "

sudo cp gssp-recoll.py /usr/bin/gssp-recoll.py
sudo chown root:root /usr/bin/gssp-recoll.py
sudo chmod 755 /usr/bin/gssp-recoll.py
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
    sudo apt-get install python-recoll
    sudo apt-get install python3-recoll
    printf "Done.\n"
fi


 