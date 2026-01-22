from django.urls import path
from .views import UserView,AdminLogin,UserMeView,LoginView,DashboardView,VerifyOTPView,ResendOTPView,AddressView,CustomerAPIView,CustomerOrderAPIView,OrderItemView,OrderView,StaffView,StaffOrderView,OrderActionView,ServiceFullDetailsView,CustomerAPIView,ServiceView,CategoryView,ProductView,PickupDeliveryView,FeedbackView,MonthlyOrdersReportView
from .views import (
    AdminForgotPassword,
    AdminVerifyOTP,
    AdminResetPassword,
    AdminResendOTP,WebsiteOrderView,OrderDashboardCounts,OrderReceiptDownloadView
)
urlpatterns = [


    path('users/', UserView.as_view()),             
    path('users/<int:user_id>', UserView.as_view()),
    path('users/me', UserMeView.as_view()),
    path("address", AddressView.as_view()),                  
    path("address/<int:address_id>", AddressView.as_view()), 
    path("user/<int:user_id>/address", AddressView.as_view()) ,
    path('admin/forgot-password', AdminForgotPassword.as_view(), name='admin-forgot-password'),
    path('admin/verify-otp', AdminVerifyOTP.as_view(), name='admin-verify-otp'),
    path('admin/reset-password', AdminResetPassword.as_view(), name='admin-reset-password'),
    path('admin/resend-otp',AdminResendOTP.as_view(),name='admin_resent_otp'),

    path('login', LoginView.as_view(), name='login'),
    path('admin/login/',  AdminLogin.as_view()),
    path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp', ResendOTPView.as_view(), name='resend-otp'),
    # -------------------------
    # CUSTOMER ROUTES
    # -------------------------

    # POST - Register Customer
    path("customers/register/", CustomerAPIView.as_view()),

    # GET - List customers
    path("customers/", CustomerAPIView.as_view()),

    # GET/PUT/DELETE - Single customer
    path("customers/<int:customer_id>/", CustomerAPIView.as_view()),
    path("customers/<int:customer_id>/orders/", CustomerOrderAPIView.as_view()),

    path("staff/", StaffView.as_view()),               
    path("staff/<int:user_id>/", StaffView.as_view()),
    # -------------------------
    # ADDRESS ROUTES
    # -------------------------

    # POST - Create address
    path("customers/<int:customer_id>/addresses/", CustomerAPIView.as_view()),

    # GET - List all addresses
    path("customers/<int:customer_id>/addresses/", CustomerAPIView.as_view()),

    # GET / PUT / DELETE - Single address
    path("customers/<int:customer_id>/addresses/<int:address_id>/", CustomerAPIView.as_view()),

    # GET - Default address
    path("customers/<int:customer_id>/addresses/default", CustomerAPIView.as_view()),

    path("website/order/", WebsiteOrderView.as_view()),






    path('staff/<int:user_id>/orders/', StaffOrderView.as_view(), name='staff-orders'),
    path('staff/orders', StaffOrderView.as_view(), name='create_get_orders'),  # POST: create, GET: list
    # path('staff/orders/user/5/orders', StaffOrderView.as_view(), name='create_get_orders'), 
    path('staff/orders/<int:order_id>', StaffOrderView.as_view(), name='get_update_delete_order'), 

    # Quick actions
    path('staff/orders/<int:order_id>/confirm', OrderActionView.as_view(), {'action': 'confirm'}, name='confirm_order'),
    path('staff/orders/<int:order_id>/pick', OrderActionView.as_view(), {'action': 'pick'}, name='pick_order'),
    path('staff/orders/<int:order_id>/complete', OrderActionView.as_view(), {'action': 'deliver'}, name='complete_order'),

    # Dashboard stats 
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path('staff/orders/dashboard/stats', DashboardView.as_view(), name='dashboard_stats'),
    # --------------------------
    # service URLs
    # --------------------------

    path(
        "services/getAllServicesWithDetails/",
        ServiceFullDetailsView.as_view(),
        name="service-details-all"
    ),
    path('services/', ServiceView.as_view(), name='service-list'),              
    path('services/<int:service_id>', ServiceView.as_view(), name='service-detail'), 

    # --------------------------
    # Category URLs
    # --------------------------
    path('categories', CategoryView.as_view(), name='category-list'),        
    path('categories/<int:category_id>', CategoryView.as_view(), name='category-detail'), 

    # --------------------------
    # Product URLs
    # --------------------------
    path('products/', ProductView.as_view(), name='product-list'),                
    path('products/<int:product_id>', ProductView.as_view(), name='product-detail'), 

    # --------------------------
    # Categories under Service
    # --------------------------    
    path('services/<int:service_id>/categories/', CategoryView.as_view(), name='service-category-list'),
    path('services/<int:service_id>/categories/<int:category_id>', CategoryView.as_view(), name='service-category-detail'), 

    # --------------------------
    #  Products under Category
    # --------------------------
    path('categories/<int:category_id>/products', ProductView.as_view(), name='category-product-list'), 
    path('categories/<int:category_id>/products/<int:product_id>', ProductView.as_view(), name='category-product-detail'),
    # --------------------------
    #  Products under Service + Category
    # --------------------------
    path('services/<int:service_id>/categories/<int:category_id>/products', ProductView.as_view(), name='service-category-product-list'), 
    path('services/<int:service_id>/categories/<int:category_id>/products/<int:product_id>', ProductView.as_view(), name='service-category-product-detail'),


    # --------------------------
    #  order-items
    # --------------------------
    path('order-items', OrderItemView.as_view(), name='order-items-list'),
    path('order-items/<int:item_id>', OrderItemView.as_view(), name='order-item'),

    # --------------------------
    #  order
    # --------------------------
    path('orders/', OrderView.as_view(), name='orders-list-create'),  
    path('orders/<int:order_id>', OrderView.as_view(), name='order-detail'),  

    # User-specific orders
    path('orders/user/<int:user_id>/', OrderView.as_view(), name='orders-by-user'),


# ----------------------------------------
# pickups-deliveries
# -----------------------------------

    path('pickups-deliveries', PickupDeliveryView.as_view(), name='pickup-delivery-list-create'),  
    path('pickups-deliveries/<int:pd_id>', PickupDeliveryView.as_view(), name='pickup-delivery-detail'),  

    # Get pickups by order
    path('pickups-deliveries/order/<int:order_id>', PickupDeliveryView.as_view(), name='pickup-delivery-by-order'),  

    # Actions
    path('pickups-deliveries/<int:pd_id>/mark-picked', PickupDeliveryView.as_view(), {'action': 'mark-picked-up'}, name='pickup-mark-picked'),  
    path('pickups-deliveries/<int:pd_id>/mark-delivered', PickupDeliveryView.as_view(), {'action': 'mark-delivered'}, name='pickup-mark-delivered'),  



    path('feedbacks', FeedbackView.as_view(), name='feedback-list-create'),              
    path('feedbacks/<int:feedback_id>', FeedbackView.as_view(), name='feedback-detail'), 

    # Feedback by order
    path('orders/<int:order_id>/feedback', FeedbackView.as_view(), name='feedback-by-order'),

    # Feedbacks by user
    path('users/<int:user_id>/feedbacks', FeedbackView.as_view(), name='feedbacks-by-user'),

    path('reports/monthly-orders/', MonthlyOrdersReportView.as_view(), name='monthly-orders-report'),
    path(
        'orders/dashboard-counts/',
        OrderDashboardCounts.as_view(),
        name='order-dashboard-counts'
    ),
    
    path(
        'staff/<int:user_id>/address/',
        StaffView.as_view(),
        name='staff-address-add'
    ),
    path(
        'staff/<int:user_id>/address/<int:address_id>/',
        StaffView.as_view(),
        name='staff-address-detail'
    ),
    
    path('orders/<int:order_id>/receipt/', OrderReceiptDownloadView.as_view()),
]

