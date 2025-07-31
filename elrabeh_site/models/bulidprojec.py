from odoo import models, fields

class BuildProject(models.Model):
    _name = 'build.project'
    _description = 'Build Project'

    name = fields.Char(string="Project Name")
    user_id = fields.Many2one('res.users', string="User")

    product_ids = fields.Many2many(
        'product.product',
        'build_project_product_rel',  # ← جدول علاقة مختلف
        'build_id',
        'product_id',
        string='Products'
    )

    purchased_product_ids = fields.Many2many(
        'product.product',
        'build_project_purchased_product_rel',  # ← جدول مختلف عن السابق
        'build_id',
        'product_id',
        string='Purchased Products'
    )
