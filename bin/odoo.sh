#!/bin/bash
if [ "$1" != "" ] && [ "$2" != "" ]; then
        source /opt/$1/venv/bin/activate
        cd /opt/$1/odoo/
        echo "ODOO: $(date)" > /tmp/odoo.txt
        ./odoo-bin --pidfile=/opt/$1/$1.pid --config /opt/$1/openerp.conf --syslog &
        sleep 15
        echo "TELEGRAM: $(date)" >> /tmp/odoo.txt
        /opt/$1/bin/telegramserver.bash & 
        echo "FIN: $(date)" >> /tmp/odoo.txt
else
        echo "Sin Argumentos. Salgo"
fi
