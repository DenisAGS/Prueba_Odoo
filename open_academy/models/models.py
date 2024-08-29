from odoo import _, api, fields, models, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    company_type = fields.Selection(selection_add=[('is_school','Escuela'), ('student_id', 'Estudiante')])
    student_id = fields.Many2one('academia.student', 'Estudiante')

class academia_student(models.Model):
    _name="academia.student"
    _description ="Gestion de estudiante"
    
    name = fields.Char("Nombre", size=128, required=True)
    lastname = fields.Char("Apellido", size=128)
    photo = fields.Binary('Fotografia')
    create_date = fields.Datetime('Fecha de creación', readonly=True)
    note = fields.Html('Comentarios')
    state = fields.Selection([
        ('draft', "Borrador"),
        ('done', "Egresado"),
        ('process', "En proceso"),
        ('cancel', "Expulsado")
    ], "Estado", default="draft")
    active = fields.Boolean("Activo", default=True)
    age = fields.Integer('Edad')
    curp = fields.Char("CURP", size=18, required=True)
    
    #Relaciones
    partner_id = fields.Many2one('res.partner', 'Escuela')
    calificaciones_id = fields.One2many('academia.calificacion', 'student_id', 'Calificaciones')
    country = fields.Many2one('res.country', 'Pais', related="partner_id.country_id")
    
    @api.model
    def create(self, values):
        if values['name']:
            nombre = values['name']
            if self.env['academia.student'].search([('name', '=', self.name)]):
                values.update({
                    'name' : values['name']+"(copy)"
                })
            res = super(academia_student, self).create(values)
            partner_obj = self.env['res.partner']
            vals_to_partner = {
                'name': res['name']+" "+res['lastname'],
                'company_type': "student_id",
                'student_id': res['id'],
            }
            print(vals_to_partner)
            partner = partner_obj.create(vals_to_partner)
            print('==> partner_id ', partner)
            return res
    
    @api.constrains('curp')
    def _check_curp(self):
        if len(self.curp) < 18:
            raise exceptions.ValidationError('La curp debe ser de 18 digitos')