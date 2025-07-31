{
    'name': 'Elrabih Site',
    'summary': 'Elrabih Site Custom Theme Site',
    'icon': '/elrabeh_site/static/src/images/logo.png',
    'author': 'ahmed mohmed',
    'sequence': '200',
    'category': 'Extra Tools',
    'description': "",
    'depends': ['website' ,'website_sale' ,'auth_signup'],
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
