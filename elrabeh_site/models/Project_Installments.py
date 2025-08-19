from odoo import models, fields, api
from odoo.exceptions import UserError

class ProjectInstallment(models.Model):
    _name = 'project.installment'
    _description = 'Project Installment'

    project_id = fields.Many2one('sale.order', string="Project", required=True)
    name = fields.Char(string="Installment Name")
    amount = fields.Float(string="Amount", required=True)
    percentage = fields.Float(string="Percentage", readonly=True)
    due_date = fields.Date(string="Due Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ], string="Status", default='draft', tracking=True)

    contractor_id = fields.Many2one('res.users', string="Contractor")
    owner_id = fields.Many2one('res.users', string="Owner", required=True)
    consultant_id = fields.Many2one('res.users', string="Consultant")

    @api.model
    def create(self, vals):
        """تأكد إن المالك بس هو اللي بيكريت الدفعات"""
        if self.env.user.id != vals.get('owner_id'):
            raise UserError("فقط المالك يمكنه إنشاء دفعة جديدة.")
        rec = super(ProjectInstallment, self).create(vals)
        rec._compute_percentage()
        return rec

    @api.onchange('amount')
    def _compute_percentage(self):
        """حساب النسبة من القيمة التعاقدية"""
        for rec in self:
            if rec.project_id.contract_value:
                rec.percentage = (rec.amount / rec.project_id.contract_value) * 100
