// odoo.define('scan_js.main', function (require) {
//   const AbstractAction = require('web.AbstractAction');
//   const core = require('web.core');

//   const OurAction = AbstractAction.extend({
//     template: "scan_js.ClientAction",
//     info: "this message comes from the JS"
//   });

//   core.action_registry.add('scan_js.action', OurAction);
// });

odoo.define('scan_js_assets.scan_js', function (require) {
  "use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var core = require('web.core');
var Session = require('web.session');

var QWeb = core.qweb;

var KioskMode = AbstractAction.extend({

  start: function () {
    var self = this;
    core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
    self.session = Session;
    console.log();
    var def = this._rpc({
        model: 'res.company',
        method: 'search_read',
        args: [[['id', '=', this.session.company_id]], ['name']],
      })
      .then(function (companies){
        self.company_name = companies[0].name;
        self.company_image_url = self.session.url('/web/image', {model: 'res.company', id: self.session.company_id, field: 'logo',});
        self.$el.html(QWeb.render("ScanJSKioskMode", {widget: self}));
        // self.start_clock();
      });
    // self._interval = window.setInterval(this._callServer.bind(this), (60*60*1000*24));
    return Promise.all([def, this._super.apply(this, arguments)]);
  },

  _onBarcodeScanned: function(barcode) {
    var self = this;
    core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
    this._rpc({
        model: 'res.partner',
        method: 'partner_scan_js',
        args: [barcode, ],
      })
      .then(function (result) {
        if (result.action) {
            self.do_action(result.action);
        } else if (result.warning) {
            self.do_warn(result.warning);
            core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
        }
      }, function () {
          core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
      });
  },

});

core.action_registry.add('scan_js_action', KioskMode);

return KioskMode;

});