// odoo.define('scan_js_assets.after_scan', function (require) {
//   const AbstractAction = require('web.AbstractAction');
//   const core = require('web.core');

//   const AfterScan = AbstractAction.extend({
//     template: "JSAfterScan",
//     info: "this message comes from the JS"
//   });

//   core.action_registry.add('after_scan_action', AfterScan);
// });

// ================================================================== //

odoo.define('scan_js_assets.after_scan', function (require) {
  "use strict";

  var AbstractAction = require('web.AbstractAction');
  var ajax = require('web.ajax');
  var core = require('web.core');
  var Session = require('web.session');

  var QWeb = core.qweb;

  var AfterScan = AbstractAction.extend({

    start: function () {
      var self = this;
      core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
      self.session = Session;
      console.log(this.session);
      var def = this._rpc({
          model: 'res.partner',
          method: 'search_read',
          // method: 'partner_scan_js',
          // args: [barcode, ],
        })
        .then(function (partner) {
          self.nomor_anggota = partner[0].no_anggota;
          self.nama_anggota = partner[0].name;
          self.nomor_npk = partner[0].no_npk;
          self.saldo_simpanan = partner[0].total_saldo_simpanan;
          self.saldo_pinjaman = partner[0].total_saldo_pinjaman;
          self.$el.html(QWeb.render("JSAfterScan", {
            widget: self
          }));
        });
    },

    _onBarcodeScanned: function (barcode) {
      var self = this;
      core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
      this._rpc({
          model: 'res.partner',
          method: 'partner_scan_js',
          args: [barcode, ],
        })
        // .then(function (result) {
        //   if (result.action) {
        //     self.do_action(result.action);
        //   } else if (result.warning) {
        //     self.do_warn(result.warning);
        //     core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
        //   }
        // }, function () {
        //   core.bus.on('barcode_scanned', self, self._onBarcodeScanned);
        // });
    },



  });

  core.action_registry.add('after_scan_action', AfterScan);

  return AfterScan;

});