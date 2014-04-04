#!/bin/sh

########################################
# Root provisioning
########################################
# Configure the VM for running ROOT and Flask with Foreman.
# Updates the VM, installs ROOT and Ruby dependencies, and then,
# after a reboot, configures AFS and runs the user provisions.
#
# Initialise the VM with provisioning
#   vagrant up --provision
# Reload the VM when prompted, provisioning a final time
#   vagrant reload --provision
# This restart is done to ensure any upgraded kernel is loaded.
########################################

echo "Beginning provisioning"

YUM=/usr/bin/yum

# Add the SLC6 XROOTD stable repository
# http://xrootd.org/binaries/xrootd-stable-slc6.repo
sudo cat > /etc/yum.repos.d/xrootd-stable-slc6.repo << EOF
[xrootd-stable]
name=XRootD Stable repository
baseurl=http://xrootd.org/binaries/stable/slc/6/\$basearch http://xrootd.cern.ch/sw/repos/stable/slc/6/\$basearch
gpgcheck=0
enabled=1
protect=0
EOF

echo "Updating packages"
sudo $YUM -y update

echo "Installing required packages"
# The bare necessities:
#   vim and git
#   OpenAFS
#   ROOT dependencies
#   Ruby dependencies
#   XROOTD
sudo $YUM install -y \
  vim git \
  kmod-openafs openafs openafs-client \
  libXpm \
  zlib-devel \
  xrootd-client-devel xrootd-client xrootd-libs-devel xrootd-libs xrootd-server

PREPFILE=$HOME/.preparation

if [ ! -f $PREPFILE ]; then
  touch $PREPFILE
  echo "You now need to reboot the VM and rerun the provisioning."
  echo "To do this, run:"
  echo "  vagrant reload --provision"
  echo "I will then continue setting up the VM."
  exit
else
  rm -f $PREPFILE
  echo "Resuming provisioning"
fi

echo "Configuring AFS"
echo "cern.ch" > $HOME/ThisCell
sudo mv $HOME/ThisCell /usr/vice/etc/ThisCell
sudo /sbin/chkconfig --add afs
sudo /sbin/service afs on

# Run the user provision as the vagrant user
su vagrant -c '/vagrant/user_provisioning.sh'

echo "Provisioning complete!"
