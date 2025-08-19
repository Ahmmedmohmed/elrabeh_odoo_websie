from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    in_platform = fields.Boolean(string='In Platform', default=False)
