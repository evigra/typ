import base64
import io
import zipfile

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    is_commission = fields.Boolean(
        help="This must be True if the amount difference is because the bank take that amount to commissions."
    )

    def l10n_mx_edi_amount_to_text(self):
        """Method to transform a float amount to text words
        E.g. 100 - ONE HUNDRED
        :returns: Amount transformed to words mexican format for invoices
        :rtype: str
        """
        self.ensure_one()
        currency = self.currency_id.name.upper()
        # M.N. = Moneda Nacional (National Currency)
        # M.E. = Moneda Extranjera (Foreign Currency)
        currency_type = "M.N" if currency == "MXN" else "M.E."
        # Split integer and decimal part
        amount_i, amount_d = divmod(self.amount, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))
        words = self.currency_id.with_context(lang=self.partner_id.lang or "es_ES").amount_to_text(amount_i).upper()
        invoice_words = "%(words)s %(amount_d)02d/100 %(curr_t)s" % dict(
            words=words, amount_d=amount_d, curr_t=currency_type
        )
        return invoice_words

    def my_payment_complements_zip(self):
        id_payment = self.id
        attachments_ids = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_id", "=", id_payment),
                    ("res_model", "=", "account.payment"),
                ],
                limit=2,
            )
        )
        attachment_file_id = self.retrieve_payment_complements_zip()
        if attachment_file_id:
            return attachment_file_id
        if attachments_ids:
            attachment_file_id = self.create_zip(attachments_ids) if len(attachments_ids) > 1 else attachments_ids[0]

        return attachment_file_id

    def retrieve_payment_complements_zip(self):
        domain = [
            ("res_id", "=", self.id),
            ("mimetype", "=", "application/zip"),
            ("res_model", "=", "account.payment"),
        ]
        attachments = self.env["ir.attachment"].search(domain, limit=1)
        return attachments

    def create_zip(self, attachments_ids):
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, "w") as myzip:
            for attachment in attachments_ids:
                myzip.writestr(attachment.name, base64.b64decode(attachment.datas))
            myzip.close()
            zip_name = attachments_ids[0].name.replace(".xml", ".zip")
            values = {
                "name": zip_name,
                "type": "binary",
                "mimetype": "application/zip",
                "public": False,
                "db_datas": base64.b64encode(zip_stream.getvalue()),
                "res_id": attachments_ids[0].res_id,
                "datas_fname": zip_name,
                "res_model": "account.payment",
            }
        attachment_id = self.env["ir.attachment"].create(values)
        return attachment_id


# class AccountRegisterPayments(models.TransientModel):  -> TODO: review on v14.0
#     _inherit = "account.register.payments"

#     is_commission = fields.Boolean(
#         help="This must be True if the amount difference is because the bank " "take that amount to commissions."
#     )

#     def _prepare_payment_vals(self, invoices):
#         """Any field that is going to be passed from this model to
#         account.payment needs to be added in this dictionary"""
#         res = super()._prepare_payment_vals(invoices)
#         res.update(
#             {
#                 "is_commission": self.is_commission,
#             }
#         )
#         return res
