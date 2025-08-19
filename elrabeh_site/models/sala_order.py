from email.policy import default

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # بيانات المشروع
    project_name = fields.Char(string="Project Name")
    contract_value = fields.Float(string="Contract Value")
    project_address = fields.Char(string="Project Address")
    user_role = fields.Char(string="User Role")
    project_image = fields.Binary(string="Project Image")
    project_attachment = fields.Binary(string="Project Attachment")
    project_attachment_filename = fields.Char(string="Attachment Filename")

    # بيانات الأطراف
    party_one_name = fields.Char(string="Party One Name")
    party_one_email = fields.Char(string="Party One Email")
    party_one_phone = fields.Char(string="Party One Phone")
    party_one_role = fields.Char(string="Party One Role")
    party_one_approved = fields.Boolean(string="Party One Approved")

    party_two_name = fields.Char(string="Party Two Name")
    party_two_email = fields.Char(string="Party Two Email")
    party_two_phone = fields.Char(string="Party Two Phone")
    party_two_role = fields.Char(string="Party Two Role")
    party_two_approved = fields.Boolean(string="Party Two Approved")

    party_three_name = fields.Char(string="Party Three Name")
    party_three_email = fields.Char(string="Party Three Email")
    party_three_phone = fields.Char(string="Party Three Phone")
    party_three_role = fields.Char(string="Party Three Role")
    party_three_approved = fields.Boolean(string="Party Three Approved")

    approval_token_party1 = fields.Char(string="Approval Token Party 1")
    approval_token_party2 = fields.Char(string="Approval Token Party 2")
    approval_token_party3 = fields.Char(string="Approval Token Party 3")
    #  الموافقة على التعديل
    party2_approved_mod_request = fields.Text(string="Party 2 Modification Request" , default="")
    party3_approved_mod_request = fields.Text(string="Party 3 Modification Request" , default="")
    party_mod_approved = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string="Modification Approval Status", default='pending')

    # حالة الموافقة
    party1_approved = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='approved')

    party2_approved = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')

    party3_approved = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')

    # كل الأطراف وافقت
    all_parties_approved = fields.Boolean(
        string="All Parties Approved",
        compute="_compute_all_approved",
        store=True
    )

    @api.depends('party1_approved', 'party2_approved', 'party3_approved')
    def _compute_all_approved(self):
        for order in self:
            order.all_parties_approved = (
                order.party1_approved == 'approved' and
                order.party2_approved == 'approved' and
                order.party3_approved == 'approved'
            )
            # أول ما كل الأطراف توافق → يتعمل Confirm أوتوماتيك
            if order.all_parties_approved and order.state not in ['sale', 'done', 'cancel']:
                order.action_confirm()
