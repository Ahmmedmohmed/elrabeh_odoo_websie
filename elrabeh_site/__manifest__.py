{
    'name': 'Elrabih Site',
    'summary': 'Elrabih Site Custom Theme Site',
    'icon': '/elrabeh_site/static/src/images/logo.png',
    'author': 'ahmed mohmed',
    'sequence': '200',
    'category': 'Extra Tools',
    'description': "",
    'depends': ['website' ,'website_sale' ,'auth_signup' ,'project','mail'],
    'data': [
        'website/menu-template.xml',
        'website/foter.xml',
        'website/homePage.xml',
        'website/account-management.xml',
        'website/service_details.xml',
        'website/askedQuestions.xml',
        'website/userComments.xml',
        'website/freeBook.xml',
        'website/contactUs.xml',
        'website/aboutus.xml',
        'website/ourServices.xml',
        'website/service_order.xml',
        'website/affiliate-area.xml',
         'website/signin.xml',
         'website/overridersingup.xml',

        'views/affiliate_request_views.xml',
        'website/affiliate_templates.xml',
      'website/affiliate_link_page.xml',
      'security/ir.model.access.csv',
 'website/bulidproject.xml',
'website/mangemyproject.xml',
'website/build_project_template.xml',
'website/build_project_detail_page.xml',
'website/overideprodecut.xml',
'website/select_project_template.xml',
'views/in_platforme.xml',
'website/manage_my_project_role.xml',
 'views/sala_orderinherit.xml',
        'views/installment_due_cron.xml',


        'website/approved2part.xml',
    'website/project_submit_success.xml',
    'website/project_submit_success.xml',
        'website/thanks_approve.xml',

        'website/contractor_installments_template.xml',
'website/approve_rquest_change.xml',


        'website/project_installments_template.xml',
        'website/installment_common_templates.xml',
        'website/installment_form_templates.xml',
        'website/installment_contractor_templates.xml',
        'website/installment_consultant_templates.xml',
        'website/installment_owner_templates.xml',

        'data/emil_templet.xml',



        'website/my_project.xml',
        'website/project_status.xml',
        'website/simple_massge_when_requestpyment.xml',
        'website/contractor_my_projects_template.xml',




    ],
    'assets': {
        'web.assets_frontend': [
            '/elrabeh_site/static/src/scss/style.scss',

'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
        ],
    },
    'version': '0.0.1',
    'application': True,
    'installable': True,
}
