#!/bin/bash
#
#  TELEGRAM BASH Daemon
#


# API
DIR="http://localhost:8069"
BBDD="pp1"
USER="admin"
PASS="admin"

# Control de Errores de Sistema
ERRORLOG="ERROR"
WARNLOG="WARN"
FECHAHORALOG="$(date +'%b %d %H:%M:%S') $HOSTNAME Alertas:"
SYSLOG="/var/log/syslog"

# Controles y Bucles
ESPERA="/bin/sleep"
SEGESPERA="0"

USREX="$(whoami)"
if [ "$USREX" == "root" ]; then
 echo "Eres Root! :)"
 PREEXECUTE="sudo -u postgres -H -- /usr/bin/"
else
 echo "No eres root... :'("
 PREEXECUTE="/usr/bin/"
fi


TELEGRAMSERVER="$(find ~/odoo/ | grep controllers | grep telegramserver.py)"

if [ "$TELEGRAMSERVER" == "" ]; then
 echo "Telegram NO encontrado. Espero 30 Segundos"
 sleep 30

else 
 

while :
do
${PREEXECUTE}psql -d $BBDD -t -c "SELECT id,token_telegram  FROM pyme_telegram WHERE activo='t'"  | while read "TELEGRAMACTIVE" ;do
ID="$(echo ${TELEGRAMACTIVE[0]} | cut -d'|' -f1 | awk {'print $1'})"
TOKEN="$(echo ${TELEGRAMACTIVE[0]} | cut -d'|' -f2 | awk {'print $1'})"
if [ "$ID" != "False" ] && [ "$TOKEN" != "" ]; then

 echo -n "Mirando: $ID con Token >$TOKEN< "
 ENMARCHA="$(ps aux | grep "$TOKEN" | grep -v grep)"
 if [ "$ENMARCHA" == "" ]; then
     echo "Iniciando.."
     python3 $TELEGRAMSERVER $TOKEN $DIR $BBDD $USER $PASS&
 else
     echo "En marcha" 
     PROCESO="$(ps aux | grep "$TOKEN" | grep -v grep | awk {'print $2'})"
	 ${PREEXECUTE}psql -d $BBDD -t -c "UPDATE pyme_telegram SET idproceso='$PROCESO' WHERE id='$ID'"
     
  fi
fi
done
sleep 5

${PREEXECUTE}psql -d $BBDD -t -c "SELECT id,token_telegram,idproceso  FROM pyme_telegram WHERE activo IS NULL OR activo='f'"  | while read "TELEGRAMACTIVE" ;do
ID="$(echo ${TELEGRAMACTIVE[0]} | cut -d'|' -f1 | awk {'print $1'})"
TOKEN="$(echo ${TELEGRAMACTIVE[0]} | cut -d'|' -f2 | awk {'print $1'})"
PROC="$(echo ${TELEGRAMACTIVE[0]} | cut -d'|' -f2 | awk {'print $1'})"
if [ "$ID" != "False" ] && [ "$TOKEN" != "" ]; then

 echo -n "Mirando: $ID con Token >$TOKEN< "
 ENMARCHA="$(ps aux | grep "$TOKEN" | grep -v grep | awk {'print $2'})"
 if [ "$ENMARCHA" == "" ]; then
     echo "NO detectado"
 else
     echo "Matando: $ENMARCHA" 
	 kill -9 $ENMARCHA
	 ${PREEXECUTE}psql -d $BBDD -t -c "UPDATE pyme_telegram SET idproceso='False' WHERE id='$ID'"
  fi
fi

done


sleep 5
done


fi