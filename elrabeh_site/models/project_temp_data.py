from odoo import models, fields

class ProjectTempData(models.Model):
    _name = 'project.temp.data'
    _description = 'Temporary Project Data'

    user_id = fields.Many2one('res.users', string='User', required=True, index=True, ondelete='cascade')

    name = fields.Char(string='Project Name')
    contract_value = fields.Float(string='Contract Value')
    address = fields.Char(string='Project Address')
    role = fields.Char(string='User Role')
    image = fields.Binary(string='Project Image')
    attachment = fields.Binary(string='Project Attachment')

    party_two_name = fields.Char(string='Party Two Name')
    party_two_role = fields.Char(string='Party Two Role')
    party_two_phone = fields.Char(string='Party Two Phone')
    party_two_email = fields.Char(string='Party Two Email')

    party_three_name = fields.Char(string='Party Three Name')
    party_three_role = fields.Char(string='Party Three Role')
    party_three_phone = fields.Char(string='Party Three Phone')
    party_three_email = fields.Char(string='Party Three Email')
