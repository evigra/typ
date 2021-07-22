import logging
from odoo import _, api, models, fields

# from odoo.addons.l10n_mx_edi.tools.run_after_commit import run_after_commit  -> TODO: review on v14.0

import io
import zipfile
import base64

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):

    _inherit = "account.move"


    type_payment_term = fields.Selection(
        [("credit", "Credit"), ("cash", "Cash"), ("postdated_check", "Postdated check")], default="credit"
    )

    @api.onchange("type_payment_term", "partner_id")
    def _get_payment_term(self):
        """Get payment term depends on type payment term in invoice register."""
        acc_payment_term_obj = self.env["account.payment.term"]
        self = self._context.get("res_id") or self
        if not self.partner_id:
            return
        immediate_payment = self.env.ref("account.account_payment_term_immediate")
        self.invoice_payment_term_id = self.partner_id.property_payment_term_id.id
        if self.pos_order_ids and (
            not self.invoice_payment_term_id or self.invoice_payment_term_id.payment_type != "cash" or self.type_payment_term != "cash"
        ):
            self.invoice_payment_term_id = immediate_payment
            self.type_payment_term = "cash"
            return
        if self.type_payment_term in ("cash", "postdated_check"):
            payment_term = acc_payment_term_obj.search([]).filtered(lambda dat: dat.payment_type == "cash")
            self.invoice_payment_term_id = payment_term[0] if payment_term else False

        if self.type_payment_term == "credit" and (
            not self.invoice_payment_term_id or self.invoice_payment_term_id.payment_type == "cash"
        ):
            self.type_payment_term = "cash"
            if not self.invoice_payment_term_id:
                self.invoice_payment_term_id = immediate_payment

        elif self.type_payment_term in ("cash", "postdated_check") and self.invoice_payment_term_id.payment_type == "credit":
            self.type_payment_term = "credit"

    def action_invoice_open(self):
        """If this invoice comes from the PoS, send it by e-mail automatically"""
        res = super().action_invoice_open()
        if "pos_picking_id" in self.env.context:
            self.send_invoice_mail()
        return res

    @api.model
    def get_human_value(self, field_name, selection_option):
        """Convert technical key to value to show in selection human readable
        for the user.
        :param field_name: selection field name
        :param selection_option: the technical value of actual_state
        :return: string with the value that will be shown in the user
        """
        data = dict(self.fields_get().get(field_name).get("selection"))
        return data.get(selection_option, "")

    # @run_after_commit
    def send_invoice_mail(self):
        """Try to send the XML and Invoice report by email to customer.
        If a problem is found, a new message will be added
        with the error in the invoice."""
        for record in self:
            if not record.partner_id.email:
                record.message_post(
                    subject=_("Error when try send invoice by email"),
                    body=_(
                        "<h2>Error when try send invoice by email</h2>"
                        "<hr>Partner have not email. Please set that value."
                        "</hr>"
                    ),
                )
                continue
            message = record.action_invoice_sent()
            mail = (
                self.env["mail.compose.message"]
                .with_context(message.get("context", {}))
                .create({})
            )
            tmp = self.env.ref("account.email_template_edi_invoice", False)
            # If not wkhtmltopdf executable of some error in the onchange
            # (for example trying to render the email custom template) the
            # invoice can be signed but not updated the invoice record, this
            # need to be managed more secure, that's why this try.
            data = {}
            errored = False
            try:
                data = mail.onchange_template_id(
                    tmp.id, None, "account.move", record.id
                ).get("value", {})
            except BaseException as e:
                _logger.info("invoice not sent even if configured. %s")
                data.update({"subject": str(e)})
                errored = True
            mail.write(
                {
                    "body": data.get(
                        "body",
                        "Invoice not sent because an "
                        "error rendering or generating "
                        "the email",
                    ),
                    "partner_ids": data.get("partner_ids", []),
                    "email_from": data.get("email_from", ""),
                    "attachment_ids": data.get("attachment_ids", []),
                    "subject": data.get("subject", ""),
                }
            )
            mail.with_context(mark_invoice_as_sent=True).send_mail()
            mail = self.env["mail.mail"].search(
                [
                    ("res_id", "=", record.id),
                    ("model", "=", record._name),
                    ("subject", "=", data.get("subject", "")),
                ],
                limit=1,
            )
            if not mail or errored:
                continue
            record.write({"sent": False})
            record.message_post(
                subject=_("Error when try send invoice by email"),
                # Validate that mail exists, because the search can return a
                # mails list with some False
                body="<br>".join(
                    [
                        "- " + msg.failure_reason
                        for msg in mail
                        if msg.failure_reason
                    ]
                ),
            )

    def my_invoices_zip(self):
        invoice_xml = self.l10n_mx_edi_retrieve_last_attachment()
        attachment_id = ""
        invoice_pdf = self.retrieve_last_invoice()

        attachments_exists = self.retrieve_invoices_zip()

        if attachments_exists:
            attachment_id = attachments_exists
        elif invoice_xml is not None and invoice_pdf is not None:
            attachment_id = self.create_zip(invoice_xml, invoice_pdf)
        elif invoice_xml is not None and invoice_pdf is None:
            attachment_id = invoice_xml
        else:
            attachment_id = invoice_pdf

        return attachment_id

    def retrieve_invoices(self):
        domain = [
            ("res_id", "=", self.id),
            ("res_model", "=", "account.move"),
            ("mimetype", "=", "application/pdf"),
            ("name", "like", "%.pdf"),
        ]
        return self.env["ir.attachment"].search(domain)

    def retrieve_last_invoice(self):
        attachment_ids = self.retrieve_invoices()
        return attachment_ids and attachment_ids[0] or None

    def retrieve_invoices_zip(self):
        domain = [
            ("res_id", "=", self.id),
            ("mimetype", "=", "application/zip"),
        ]
        attachments = self.env["ir.attachment"].search(domain)
        return attachments

    def create_zip(self, invoice_xml, invoice_pdf):
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, "w") as myzip:
            myzip.writestr(
                invoice_xml.name, base64.b64decode(invoice_xml.datas)
            )
            myzip.writestr(
                invoice_pdf.name, base64.b64decode(invoice_pdf.datas)
            )
            myzip.close()
            zip_name = invoice_xml.name.replace(".xml", ".zip")
            values = {
                "name": zip_name,
                "type": "binary",
                "mimetype": "application/zip",
                "public": False,
                "db_datas": base64.b64encode(zip_stream.getvalue()),
                "res_id": invoice_xml.res_id,
                "datas_fname": zip_name,
            }
        attachment_id = self.env["ir.attachment"].create(values)
        return attachment_id

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        """Use the pos order usage and payment method"""
        usage = self.l10n_mx_edi_usage or self.partner_id.l10n_mx_edi_usage
        payment_method = (
            self.l10n_mx_edi_payment_method_id
            or self.partner_id.l10n_mx_edi_payment_method_id
        )
        res = super()._onchange_partner_id()
        if self._context.get("l10n_mx_edi_avoid_partner_defaults", False):
            self.update(
                {
                    "l10n_mx_edi_usage": usage,
                    "l10n_mx_edi_payment_method_id": payment_method.id,
                }
            )
        return res
