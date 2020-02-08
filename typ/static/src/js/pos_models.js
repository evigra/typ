odoo.define('typ.models.extend', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var _t = core._t;

    models.load_models({
        model: 'l10n_mx_edi.payment.method',
        fields: ['name'],
        loaded: function(self, l10n_mx_edi_payment_method){
            self.l10n_mx_edi_payment_method = l10n_mx_edi_payment_method;
        },
    });

    models.load_fields('res.partner', ['l10n_mx_edi_usage', 'l10n_mx_edi_payment_method_id']);

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes){
            this.usage_selection = {
                'G01': _t('Acquisition of merchandise'),
                'G02': _t('Returns, discounts or bonuses'),
                'G03': _t('General expenses'),
                'I01': _t('Constructions'),
                'I02': _t('Office furniture and equipment investment'),
                'I03': _t('Transportation equipment'),
                'I04': _t('Computer equipment and accessories'),
                'I05': _t('Dices, dies, molds, matrices and tooling'),
                'I06': _t('Telephone communications'),
                'I07': _t('Satellite communications'),
                'I08': _t('Other machinery and equipment'),
                'D01': _t('Medical, dental and hospital expenses.'),
                'D02': _t('Medical expenses for disability'),
                'D03': _t('Funeral expenses'),
                'D04': _t('Donations'),
                'D05': _t('Real interest effectively paid for mortgage loans (room house)'),
                'D06': _t('Voluntary contributions to SAR'),
                'D07': _t('Medical insurance premiums'),
                'D08': _t('Mandatory School Transportation Expenses'),
                'D09': _t('Deposits in savings accounts, premiums based on pension plans.'),
                'D10': _t('Payments for educational services (Colegiatura)'),
                'P01': _t('To define'),
            };
            return _super_posmodel.initialize.call(this,session,attributes);
        },
    });
});
