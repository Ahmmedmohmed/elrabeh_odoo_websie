from email.policy import default

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # بيانات المشروع
    # بيانات المشروع
    project_name = fields.Char(string="Project Name")
    contract_value = fields.Float(string="Contract Value")
    project_address = fields.Char(string="Project Address")
    installments_count = fields.Integer(string="عدد الدفعات", default=1)


    user_role = fields.Selection([
        ('owner', 'مالك'),
        ('consultant', 'استشاري'),
        ('contractor', 'مقاول'),
    ], string="User Role")

    project_image = fields.Binary(string="Project Image")
    project_attachment = fields.Binary(string="Project Attachment")
    project_attachment_filename = fields.Char(string="Attachment Filename")

    # بيانات الأطراف
    party_one_name = fields.Char(string="Party One Name")
    party_one_email = fields.Char(string="Party One Email")
    party_one_phone = fields.Char(string="Party One Phone")
    party_one_role = fields.Selection([
        ('owner', 'مالك'),
        ('consultant', 'استشاري'),
        ('contractor', 'مقاول'),
    ], string="Party One Role")
    party_one_approved = fields.Boolean(string="Party One Approved")

    party_two_name = fields.Char(string="Party Two Name")
    party_two_email = fields.Char(string="Party Two Email")
    party_two_phone = fields.Char(string="Party Two Phone")
    party_two_role = fields.Selection([  # ✅ اتعدلت هنا
        ('owner', 'مالك'),
        ('consultant', 'استشاري'),
        ('contractor', 'مقاول'),
    ], string="Party Two Role")
    party_two_approved = fields.Boolean(string="Party Two Approved")

    party_three_name = fields.Char(string="Party Three Name")
    party_three_email = fields.Char(string="Party Three Email")
    party_three_phone = fields.Char(string="Party Three Phone")
    party_three_role = fields.Selection([
        ('owner', 'مالك'),
        ('consultant', 'استشاري'),
        ('contractor', 'مقاول'),
    ], string="Party Three Role")
    party_three_approved = fields.Boolean(string="Party Three Approved")  # ✅ اتعدلت

    approval_token_party1 = fields.Char(string="Approval Token Party 1")
    approval_token_party2 = fields.Char(string="Approval Token Party 2")
    approval_token_party3 = fields.Char(string="Approval Token Party 3")

    # موافقة التعديل
    party2_approved_mod_request = fields.Text(string="Party 2 Modification Request", default="")
    party3_approved_mod_request = fields.Text(string="Party 3 Modification Request", default="")
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

    #  نقل الحقول قيم المشروع من sala order  الى المشروع
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for order in self:
            # الحصول على المشروع أو إنشاء مشروع جديد لو مش موجود
            project = order.analytic_account_id.project_ids[:1]
            if not project:
                project = self.env['project.project'].create({
                    'name': order.project_name,
                    'sale_order_id': order.id,
                    'contract_value': order.contract_value,
                    'project_address': order.project_address,
                    'user_role': order.user_role,
                    'project_image': order.project_image,
                    'project_attachment': order.project_attachment,
                    'project_attachment_filename': order.project_attachment_filename,
                    'installments_count' : order.installments_count
                })
            else:
                project_vals = {
                    'name': order.project_name,
                    'contract_value': order.contract_value,
                    'project_address': order.project_address,
                    'user_role': order.user_role,
                    'project_image': order.project_image,
                    'project_attachment': order.project_attachment,
                    'project_attachment_filename': order.project_attachment_filename,
                    'installments_count' : order.installments_count
                }
                project.write(project_vals)

            # إنشاء خريطة للدور → البيانات
            role_map = {
                order.party_one_role: {
                    'name': order.party_one_name,
                    'email': order.party_one_email,
                    'phone': order.party_one_phone,
                    'role': order.party_one_role,
                    'approved': order.party_one_approved
                },
                order.party_two_role: {
                    'name': order.party_two_name,
                    'email': order.party_two_email,
                    'phone': order.party_two_phone,
                    'role': order.party_two_role,
                    'approved': order.party_two_approved
                },
                order.party_three_role: {
                    'name': order.party_three_name,
                    'email': order.party_three_email,
                    'phone': order.party_three_phone,
                    'role': order.party_three_role,
                    'approved': order.party_three_approved
                }
            }

            # كتابة البيانات في المشروع حسب الدور وإنشاء المستخدم + إرسال إيميل
            for role, vals in role_map.items():
                if not vals['name']:
                    continue

                project_vals = {}
                if role == 'owner':
                    project_vals = {
                        'owner_name': vals['name'],
                        'owner_email': vals['email'],
                        'owner_phone': vals['phone'],
                        'owner_role': vals['role'],
                        'owner_approved': vals['approved'],
                    }
                elif role == 'consultant':
                    project_vals = {
                        'consultant_name': vals['name'],
                        'consultant_email': vals['email'],
                        'consultant_phone': vals['phone'],
                        'consultant_role': vals['role'],
                        'consultant_approved': vals['approved'],
                    }
                elif role == 'contractor':
                    project_vals = {
                        'contractor_name': vals['name'],
                        'contractor_email': vals['email'],
                        'contractor_phone': vals['phone'],
                        'contractor_role': vals['role'],
                        'contractor_approved': vals['approved'],
                    }

                project.write(project_vals)

            # ✅ الطرف الأساسي (العميل الرئيسي)
            self._create_portal_user_and_send_mail(order.partner_id, order, base_url)

            # ✅ الطرف الثاني
            if order.party_two_email and order.party_two_name:
                user = self.env['res.users'].sudo().search([('login', '=', order.party_two_email)], limit=1)
                if not user:
                    user = self._create_portal_user_and_send_mail(
                        None, order, base_url,
                        email=order.party_two_email,
                        name=order.party_two_name
                    )

            # ✅ الطرف الثالث
            if order.party_three_email and order.party_three_name:
                user = self.env['res.users'].sudo().search([('login', '=', order.party_three_email)], limit=1)
                if not user:
                    user = self._create_portal_user_and_send_mail(
                        None, order, base_url,
                        email=order.party_three_email,
                        name=order.party_three_name
                    )

        return res

    def _create_portal_user_and_send_mail(self, partner, order, base_url, email=None, name=None):
        """Create portal user if not exists and send welcome email"""
        if not partner:
            # Create partner if only email+name provided
            partner = self.env['res.partner'].create({
                'name': name,
                'email': email,
            })

        # Check if partner already has a user
        user = self.env['res.users'].search([('partner_id', '=', partner.id)], limit=1)
        if not user:
            # Generate password
            password = "123123123"  # TODO: ممكن تخليه random عشان أمان أكتر

            # Create user
            user = self.env['res.users'].create({
                'name': partner.name,
                'login': partner.email,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])],
                'password': password,
            })

            # Send welcome email
            subject = "📌 You have been added to a new project"
            body_html = f"""
                <p>Hello <b>{partner.name}</b>,</p>
                <p>You have been added as a party to a new project related to the Sales Order <b>{order.name}</b>.</p>
                <p>Your account details are as follows:</p>
                <ul>
                    <li><b>Login:</b> {partner.email}</li>
                    <li><b>Temporary Password:</b> {password}</li>
                </ul>
                <p>Please log in to the system using the following link and change your password for security:</p>
                <p><a href="{base_url}/web/login">{base_url}/web/login</a></p>
                <br/>
                <p>Best regards,<br/>Your Project Team</p>
            """

            mail_values = {
                'subject': subject,
                'body_html': body_html,
                'email_from': 'odooboot2025@gmail.com',
                'email_to': partner.email,
                'res_id': order.id,
                'model': 'sale.order',
            }
            self.env['mail.mail'].sudo().create(mail_values).send()


