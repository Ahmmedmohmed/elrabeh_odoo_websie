from odoo import models, fields, api
from odoo.exceptions import UserError
import uuid

class ProjectInstallment(models.Model):
    _name = 'project.installment'
    _description = 'Project Installment'
    _order = 'id desc'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    name = fields.Char(string="Installment Name", required=True)
    amount = fields.Float(string="Amount", required=True)
    percentage = fields.Float(string="Percentage", readonly=True, compute='_compute_percentage', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('consultant_approved', 'Consultant Approved'),
        ('owner_approved', 'Owner Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)

    contractor_id = fields.Many2one('res.users', string="Contractor")
    owner_id = fields.Many2one('res.users', string="Owner", required=True)
    consultant_id = fields.Many2one('res.users', string="Consultant")
    attachment_id = fields.Many2one('ir.attachment', string="Proof of Payment")
    confirm_token = fields.Char(string="Contractor Confirm Token", readonly=True)
    contractor_attachment_id = fields.Many2one(
        'ir.attachment',
        string="Contractor Attachment",
        help="ملف مرفق من المقاول عند طلب الدفعة (اختياري)."
    )

    @api.depends('amount', 'project_id')
    def _compute_percentage(self):
        for rec in self:
            total = rec.project_id.contract_value if rec.project_id else 0
            rec.percentage = (rec.amount / total) * 100 if total else 0.0

    # ---------- Actions ----------
    def action_request_payment(self):
        for rec in self:
            if self.env.user.email != rec.project_id.contractor_email:
                raise UserError("فقط المقاول يقدر يطلب الدفعة.")
            if rec.state != 'draft':
                raise UserError("لا يمكن طلب الدفع إلا من حالة مسودة (Draft).")

            # إنشاء التوكن عند الطلب
            token = str(uuid.uuid4())
            rec.sudo().write({'confirm_token': token, 'state': 'requested'})

            rec._email_owner_and_consultant_on_request()

    def action_consultant_approve(self):
        for rec in self:
            if self.env.user.email != rec.project_id.consultant_email:
                raise UserError("فقط الاستشاري يقدر يوافق.")
            if rec.state != 'requested':
                raise UserError("هذه الدفعة ليست في حالة طلب صرف.")
            rec.state = 'consultant_approved'

    def action_owner_approve(self):
        for rec in self:
            if self.env.user.email != rec.project_id.owner_email:
                raise UserError("فقط المالك يقدر يوافق.")
            if rec.state != 'consultant_approved':
                raise UserError("لا يمكن الموافقة قبل موافقة الاستشاري.")
            rec.state = 'owner_approved'

    def action_owner_reject(self):
        for rec in self:
            if self.env.user not in [rec.owner_id, rec.consultant_id]:
                raise UserError("فقط المالك أو الاستشاري يمكنهم الرفض.")
            if rec.state not in ('requested', 'consultant_approved'):
                raise UserError("لا يمكن الرفض في هذه الحالة.")
            rec.state = 'rejected'

    def action_owner_pay(self, attachment):
        for rec in self:
            if self.env.user.email != rec.project_id.owner_email:
                raise UserError("فقط المالك يقدر يدفع.")
            if rec.state != 'owner_approved':
                raise UserError("لا يمكن الدفع قبل موافقة الاستشاري والمالك.")
            if not attachment:
                raise UserError("من فضلك أرفع إثبات الدفع.")
            rec.write({
                'state': 'paid',
                'attachment_id': attachment.id,
            })
            rec._send_paid_email_to_contractor()

    def action_contractor_confirm(self, token):
        for rec in self:
            if not rec.confirm_token or token != rec.confirm_token:
                raise UserError("رابط تأكيد غير صالح.")
            if self.env.user != rec.contractor_id:
                raise UserError("فقط المقاول يقدر يأكد الاستلام.")
            if rec.state != 'paid':
                raise UserError("لا يمكن التأكيد قبل حالة الدفع.")
            rec.state = 'done'
            rec.confirm_token = False

    # ---------- Emails ----------
    def _email_owner_and_consultant_on_request(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            link_owner = f"{base_url}/owner/installments/{rec.project_id.id}"
            link_cons = f"{base_url}/consultant/installments/{rec.project_id.id}"
            subject = f"طلب صرف دفعة: {rec.name}"
            body = f"""
                <p>تم طلب صرف الدفعة <b>{rec.name}</b> للمشروع <b>{rec.project_id.name}</b>.</p>
                <p>المبلغ: <b>{rec.amount}</b></p>
                <p><a href="{link_cons}">مراجعة (الاستشاري)</a> | <a href="{link_owner}">مراجعة (المالك)</a></p>
            """
            emails = []
            if  rec.project_id.owner_email:
                emails.append(rec.project_id.owner_email)
            if  rec.project_id.consultant_email:
                emails.append(rec.project_id.consultant_email)
            if emails:
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_to': ",".join(emails),
                    'email_from': 'odooboot2025@gmail.com',
                    'model': 'project.installment',
                    'res_id': rec.id,
                }
                self.env['mail.mail'].sudo().create(mail_values).send()

    def _send_paid_email_to_contractor(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for rec in self:
            if not rec.contractor_id or not rec.contractor_id.partner_id.email:
                continue
            token = str(uuid.uuid4())
            rec.sudo().write({'confirm_token': token})
            link = f"{base_url}/contractor/confirm/{rec.id}/{token}"
            subject = f"تم دفع الدفعة: {rec.name}"
            body = f"""
                <p>تم دفع الدفعة <b>{rec.name}</b> للمشروع <b>{rec.project_id.name}</b>.</p>
                <p>من فضلك قم بتأكيد الاستلام عبر الرابط التالي:</p>
                <p><a href="{link}" style="background:#198754;color:#fff;padding:8px 14px;border-radius:6px;text-decoration:none;">تأكيد الاستلام</a></p>
            """
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': rec.contractor_id.partner_id.email,
                'email_from': 'odooboot2025@gmail.com',
                'model': 'project.installment',
                'res_id': rec.id,
            }
            self.env['mail.mail'].sudo().create(mail_values).send()
