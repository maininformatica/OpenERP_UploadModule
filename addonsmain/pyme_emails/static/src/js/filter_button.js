/**********************************************************************************
*
*    Copyright (c) 2021 Main Informatica Gandia, S.L.
*
*    This file is part of WEBMAIL PYME 
*
**********************************************************************************/
odoo.define('pyme_emails.filter_button', function (require) {
"use strict";
var core = require('web.core');
var ListController = require('web.ListController');
    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
                let filter_button = this.$buttons.find('.oe_filter_button');
                filter_button && filter_button.click(this.proxy('filter_button')) ;
            }
        },
        filter_button: function () {
            console.log('yay filter')
            //implement your click logic here
        }
    });
})