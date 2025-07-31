from odoo import models, fields, api
from odoo.http import request


class AffiliateRequest(models.Model):
    _name = 'elrabeh.affiliate.request'
    _description = 'Affiliate Registration Request'

    name = fields.Char(string="Full Name", required=True)
    username = fields.Char(string="Username", required=True)
    email = fields.Char(string="Account Email", required=True)
    payment_email = fields.Char(string="Payment Email", required=True)
    website_url = fields.Char(string="Website URL")
    promotion_method = fields.Text(string="Promotion Method")
    user_id = fields.Integer(string="User ID", required=True)
    commission_rate = fields.Float(string="Commission Rate (%)", required=True, default=10.0)

    order_ids = fields.One2many('sale.order', 'affiliate_id', string="Affiliate Orders")

    amount_of_commission = fields.Float(
        string="Amount of Commission",
        compute="_compute_amount_of_commission",
        store=True
    )

    tracking_url = fields.Char(string="Affiliate Link", readonly=True)

    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending', string="Status")

    @api.depends('order_ids.affiliate_commission')
    def _compute_amount_of_commission(self):
        for rec in self:
            rec.amount_of_commission = sum(
                order.affiliate_commission for order in rec.order_ids if order.state in ['sale', 'done']
            )

    def action_approve(self):
        for rec in self:
            rec.state = 'approved'
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            full_url = f"{base_url}/shop?utm_source={rec.user_id}"
            utm_source = self.env['utm.source'].sudo().search([('name', '=', str(rec.user_id))], limit=1)
            if not utm_source:
                utm_source = self.env['utm.source'].sudo().create({'name': str(rec.user_id)})

            tracker = self.env['link.tracker'].sudo().create({
                'url': full_url,
                'source_id': utm_source.id,
                'medium_id': rec.create_uid.id,
                'campaign_id': rec.create_uid.id,
            })

            rec.tracking_url = tracker.short_url

            # تحديث العمولة للطلبات المؤكدة سابقًا
            for order in rec.order_ids:
                if order.state in ['sale', 'done']:
                    order.affiliate_commission = order.amount_total * (rec.commission_rate / 100.0)

    def action_reject(self):
            for rec in self:
                rec.state = 'rejected'

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    affiliate_id = fields.Many2one('elrabeh.affiliate.request', string='Affiliate')
    affiliate_commission = fields.Float(
        string='Commission',
        compute='_compute_affiliate_commission',
        store=True
    )

    @api.depends('amount_total', 'affiliate_id', 'state')
    def _compute_affiliate_commission(self):
        for order in self:
            if order.affiliate_id and order.state in ['sale', 'done']:
                rate = order.affiliate_id.commission_rate or 0.0
                order.affiliate_commission = order.amount_total * (rate / 100.0)
            else:
                order.affiliate_commission = 0.0

    @api.model
    def create(self, vals):
        print("📦 [CREATE] Starting order creation...")
        if not vals.get('source_id'):
            utm_source_val = request.session.get('utm_source') if request and hasattr(request, 'session') else None
            print(f"🔍 [SESSION] UTM Source from session: {utm_source_val}")
            if utm_source_val:
                utm_source = self.env['utm.source'].sudo().search([('name', '=', str(utm_source_val))], limit=1)
                if utm_source:
                    vals['source_id'] = utm_source.id
                    try:
                        user_id = int(utm_source.name)
                        affiliate = self.env['elrabeh.affiliate.request'].sudo().search([
                            ('user_id', '=', user_id), ('state', '=', 'approved')
                        ], limit=1)
                        if affiliate:
                            vals['affiliate_id'] = affiliate.id
                            print(f"🤝 [AFFILIATE] Linked with: {affiliate.name} (ID: {affiliate.id})")
                    except Exception as e:
                        print(f"❌ [ERROR] Invalid UTM Source name: {utm_source.name}, Error: {e}")
        return super().create(vals)

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            if order.affiliate_id:
                rate = order.affiliate_id.commission_rate or 0.0
                order.affiliate_commission = order.amount_total * (rate / 100.0)
                print(f"✅ [COMMISSION] Affiliate Commission for Order {order.name}: {order.affiliate_commission}")
        return res


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    affiliate_id = fields.Many2one('elrabeh.affiliate.request', string='Affiliate')
    affiliate_commission = fields.Float(string="Affiliate Commission")

    def _confirm_and_assign(self):
        res = super()._confirm_and_assign()
        for tx in self:
            utm_source = request.session.get('utm_source')
            affiliate = None
            if utm_source:
                affiliate = self.env['elrabeh.affiliate.request'].sudo().search([
                    ('user_id', '=', int(utm_source)), ('state', '=', 'approved')
                ], limit=1)
                if affiliate:
                    tx.affiliate_id = affiliate
                    tx.affiliate_commission = tx.amount * (affiliate.commission_rate / 100.0)
                    print(f"💸 [TX] Affiliate '{affiliate.name}' gets commission: {tx.affiliate_commission}")
            else:
                print("⚠️ [SESSION] No utm_source in session.")

            # تأكيد الطلبات المرتبطة
            for order in tx.sale_order_ids:
                if order.state in ['draft', 'sent']:
                    print(f"🧾 [ORDER] Confirming Order from Transaction: {order.name}")
                    order.action_confirm()

                if affiliate:
                    order.affiliate_id = affiliate
                    order.affiliate_commission = order.amount_total * (affiliate.commission_rate / 100.0)

                    # تحديث إجمالي عمولة الأفلييت
                    affiliate.amount_of_commission = sum(
                        o.affiliate_commission for o in affiliate.order_ids if o.state in ['sale', 'done']
                    )
                    print(f"📊 [UPDATE] Total Commission for {affiliate.name}: {affiliate.amount_of_commission}")

        return res
