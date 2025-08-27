from odoo import models, fields

class ProjectProject(models.Model):
    _inherit = 'project.project'

    # ربط بالمشروع
    sale_order_id = fields.Many2one('sale.order', string="Related Sale Order")

    # بيانات المشروع
    project_name = fields.Char(string="Project Name")
    installments_count = fields.Integer(string="عدد الدفعات", default=1)

    contract_value = fields.Float(string="Contract Value")
    project_address = fields.Char(string="Project Address")
    user_role = fields.Char(string="User Role")
    project_image = fields.Binary(string="Project Image")
    project_attachment = fields.Binary(string="Project Attachment")
    project_attachment_filename = fields.Char(string="Attachment Filename")

    owner_name = fields.Char(string="Owner Name")
    owner_email = fields.Char(string="Owner Email")
    owner_phone = fields.Char(string="Owner Phone")
    owner_role = fields.Char(string="Owner Role")
    owner_approved = fields.Boolean(string="Owner Approved")

    consultant_name = fields.Char(string="Consultant Name")
    consultant_email = fields.Char(string="Consultant Email")
    consultant_phone = fields.Char(string="Consultant Phone")
    consultant_role = fields.Char(string="Consultant Role")
    consultant_approved = fields.Boolean(string="Consultant Approved")

    contractor_name = fields.Char(string="Contractor Name")
    contractor_email = fields.Char(string="Contractor Email")
    contractor_phone = fields.Char(string="Contractor Phone")
    contractor_role = fields.Char(string="Contractor Role")
    contractor_approved = fields.Boolean(string="Contractor Approved")
    # ربط المشروع بدفعات خصه بيه
    installment_ids = fields.One2many(
        "project.installment", "project_id", string="Installments"
    )
