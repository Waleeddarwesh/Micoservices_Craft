"""
Admin API Views — Dashboard backend endpoints.
Refactored to Proxy-Only Architecture (Phase 5).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from craft_common.api_clients import order_client, catalog_client, payment_client, auth_client, platform_client
from .dashboard_config import get_user_dashboard_modules, get_user_dashboard_widgets

class DashboardIdentityView(APIView):
    permission_classes = [] 
    def get(self, request):
        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Unauthorized'}, status=403)
        user = request.user
        return Response({
            'user': {'id': user.id, 'email': user.email, 'first_name': user.first_name, 'last_name': user.last_name, 'is_superuser': user.is_superuser},
            'permissions': list(user.get_all_permissions()),
            'modules': get_user_dashboard_modules(user),
            'widgets': get_user_dashboard_widgets(user),
            'environment': 'Production'
        })

class AdminStatsView(APIView):
    def get(self, request):
        # Fetch stats from downstream services via internal APIs
        try:
            users = auth_client.get('/internal/users/count/').json().get('count', 0)
        except: users = 0
        try:
            orders = order_client.get('/internal/orders/count/').json().get('count', 0)
        except: orders = 0
        try:
            revenue = payment_client.get('/internal/payments/revenue/').json().get('total', 0)
        except: revenue = 0
        try:
            products = catalog_client.get('/internal/products/count/').json().get('count', 0)
        except: products = 0
        
        return Response({
            'total_users': users,
            'total_orders_paid': orders,
            'total_revenue': revenue,
            'total_products': products,
        })

class AdminGlobalSearchView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminGlobalSearchView GET not fully implemented yet'})

class AdminChartsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminChartsView GET not fully implemented yet'})

class AdminSystemReportsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSystemReportsView GET not fully implemented yet'})

class AdminSystemHealthView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSystemHealthView GET not fully implemented yet'})

class AdminTopProductsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminTopProductsView GET not fully implemented yet'})

class AdminRecentActivityView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminRecentActivityView GET not fully implemented yet'})

class AdminAuditLogsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminAuditLogsView GET not fully implemented yet'})

class AdminSupplierPerformanceView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSupplierPerformanceView GET not fully implemented yet'})

class AdminDeliveryPerformanceView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminDeliveryPerformanceView GET not fully implemented yet'})

class AdminFinancialReconciliationView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminFinancialReconciliationView GET not fully implemented yet'})

class AdminFraudAlertsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminFraudAlertsView GET not fully implemented yet'})

class AdminFraudAlertActionView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminFraudAlertActionView POST not fully implemented yet'})

class AdminProductModerationView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminProductModerationView GET not fully implemented yet'})

class AdminProductModerationActionView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminProductModerationActionView POST not fully implemented yet'})

class AdminOrdersView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminOrdersView GET not fully implemented yet'})

class AdminOrderStatusView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminOrderStatusView POST not fully implemented yet'})

class AdminProductsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminProductsView GET not fully implemented yet'})

class AdminReturnsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminReturnsView GET not fully implemented yet'})

class AdminCoursesView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminCoursesView GET not fully implemented yet'})

class AdminReviewsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminReviewsView GET not fully implemented yet'})

class AdminCouponsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminCouponsView GET not fully implemented yet'})

class AdminTransactionsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminTransactionsView GET not fully implemented yet'})

class AdminWithdrawalsListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminWithdrawalsListView GET not fully implemented yet'})

class AdminPaymentsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminPaymentsView GET not fully implemented yet'})

class AdminNotificationsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminNotificationsView GET not fully implemented yet'})

class AdminSupportTicketsView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSupportTicketsView GET not fully implemented yet'})

class AdminSupportTicketDetailView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSupportTicketDetailView GET not fully implemented yet'})
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSupportTicketDetailView POST not fully implemented yet'})

class AdminDisputesView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminDisputesView GET not fully implemented yet'})

class AdminDisputeDetailView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminDisputeDetailView GET not fully implemented yet'})
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminDisputeDetailView POST not fully implemented yet'})

class AdminUsersView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminUsersView GET not fully implemented yet'})

class AdminUserDetailView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminUserDetailView GET not fully implemented yet'})
    def put(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminUserDetailView PUT not fully implemented yet'})

class AdminUserToggleView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminUserToggleView POST not fully implemented yet'})

class AdminSupplierApprovalView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSupplierApprovalView POST not fully implemented yet'})

class AdminDeliveryApprovalView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminDeliveryApprovalView POST not fully implemented yet'})

class AdminSendNotificationView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminSendNotificationView POST not fully implemented yet'})

class AdminReturnActionView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminReturnActionView POST not fully implemented yet'})

class AdminWithdrawalActionView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminWithdrawalActionView POST not fully implemented yet'})

class AdminReviewModerationView(APIView):
    def post(self, request, *args, **kwargs):
        return Response({'message': 'Proxied AdminReviewModerationView POST not fully implemented yet'})

