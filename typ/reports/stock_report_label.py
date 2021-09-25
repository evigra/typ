from odoo import api, models


class ReportZebraProduct(models.AbstractModel):

    _name = "report.typ.product_label_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    @api.model
    def render_html(self, docids, data=None):
        if data is None:
            data = {}

        datas = {"docs": self.env["product.product"].browse(data.get("ids", docids)), "qty": data.get("qty", 1)}
        return self.env["report"].render("typ.product_label_zebra_view", datas)

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraProductM(models.AbstractModel):

    _name = "report.typ.product_label_medium_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    @api.model
    def render_html(self, docids, data=None):
        if data is None:
            data = {}

        datas = {"docs": self.env["product.product"].browse(data.get("ids", docids)), "qty": data.get("qty", 1)}
        return self.env["report"].render("typ.product_label_zebra_view", datas)

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraProductE(models.AbstractModel):

    _name = "report.typ.product_label_extra_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    @api.model
    def render_html(self, docids, data=None):
        if data is None:
            data = {}

        datas = {"docs": self.env["product.product"].browse(data.get("ids", docids)), "qty": data.get("qty", 1)}
        return self.env["report"].render("typ.product_label_zebra_view", datas)

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraRack(models.AbstractModel):

    _name = "report.typ.rack_label_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraRackM(models.AbstractModel):

    _name = "report.typ.rack_label_medium_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraRackE(models.AbstractModel):

    _name = "report.typ.rack_label_extra_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraImportUSA(models.AbstractModel):

    _name = "report.typ.import_usa_label_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraImportCAN(models.AbstractModel):

    _name = "report.typ.import_can_label_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}


class ReportZebraImportUK(models.AbstractModel):

    _name = "report.typ.import_uk_label_zebra_view"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def _get_report_values(self, docids, data):
        products = self.env["product.product"].browse(docids)
        return {"doc_ids": products.ids, "docs": products, "data": data}
