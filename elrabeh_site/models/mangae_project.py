from odoo import models, fields

class ManageProject(models.Model):
    _name = 'manage.project'
    _description = 'Manage Project (Website Form)'

    name = fields.Char(string="اسم المشروع", required=True)
    contract_value = fields.Monetary(string="القيمة التعاقدية", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    address = fields.Text(string="العنوان")
    creator_id = fields.Many2one('res.users', string="منشئ المشروع")
    role = fields.Selection([
        ('owner', 'مالك'),
        ('contractor', 'مقاول'),
        ('consultant', 'استشاري'),
    ], string="الدور", required=True)
    attachment = fields.Binary(string="مرفق", attachment=True)
    image = fields.Image(string="صورة المشروع", max_width=1024, max_height=1024)

    def _compute_dynamic_price(self):
        for product in self:
            user_partner = self.env.user.partner_id

            # Check if product is marked as "in_platform"
            if product.in_platform:
                # Check if this partner bought this product before (confirmed orders only)
                previous_orders = self.env['sale.order.line'].search([
                    ('order_id.partner_id', '=', user_partner.id),
                    ('product_id.product_tmpl_id', '=', product.id),
                    ('order_id.state', 'in', ['sale', 'done']),
                ])
                if previous_orders:
                    product.list_price = 100
                else:
                    product.list_price = 0
