#/bin/env bash
# If you want the environment variables to be set automatically when you start a new shell, 
# you can add the following line to your .bashrc or .bash_profile file:

envfile="/home/thecw/Projects/xiaoxiang/development.env"
if [ -f $envfile ]; then
  export $(grep -v '^#' $envfile | xargs)
fi
