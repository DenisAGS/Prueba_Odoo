from odoo import _, api, fields, models, exceptions


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    company_type = fields.Selection(selection_add=[('is_school','Escuela'), ('student_id', 'Estudiante')])
    student_id = fields.Many2one('academia.student', 'Estudiante')

class academia_student(models.Model):
    _name="academia.student"
    _description ="Gestion de estudiante"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    
    #Funciones
    def _get_school_default(self):
        school_id = self.env['res.partner'].search([('name', '=', 'Escuela comodin')])
        return school_id 
    
    name = fields.Char("Nombre", size=128, required=True, track_visibility='onchange')
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
    curp = fields.Char("CURP", size=18, copy=False)
    
    #Relaciones
    partner_id = fields.Many2one('res.partner', 'Escuela', default=_get_school_default)
    calificaciones_id = fields.One2many('academia.calificacion', 'student_id', 'Calificaciones')
    country = fields.Many2one('res.country', 'Pais', related="partner_id.country_id")
    invoice_ids = fields.Many2many('account.move',
                                   'student_invoice_rel',
                                   'student_id', 'journal_id',
                                    'Facturas')
    
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
        
    def unlink(self):
        partner_obj = self.env['res.partner']
        partners = partner_obj.search([('student_id', 'in', self.ids)])
        print('partners: ', partners)
        if partners:
            for partner in partners:
                partner.unlink()
        res = super(academia_student, self).unlink()
        return res
        
    
    @api.constrains('curp')
    def _check_curp(self): 
        if len(self.curp) < 18:
            raise exceptions.ValidationError('La curp debe ser de 18 digitos')