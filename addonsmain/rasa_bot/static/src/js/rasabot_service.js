odoo.define('rasa_bot.RasabotService', function (require) {
"use strict";

var AbstractService = require('web.AbstractService');
var core = require('web.core');
var session = require('web.session');

var _t = core._t;

var RasaBotService =  AbstractService.extend({
    /**
     * @override
     */
    start: function () {
        this._hasRequest = (window.Notification && window.Notification.permission === "default") || false;
        if ('rasabot_initialized' in session && !session.rasabot_initialized) {
            this._showRasabotTimeout();
        }
    },

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * Get the previews related to the rasaBot (conversation not included).
     * For instance, when there is no conversation with rasaBot and rasaBot has
     * a request, it should display a preview in the systray messaging menu.
     *
     * @param {string|undefined} [filter]
     * @returns {Object[]} list of objects that are compatible with the
     *   'mail.Preview' template.
     */
    getPreviews: function (filter) {
        var previews = [];
        if (this.hasRequest() && (filter === 'mailbox_inbox' || !filter)) {
            previews.push({
                title: _t("rasaBot has a request"),
                imageSRC: "/rasa_bot/static/src/img/rasalogo.png",
                status: 'bot',
                body:  _t("Enable desktop notifications to chat"),
                id: 'request_notification',
                unreadCounter: 1,
            });
        }
        return previews;
    },
    /**
     * Tell whether rasaBot has a request or not.
     *
     * @returns {boolean}
     */
    hasRequest: function () {
        return this._hasRequest;
    },
    /**
     * Called when user either accepts or refuses push notifications.
     */
    removeRequest: function () {
        this._hasRequest = false;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _showRasabotTimeout: function () {
        var self = this;
        setTimeout(function () {
            session.rasabot_initialized = true;
            self._rpc({
                model: 'mail.channel',
                method: 'init_rasabot',
            });
        }, 2*60*100);
    },
});

core.serviceRegistry.add('rasabot_service', RasaBotService);
return RasaBotService;

});
