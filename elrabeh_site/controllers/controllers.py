from odoo import http
from odoo.http import request
from odoo import _, api, models
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http, models, fields
import logging
from odoo.exceptions import UserError
import base64
_logger = logging.getLogger(__name__)

import uuid



import datetime
from datetime import datetime, timedelta
import json
import logging

from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request, route
import uuid







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
        user = request.env.user
        Project = request.env['build.project'].sudo()
        SaleOrder = request.env['sale.order'].sudo()
        Product = request.env['product.product'].sudo()

        # اسم المنتج اللي بيمنح صلاحية إنشاء مشروع جديد
        product_name = "ابني مشروعك"
        product = Product.search([('name', '=', product_name)], limit=1)

        if not product:
            # إنشاء المنتج تلقائياً إذا مش موجود
            product = Product.create({
                'name': product_name,
                'type': 'service',
                'list_price': 100.0,  # عدل السعر حسب ما تريد
            })

        # تحقق إذا كان لدى المستخدم مشاريع بالفعل
        existing_projects = Project.search([('user_id', '=', user.id)], limit=1)

        if existing_projects:
            # تأكد إن المستخدم اشترى المنتج
            orders = SaleOrder.search([
                ('partner_id', '=', user.partner_id.id),
                ('state', 'in', ['sale', 'done']),
                ('order_line.product_id', '=', product.id)
            ], limit=1)

            if not orders:
                # لم يشتري المنتج → تحويله إلى صفحة شراء المنتج
                return request.redirect(f'/shop/{product.id}')

        # إنشاء المشروع
        if project_name:
            Project.create({
                'name': project_name,
                'user_id': user.id
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

        # كل منتجات المتجر مصنفة حسب التصنيفات
        products_by_category = []
        for cat in categories:
            products = request.env['product.product'].sudo().search([
                ('public_categ_ids', 'in', cat.id)
            ])
            products_by_category.append({
                'category': cat,
                'products': products,
            })

        # ✅ منتجات المشروع فقط مصنفة حسب التصنيفات
        my_products_by_category = []
        for cat in categories:
            my_products = project.product_ids.filtered(lambda p: cat.id in p.public_categ_ids.ids)
            if my_products:
                my_products_by_category.append({
                    'category': cat,
                    'products': my_products,
                })

        return request.render('elrabeh_site.build_project_detail_page', {
            'project': project,
            'products_by_category': products_by_category,
            'my_products_by_category': my_products_by_category,  # الجديد
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
        order = request.website.sale_get_order(force_create=1)
        project = request.env['build.project'].sudo().browse(project_id)

        if not project.exists():
            return request.not_found()

        for product in project.product_ids:
            order._cart_update(product_id=product.id, add_qty=1)
        return request.redirect('/shop/cart')

    @http.route('/remove_from_cart/<int:project_id>', type='http', auth='user', website=True)
    def remove_from_cart(self, project_id, **kwargs):
        order = request.website.sale_get_order()
        project = request.env['build.project'].sudo().browse(project_id)

        if not project.exists():
            return request.not_found()

        for line in order.order_line:
            if line.product_id.id in project.product_ids.ids:
                line.unlink()
        return request.redirect('/shop/cart')

    @http.route(['/my/build_project/confirm_add'], type='http', auth='user', methods=['POST'], csrf=False)
    def confirm_add_product(self, **post):
        product_id = int(post.get('product_id', 0))
        project_id = int(post.get('project_id', 0))
        _logger = logging.getLogger(__name__)
        _logger.info(f"[Confirm Add] product_id: {product_id}, project_id: {project_id}")

        Product = request.env['product.product'].sudo()
        Project = request.env['build.project'].sudo()

        product = Product.browse(product_id)
        project = Project.browse(project_id)

        if product in project.product_ids:

            request.session['add_product_message'] = f"⚠️ المنتج  مضاف بالفعل للمشروع."
        else:
            project.write({'product_ids': [(4, product.id)]})
            request.session['add_product_message'] = f"✅ تم إضافة المنتج للمشروع بنجاح "

        return request.redirect(f'/my/project/{project_id}')

    @http.route(['/my/build_project/add_product'], type='http', auth='user', methods=['POST'], csrf=False ,website=True)
    def add_product_to_project_from_Shop(self, **post):
        product_id = int(post.get('product_id'))
        user = request.env.user

        # نجيب المشاريع بتاعت المستخدم
        user_projects = request.env['build.project'].sudo().search([('user_id', '=', user.id)])

        if user_projects:
            # لو عنده مشاريع، نعرض صفحة اختيار مشروع
            return request.render('elrabeh_site.select_project_template', {
                'product_id': product_id,  # حوله لـ str عشان يظهر في التيمبلت
                'projects': user_projects,
            })


        else:
            # مفيش مشاريع؟ يروح ينشئ مشروع جديد
            return request.redirect('/my/build_project/create')


    ########## mange my project #############

    @http.route('/project/approve/<string:token>', type='http', auth='public', website=True)
    def project_approve_page(self, token, **kwargs):
        order = request.env['sale.order'].sudo().search([
            '|',
            ('approval_token_party2', '=', token),
            ('approval_token_party3', '=', token)
        ], limit=1)

        if not order:
            return request.render('elrabeh_site.approval_invalid')

        # تحديد الطرف
        party = 'party2' if order.approval_token_party2 == token else 'party3'

        return request.render('elrabeh_site.approval_page', {
            'order': order,
            'party': party,
            'token': token
        })
 #  الموافقة او الرفض او طلب تعديل
    @http.route('/project/respond', type='http', auth='public', website=True, csrf=False)
    def project_respond(self, **post):
        token = post.get('token')
        action = post.get('action')  # approved / rejected / approve_with_mod
        mod_request = post.get('mod_request', False)

        order = request.env['sale.order'].sudo().search([
            '|',
            ('approval_token_party2', '=', token),
            ('approval_token_party3', '=', token)
        ], limit=1)

        if order:
            # تحديد الطرف
            if order.approval_token_party2 == token:
                party_field = 'party2_approved'
                party_name = order.party_two_name
            elif order.approval_token_party3 == token:
                party_field = 'party3_approved'
                party_name = order.party_three_name
            else:
                party_field = None

            if party_field:
                if action == 'approve_with_mod' and mod_request:
                    # حفظ طلب التعديل وحالة خاصة
                    order.sudo().write({
                        party_field: 'pending',  # حالة جديدة
                        f'{party_field}_mod_request': mod_request if hasattr(order,
                                                                             f'{party_field}_mod_request') else False
                    })

                    # إرسال إيميل للطرف الأول (مالك المشروع)
                    body_mail = f"""
                    <p>Hello <b>{order.party_one_name}</b>,</p>
                    <p><b>{party_name}</b> has requested modifications for the project <b>{order.project_name}</b>.</p>
                    <p><b>Requested Changes:</b></p>
                    <p>{mod_request}</p>
                    <p>Please review and approve or reject the modification in your portal.</p>
                    """

                    mail_values = {
                        'subject': f"📌 Modification Request from {party_name}",
                        'body_html': body_mail,
                        'email_from': 'odooboot2025@gmail.com',
                        'email_to': order.party_one_email,
                        'res_id': order.id,
                        'model': 'sale.order',
                    }
                    mail = request.env['mail.mail'].sudo().create(mail_values)
                    mail.sudo().send()
                else:
                    # الحالة العادية approve / reject
                    order.sudo().write({party_field: action})

        return request.render('elrabeh_site.approval_thanks')

    # الموافقة او الرفض على التعديل

    @http.route('/project/mod_review/<int:order_id>/<string:party>', type='http', auth='public', website=True,
                csrf=False)
    def mod_review_page(self, order_id, party, **post):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order:
            return request.render('elrabeh_site.approval_invalid')

        if post.get('action') in ['approved', 'rejected']:
            # تنفيذ التعديل لو وافق
            if post.get('action') == 'approved':
                if party == 'party2':
                    # هنا نطبق التعديل على المشروع تلقائيًا حسب نص طلب التعديل
                    # مثال: تعديل اسم المشروع أو أي حقل حسب طلب الطرف 2
                    # order.write({'project_name': order.party2_mod_request})
                    order.party_mod_approved = 'approved'
                elif party == 'party3':
                    order.party_mod_approved = 'approved'
            else:
                order.party_mod_approved = 'rejected'
            return request.render('elrabeh_site.mod_review_thanks')

        # الصفحة تعرض نص التعديل
        mod_text = order.party2_mod_request if party == 'party2' else order.party3_mod_request
        return request.render('elrabeh_site.mod_review_page', {
            'order': order,
            'party': party,
            'mod_text': mod_text
        })

    @http.route('/mangeyproject', type='http', auth='user', website=True)
    def affiliate_link_page(self):
        user = request.env.user
        # البحث عن منتج المشروع - مثلاً المنتج اللي عنده in_platform = True
        product = request.env['product.product'].sudo().search([('in_platform', '=', True)], limit=1)

        if product:
            # ابحث إذا عنده طلب بيع مرتبط بالمنتج ده
            sale_order = request.env['sale.order'].sudo().search([
                ('partner_id', '=', user.partner_id.id),
                ('order_line.product_id', '=', product.id)
            ], limit=1)

            if sale_order:
                # لو موجود طلب بيع بالمشروع، يروح للصفحة الخاصة بالمشاريع
                return request.redirect('/my-projects')

        # لو مفيش طلب بيع مرتبط بالمشروع، عرض النموذج عادي مع البيانات المؤقتة (لو موجودة)
        temp = request.env['project.temp.data'].sudo().search([('user_id', '=', user.id)], limit=1)
        values = {}
        if temp:
            values = {
                'name': temp.name,
                'contract_value': temp.contract_value,
                'address': temp.address,
                'role': temp.role,
                'image': temp.image,
                'attachment': temp.attachment,
                'installments_count' : temp.installments_count,
            }
        return request.render('elrabeh_site.project_form_template', values)

    @http.route('/my-projects', type='http', auth='user', website=True)
    def my_projects(self):
        product = request.env['product.product'].sudo().search([('in_platform', '=', True)], limit=1)

        orders = request.env['sale.order'].sudo().search([
            ('partner_id', '=', request.env.user.partner_id.id),
            ('order_line.product_id', '=', product.id)
        ])

        return request.render('elrabeh_site.my_projects_template', {
            'orders': orders
        })

    @http.route('/project-status/<int:order_id>', type='http', auth='user', website=True)
    def project_status(self, order_id):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order or order.partner_id.id != request.env.user.partner_id.id:
            return request.not_found()

        pending_parties = []
        if order.party1_approved == 'pending':
            pending_parties.append(order.party_one_name or 'Party 1')
        if order.party2_approved == 'pending':
            pending_parties.append(order.party_two_name or 'Party 2')
        if order.party3_approved == 'pending':
            pending_parties.append(order.party_three_name or 'Party 3')

        return request.render('elrabeh_site.project_status_template', {
            'order': order,
            'pending_parties': pending_parties
        })

    @http.route('/project/step2', type='http', auth='user', website=True, csrf=False)
    def project_step2(self, **post):
        # جلب أو إنشاء سجل مؤقت للمستخدم
        temp = request.env['project.temp.data'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        vals = {
            'user_id': request.env.user.id,
            'name': post.get('name'),
            'contract_value': post.get('contract_value'),
            'address': post.get('address'),
            'role': post.get('role'),
            # image و attachment يفضل التعامل معهم كملفات في فورم خاص لو محتاج
            # لذا هنا افترض أنك ترسلهم كبيانات باينري مباشرة أو تعاملهم لاحقًا
            'image': post.get('image'),
            'attachment': post.get('attachment'),
            'installments_count' : post.get('installments_count')
        }
        if temp:
            temp.sudo().write(vals)
        else:
            temp = request.env['project.temp.data'].sudo().create(vals)

        user = request.env.user
        return request.render('elrabeh_site.project_role', {
            'name': user.name,
            'email': user.email,
            'phone': user.partner_id.phone or '',
            'user_role': post.get('role'),
        })

    @http.route('/project/submit/roles', type='http', auth='user', website=True, csrf=False)
    def submit_roles(self, **post):
        temp = request.env['project.temp.data'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        if not temp:
            return request.redirect('/mangeyproject')

        # تحديث بيانات الأطراف الثانية والثالثة
        temp.sudo().write({
            'party_two_name': post.get('second_party_name'),
            'party_two_role': post.get('second_party_role'),
            'party_two_phone': post.get('second_party_phone'),
            'party_two_email': post.get('second_party_email'),
            'party_three_name': post.get('third_party_name'),
            'party_three_role': post.get('third_party_role'),
            'party_three_phone': post.get('third_party_phone'),
            'party_three_email': post.get('third_party_email'),
        })

        # إنشاء sale.order
        product = request.env['product.product'].sudo().search([('in_platform', '=', True)], limit=1)
        sale_order_vals = {
            'partner_id': request.env.user.partner_id.id,
            'order_line': [(0, 0, {
                'product_id': product.id if product else False,
                'product_uom_qty': 1,
                'price_unit': 0,
            })],

            # بيانات المشروع
            'project_name': temp.name,
            'installments_count' : temp.installments_count,
            'contract_value': temp.contract_value,
            'project_address': temp.address,
            'party_one_role': temp.role,
            'project_image': temp.image,
            'project_attachment': temp.attachment,

            # بيانات الطرف الأول
            'party_one_name': request.env.user.name,
            'party_one_email': request.env.user.email,
            'party_one_phone': request.env.user.partner_id.phone or '',
            'party_one_role': temp.role,

            # بيانات الطرف الثاني
            'party_two_name': temp.party_two_name,
            'party_two_role': temp.party_two_role,
            'party_two_phone': temp.party_two_phone,
            'party_two_email': temp.party_two_email,

            # بيانات الطرف الثالث
            'party_three_name': temp.party_three_name,
            'party_three_role': temp.party_three_role,
            'party_three_phone': temp.party_three_phone,
            'party_three_email': temp.party_three_email,
        }
        sale_order = request.env['sale.order'].sudo().create(sale_order_vals)

        # إنشاء رموز الموافقة
        token2 = str(uuid.uuid4())
        token3 = str(uuid.uuid4())
        sale_order.sudo().write({
            'approval_token_party2': token2,
            'approval_token_party3': token3,
        })

        # روابط الموافقة
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        link_party2 = f"{base_url}/project/approve/{token2}"
        link_party3 = f"{base_url}/project/approve/{token3}"

        # صياغة HTML للإيميل
        body_party2 = f"""
        <p>Hello <b>{post.get('second_party_name')}</b>,</p>
        <p>You have been added to the project <b>{sale_order.project_name or sale_order.name}</b> 
        as <b>{post.get('second_party_role')}</b>.</p>
        <p>Please review the project details and approve your participation using the link below:</p>
        <p><a href="{link_party2}" style="background:#28a745;color:#fff;padding:10px 15px;border-radius:5px;text-decoration:none;">
        Approve Project</a></p>
        """

        body_party3 = f"""
        <p>Hello <b>{post.get('third_party_name')}</b>,</p>
        <p>You have been added to the project <b>{sale_order.project_name or sale_order.name}</b> 
        as <b>{post.get('third_party_role')}</b>.</p>
        <p>Please review the project details and approve your participation using the link below:</p>
        <p><a href="{link_party3}" style="background:#28a745;color:#fff;padding:10px 15px;border-radius:5px;text-decoration:none;">
        Approve Project</a></p>
        """
        # إرسال للطرف الثاني
        if post.get('second_party_email'):
            mail_values2 = {
                'subject': "📌 تمت إضافتك في مشروع جديد",
                'body_html': body_party2,
                'email_from': 'odooboot2025@gmail.com',
                'email_to': post.get('second_party_email'),
                'res_id': sale_order.id,
                'model': 'sale.order',
            }
            mail2 = request.env['mail.mail'].sudo().create(mail_values2)
            mail2.sudo().send()

        # إرسال للطرف الثالث
        if post.get('third_party_email'):
            mail_values3 = {
                'subject': "📌 تمت إضافتك في مشروع جديد",
                'body_html': body_party3,
                'email_from': 'odooboot2025@gmail.com',
                'email_to': post.get('third_party_email'),
                'res_id': sale_order.id,
                'model': 'sale.order',
            }
            mail3 = request.env['mail.mail'].sudo().create(mail_values3)
            mail3.sudo().send()

        # # إرسال إيميل للطرف الثاني
        # if post.get('second_party_email'):
        #     template_two = request.env.ref('elrabeh_site.email_template_project_party_two')
        #     template_two.sudo().with_context(
        #         approval_link=link_party2,
        #         party_two_name=temp.party_two_name,
        #         party_two_role=temp.party_two_role,
        #         project_name=temp.name
        #     ).send_mail(
        #         sale_order.id,
        #         force_send=True,
        #         email_values={
        #             'email_to': post.get('second_party_email'),
        #             'email_from': 'odooboot2025@gmail.com'
        #         }
        #     )

        # إرسال إيميل للطرف الثالث
        # if post.get('third_party_email'):
        #     template_three = request.env.ref('elrabeh_site.email_template_project_party_three')
        #     template_three.sudo().with_context(
        #         approval_link=link_party3,
        #         party_three_name=temp.party_three_name,
        #         party_three_role=temp.party_three_role,
        #         project_name=temp.name
        #     ).send_mail(
        #         sale_order.id,
        #         force_send=True,
        #         email_values={
        #             'email_to': post.get('third_party_email'),
        #             'email_from': 'odooboot2025@gmail.com'
        #         }
        #     )

        # حذف البيانات المؤقتة
        temp.sudo().unlink()

        return request.render('elrabeh_site.project_submit_success', {
            'order': sale_order
        })

    @http.route('/project/create', type='http', auth='user', website=True)
    def create_project(self):
        # بس عرض فورم إنشاء مشروع بدون فحص
        temp = request.env['project.temp.data'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        values = {}
        if temp:
            values = {
                'name': temp.name,
                'contract_value': temp.contract_value,
                'address': temp.address,
                'role': temp.role,
                'image': temp.image,
                'attachment': temp.attachment,
            }
        return request.render('elrabeh_site.project_form_template', values)


    # الدفعات
    # --------- إنشاء دفعة (مالك/استشاري) ---------
    @http.route(['/installment/create/<int:order_id>'], type='http', auth="user", website=True)
    def installment_form(self, order_id, **post):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()

        current_user_email = request.env.user.email
        allowed_emails = ["admin@yourcompany.example.com"]
        for party_num in [1, 2, 3]:
            email_field = getattr(order, f'party_{party_num}_email', False)
            role_field = getattr(order, f'party_{party_num}_role', False)
            if email_field and role_field in ['owner', 'consultant']:
                allowed_emails.append(email_field)

        if current_user_email not in allowed_emails:
            return request.render('elrabeh_site.unauthorized_page')

        return request.render("elrabeh_site.installment_form_page", {'project': order})

    # --------- حفظ الدفعة ---------
    @http.route(['/installment/save'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def installment_save(self, **post):
        order = request.env['sale.order'].sudo().browse(int(post.get('project_id')))
        if not order.exists():
            return request.render('elrabeh_site.installment_form_page', {
                'project': order,
                'error_message': "لم يتم العثور على أمر البيع."
            })

        current_user_email = request.env.user.email
        project = order.analytic_account_id.project_ids[:1]
        if not project:
            return request.render('elrabeh_site.installment_form_page', {
                'project': order,
                'error_message': "لم يتم العثور على مشروع مرتبط بهذا الطلب."
            })

        allowed_emails = ["admin@yourcompany.example.com"]
        if project.owner_email:
            allowed_emails.append(project.owner_email)
        if project.consultant_email:
            allowed_emails.append(project.consultant_email)

        if current_user_email not in allowed_emails:
            return request.render('elrabeh_site.unauthorized_page')

        # تحويل المبلغ ل float
        try:
            amount = float(post.get('amount', 0))
        except:
            return request.render('elrabeh_site.installment_form_page', {
                'project': order,
                'error_message': "المبلغ غير صالح."
            })

        # --- التحقق من عدد الدفعات ---
        total_installments_allowed = order.installments_count or 0
        existing_installments_count = request.env['project.installment'].sudo().search_count(
            [('project_id', '=', project.id)]
        )

        if total_installments_allowed and existing_installments_count >= total_installments_allowed:
            msg = f"عدد الدفعات المسموح به هو {total_installments_allowed} فقط. لا يمكنك إنشاء دفعات أكثر."
            return request.render('elrabeh_site.installment_form_page', {
                'project': order,
                'error_message': msg,
                'remaining_installments': total_installments_allowed - existing_installments_count
            })

        # --- التحقق من إجمالي المبلغ ---
        total_paid = sum(
            request.env['project.installment'].sudo().search([('project_id', '=', project.id)]).mapped('amount')
        )
        contract_value = order.contract_value or 0.0
        if contract_value and (total_paid + amount > contract_value):
            msg = f"القيمة الإجمالية للدفعات ({total_paid + amount}) تجاوزت القيمة التعاقدية للمشروع ({contract_value})."
            return request.render('elrabeh_site.installment_form_page', {
                'project': order,
                'error_message': msg,
                'total_paid': total_paid,
                'contract_value': contract_value
            })

        # إنشاء الدفعة الجديدة
        owner_user = request.env['res.users'].sudo().search([('email', '=', project.owner_email)], limit=1)
        vals = {
            'project_id': project.id,
            'name': post.get('name'),
            'amount': amount,
            'owner_id': owner_user.id if owner_user else request.env.user.id,
        }
        request.env['project.installment'].sudo().create(vals)

        return request.redirect(f'/owner/installments/{order.id}')

    # --------- عرض دفعات المقاول ---------
    @http.route(['/contractor/installments/<int:order_id>'], type='http', auth="user", website=True)
    def contractor_installments(self, order_id):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()

        project = order.analytic_account_id.project_ids[:1]
        if not project or not project.contractor_email:
            return request.not_found()

        if request.env.user.email != project.contractor_email:
            return request.render('elrabeh_site.unauthorized_page')

        installments = request.env['project.installment'].sudo().search([('project_id', '=', project.id)])
        return request.render("elrabeh_site.contractor_installments_template", {
            'project': order,
            'installments': installments
        })

    # --------- عرض دفعات الاستشاري ---------
    @http.route(['/consultant/installments/<int:project_id>'], type='http', auth="user", website=True)
    def consultant_installments(self, project_id):
        project = request.env['project.project'].sudo().browse(project_id)
        if not project.exists():
            return request.not_found()

        allowed_email = project.consultant_email
        if not allowed_email or request.env.user.email != allowed_email:
            return request.render('elrabeh_site.unauthorized_page')

        installments = request.env['project.installment'].sudo().search([('project_id', '=', project.id)])
        return request.render("elrabeh_site.consultant_installments_template", {
            'project': project,
            'installments': installments
        })

    # --------- عرض دفعات المالك ---------
    @http.route(['/owner/installments/<int:order_id>'], type='http', auth="user", website=True)
    def owner_installments(self, order_id):
        order = request.env['sale.order'].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()

        allowed_emails = []
        for party in ['party_one', 'party_two', 'party_three']:
            role = getattr(order, f'{party}_role')
            email = getattr(order, f'{party}_email')
            if role in ['owner', 'consultant', 'contractor'] and email:
                allowed_emails.append(email)

        if request.env.user.email not in allowed_emails:
            return request.render('elrabeh_site.unauthorized_page')

        project = order.analytic_account_id.project_ids[:1]
        if not project:
            return request.not_found()

        installments = request.env['project.installment'].sudo().search([('project_id', '=', project.id)])
        return request.render("elrabeh_site.owner_installments_template", {
            'project': order,
            'installments': installments
        })

    # --------- المقاول يطلب دفعة ---------
    @http.route(['/contractor/request_payment/<int:inst_id>'], type='http', auth="user", website=True)
    def contractor_request_payment(self, inst_id):
        inst = request.env['project.installment'].sudo().browse(inst_id)
        if not inst.project_id.contractor_email or request.env.user.email != inst.project_id.contractor_email:
            return request.render('elrabeh_site.unauthorized_page')

        try:
            inst.action_request_payment()
            message = "تم طلب الدفعة بنجاح! إشعار تم إرساله للمالك والاستشاري."
        except UserError as e:
            message = str(e)

        return request.render('elrabeh_site.simple_message', {
            'title': 'طلب الدفعة',
            'message': message
        })

    # --------- الاستشاري يوافق ---------
    @http.route(['/consultant/approve/<int:inst_id>'], type='http', auth="user", website=True)
    def consultant_approve(self, inst_id):
        inst = request.env['project.installment'].sudo().browse(inst_id)
        if not inst.project_id.consultant_email or request.env.user.email != inst.project_id.consultant_email:
            return request.render('elrabeh_site.unauthorized_page')

        try:
            inst.action_consultant_approve()
        except UserError as e:
            return request.render('elrabeh_site.simple_message', {'title': 'خطأ', 'message': str(e)})

        project_id = inst.project_id
        return request.redirect(f"/consultant/installments/{project_id.id}")

    # --------- الاستشاري/المالك يرفض ---------
    @http.route(['/consultant/reject/<int:inst_id>'], type='http', auth="user", website=True)
    def consultant_reject(self, inst_id):
        inst = request.env['project.installment'].sudo().browse(inst_id)
        emails_allowed = []
        if inst.project_id.consultant_email:
            emails_allowed.append(inst.project_id.consultant_email)
        if inst.project_id.owner_email:
            emails_allowed.append(inst.project_id.owner_email)

        if request.env.user.email not in emails_allowed:
            return request.render('elrabeh_site.unauthorized_page')

        inst.action_owner_reject()
        project_id = inst.project_id
        return request.redirect(f"/consultant/installments/{project_id.id}")

    # --------- المالك يدفع ---------
    @http.route(['/owner/pay/<int:inst_id>'], type='http', auth="user", website=True)
    def owner_pay_form(self, inst_id, **kw):
        inst = request.env['project.installment'].sudo().browse(inst_id)

        # تأكد أن الدفعة موجودة
        if not inst.exists():
            return request.not_found()

        project = inst.project_id
        # تحقق أن المشروع موجود
        if not project:
            return request.not_found()

        # تحقق أن المستخدم هو المالك
        # if not project.owner_email or request.env.user.email != project.owner_email:
        #     return request.render('elrabeh_site.unauthorized_page')

        if inst.state not in ('consultant_approved', 'owner_approved'):
            return request.render('elrabeh_site.simple_message',
                                  {'title': 'تنبيه', 'message': 'لا يمكن الدفع قبل موافقة الاستشاري.'})
        return request.render('elrabeh_site.owner_pay_form_template', {'inst': inst})

    @http.route(['/owner/pay/submit'], type='http', auth="user", website=True, methods=['POST'], csrf=True)
    def owner_pay_submit(self, **post):
        inst = request.env['project.installment'].sudo().browse(int(post.get('inst_id')))
        if not inst.project_id.owner_email or request.env.user.email != inst.project_id.owner_email:
            return request.render('elrabeh_site.unauthorized_page')

        upload = post.get('payment_proof')
        if not upload or not getattr(upload, 'filename', False):
            return request.render('elrabeh_site.simple_message',
                                  {'title': 'تنبيه', 'message': 'من فضلك أرفع إثبات الدفع.'})

        attachment = request.env['ir.attachment'].sudo().create({
            'name': upload.filename,
            'datas': base64.b64encode(upload.read()),
            'res_model': 'project.installment',
            'res_id': inst.id,
            'mimetype': upload.mimetype or 'application/octet-stream',
        })

        try:
            inst.action_owner_pay(attachment)
        except UserError as e:
            return request.render('elrabeh_site.simple_message', {'title': 'خطأ', 'message': str(e)})

        return request.render('elrabeh_site.simple_message',
                              {'title': 'تم الدفع', 'message': 'تم تسجيل الدفع وإرسال إشعار للمقاول لتأكيد الاستلام.'})

    # --------- المقاول يؤكد الاستلام بالتوكن ---------
    @http.route(['/contractor/confirm/<int:inst_id>/<string:token>'], type='http', auth="user", website=True)
    def contractor_confirm_received(self, inst_id, token, **kw):
        inst = request.env['project.installment'].sudo().browse(inst_id)
        try:
            inst.action_contractor_confirm(token)
        except UserError as e:
            return request.render('elrabeh_site.simple_message', {'title': 'خطأ', 'message': str(e)})

        return request.render('elrabeh_site.simple_message',
                              {'title': 'تم التأكيد', 'message': 'تم تأكيد استلام الدفعة. شكراً لك.'})

    #الدفعات المستحقة من المقاول
    @http.route(['/contractor/my_projects'], type='http', auth="user", website=True)
    def contractor_projects(self):
        # جلب كل المشاريع اللي المقاول مربوط بيها
        projects = request.env['project.project'].sudo().search([
            ('contractor_email', '=', request.env.user.email)
        ])
        return request.render("elrabeh_site.contractor_my_projects_template", {
            'projects': projects
        })

############  end mange my project #########################


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