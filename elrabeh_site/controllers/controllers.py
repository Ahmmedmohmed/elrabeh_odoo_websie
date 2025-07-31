from odoo import http
from odoo.http import request
from odoo import _, api, models
from odoo.addons.website_sale.controllers.main import WebsiteSale

import datetime
from datetime import datetime, timedelta
import json
import logging

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request, route






class QamarWebsite(http.Controller):


    @http.route('/', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def website_home(self, **kw):
        return http.request.render('elrabeh_site.home' )

    @http.route('/account', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def account_management(self, **kw):
        return http.request.render('elrabeh_site.account_management', {})

    @http.route('/service/details', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def service_details(self, **kw):
        return http.request.render('elrabeh_site.service_details', {})

    @http.route('/freqQues', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def quesAr(self, **kw):
        return http.request.render('elrabeh_site.askedQuestionsAr', {})


    @http.route('/bookFreeApp', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def freeAr(self, **kw):
        return http.request.render('elrabeh_site.freeBook', {})

    @http.route('/contactus', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def contact(self, **kw):
        return http.request.render('elrabeh_site.contact_us', {})

    @http.route('/aboutRabeh', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def profile(self, **kw):
        return http.request.render('elrabeh_site.about_us', {})

    @http.route('/ourservices', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def ourServices(self, **kw):
        return http.request.render('elrabeh_site.our_services', {})

    @http.route('/serviceOrder', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def services(self, **kw):
        return http.request.render('elrabeh_site.service_order', {})

    @http.route('/affiliate-area', type='http', auth='public', website=True)
    def render_events_page(self, **kwargs):


        return http.request.render('elrabeh_site.affiliate-area', {

        })


    @http.route('/signin', type='http', auth='public', methods=['GET'], csrf=False, website=True)
    def services(self, **kw):
        return http.request.render('elrabeh_site.signin_in', {})
    #
    # @http.route(['/shop'], type='http', auth="public", website=True)
    #
    # def shop_with_affiliate(self, **kwargs):
    #     affiliate = kwargs.get('utm_source')
    #     if affiliate:
    #         request.session['affiliate_code'] = affiliate
    #
    #     # هنا بنستدعي الصفحة الأصلية بدون تعديل
    #     return request.render("website_sale.products", {})

    @http.route('/affiliate/register', type='http', auth="public", website=True, csrf=False)
    def register_affiliate(self, **post):
        required_fields = ['name', 'username', 'email', 'payment_email']
        if all(post.get(field) for field in required_fields):
            request.env['elrabeh.affiliate.request'].sudo().create({
                'name': post.get('name'),
                'username': post.get('username'),
                'email': post.get('email'),
                'payment_email': post.get('payment_email'),
                'website_url': post.get('website_url', ''),
                'user_id': request.env.user.id,
                'promotion_method': post.get('promotion_method', ''),
            })
            return request.render("elrabeh_site.affiliate_thanks")
        return request.redirect('/')

    @http.route('/affiliate/link', type='http', auth='user', website=True)
    def affiliate_link_page(self):
        return request.render('elrabeh_site.affiliate_link_page')

    @http.route(['/shop/payment/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation_custom(self, **post):
        order = request.website.sale_get_order()
        if order and order.state in ['draft', 'sent']:
            order.action_confirm()
            order._compute_affiliate_commission()
            print(f"✅ Order confirmed & commission computed: {order.name}")
        return request.render("website_sale.confirmation", {'order': order})

    @http.route('/vendor/signup', type='http', auth="public", website=True, csrf=False)
    def vendor_signup(self, **post):
        name = post.get('name')
        email = post.get('email')
        password = post.get('password')

        # تحقق إن الإيميل مش مكرر
        existing_user = request.env['res.users'].sudo().search([('login', '=', email)])
        if existing_user:
            return request.render("your_module.signup_error", {'error': "Email already exists"})

        # إنشاء Partner
        partner = request.env['res.partner'].sudo().create({
            'name': name,
            'email': email,
        })

        # إنشاء User وربطه بمجموعة Vendor
        user = request.env['res.users'].sudo().create({
            'name': name,
            'login': email,
            'password': password,
            'partner_id': partner.id,
            'groups_id': [(6, 0, [request.env.ref('your_marketplace_module.group_marketplace_seller').id])],
        })

        # إنشاء سجل البائع وربطه بالمستخدم
        request.env['marketplace.seller'].sudo().create({
            'name': name,
            'user_id': user.id,
            'partner_id': partner.id,
        })

        return request.redirect('/web/login')

    @http.route('/buildmyproject', type='http', auth='user', csrf=False,website=True)
    def build_project_page(self, **kwargs):
        user = request.env.user
        projects = request.env['build.project'].sudo().search([('user_id', '=', user.id)])
        return request.render('elrabeh_site.build_project_page', {
            'projects': projects,
        })

    @http.route('/my/project/create', type='http', auth='user', website=True, csrf=False, methods=['POST'])
    def create_project(self, **post):
        project_name = post.get('project_name')
        if project_name:
            request.env['build.project'].sudo().create({
                'name': project_name,
                'user_id': request.env.user.id
            })
        return request.redirect('/my/build')

    @http.route('/my/build', type='http', auth='user', website=True)
    def my_build_projects(self, **kwargs):
        user_projects = request.env['build.project'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ])
        return request.render('elrabeh_site.build_project_template', {
            'projects': user_projects
        })

    @http.route('/my/project/<int:project_id>', type='http', auth='user', website=True)
    def view_project(self, project_id, **kwargs):
        project = request.env['build.project'].sudo().browse(project_id)
        if not project or project.user_id.id != request.env.user.id:
            return request.redirect('/my/build')

        categories = request.env['product.public.category'].sudo().search([])
        products_by_category = []
        for cat in categories:
            products = request.env['product.product'].sudo().search([
                ('public_categ_ids', 'in', cat.id)
            ])
            products_by_category.append({
                'category': cat,
                'products': products,
            })

        return request.render('elrabeh_site.build_project_detail_page', {
            'project': project,
            'products_by_category': products_by_category,
        })

    @http.route('/add_product_to_project/<int:project_id>/<int:product_id>', type='http', auth='user', website=True)
    def add_product_to_project(self, project_id, product_id, **kwargs):
        project = request.env['build.project'].sudo().browse(project_id)
        product = request.env['product.product'].sudo().browse(product_id)
        if project and product and request.env.user.id == project.user_id.id:
            project.write({'product_ids': [(4, product.id)]})
        return request.redirect('/my/project/%s' % project_id)

    @http.route('/remove_product_from_project/<int:project_id>/<int:product_id>', type='http', auth='user',
                website=True)
    def remove_product_from_project(self, project_id, product_id, **kwargs):
        project = request.env['build.project'].sudo().browse(project_id)
        product = request.env['product.product'].sudo().browse(product_id)
        if project and product and request.env.user.id == project.user_id.id:
            project.write({'product_ids': [(3, product.id)]})
        return request.redirect('/my/project/%s' % project_id)

    @http.route('/add_to_cart/<int:project_id>', type='http', auth='user', website=True)
    def add_to_cart(self, project_id, **kwargs):
        order = request.website.sale_get_order()
        project = request.env['build.project'].sudo().browse(project_id)
        for product in project.product_ids:
            order._cart_update(product_id=product.id, add_qty=1)
        return request.redirect('/shop/cart')

    @http.route('/remove_from_cart/<int:project_id>', type='http', auth='user', website=True)
    def remove_from_cart(self, project_id, **kwargs):
        order = request.website.sale_get_order()
        project = request.env['build.project'].sudo().browse(project_id)
        for line in order.order_line:
            if line.product_id.id in project.product_ids.ids:
                line.unlink()
        return request.redirect('/shop/cart')

    @http.route('/mangeyproject', type='http', auth='user', website=True)
    def affiliate_link_page(self):
        return request.render('elrabeh_site.mange_project_page')



class WebsiteSaleCustom(WebsiteSale):

    @http.route(['/shop', '/ar/shop'], type='http', auth="public", website=True)
    def shop_with_affiliate(self, **kwargs):
        # تخزين قيم UTM في الجلسة
        utm_source = kwargs.get('utm_source')
        utm_medium = kwargs.get('utm_medium')
        utm_campaign = kwargs.get('utm_campaign')

        if utm_source:
            request.session['utm_source'] = utm_source
        if utm_medium:
            request.session['utm_medium'] = utm_medium
        if utm_campaign:
            request.session['utm_campaign'] = utm_campaign
        print("=== UTM DEBUG ===")
        print(f"utm_source: {kwargs.get('utm_source')}")
        print(f"utm_medium: {kwargs.get('utm_medium')}")
        print(f"utm_campaign: {kwargs.get('utm_campaign')}")

        return super().shop(**kwargs)


class CustomSignup(AuthSignupHome):

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        street = kw.get('street')
        street2 = kw.get('street2')

        # استدعاء الميثود الأصلية للتسجيل
        response = super(CustomSignup, self).web_auth_signup(*args, **kw)

        print("تسجيل الدخول بتحمل ")

        # بعد إنشاء المستخدم، نعدل الـ partner المرتبط به
        if request.session.uid:
            user = request.env['res.users'].sudo().browse(request.session.uid)
            if user.partner_id:
                user.partner_id.write({
                    'street': street,
                    'street2': street2,
                })
        return response