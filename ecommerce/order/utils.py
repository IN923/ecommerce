from .models import VendorOrders,Order


def update_customer_order(order):
    all_vendor_orders = VendorOrders.objects.filter(order=order).values_list("status",flat=True)


    if all(s=="confirmed" for s in all_vendor_orders):
        order.status="confirmed"
    elif all(s=="shipped" for s in all_vendor_orders):
        order.status="shipped"
    elif all(s=="delivered" for s in all_vendor_orders):
        order.status="delivered"
    elif any(s in ["pending","confirmed","shipped"] for s in all_vendor_orders):
        order.status="pending"
    elif any(s in ["confirmed","shipped"] for s in all_vendor_orders):
        order.status="confirmed"
    elif any(s in ["shipped","delivered"] for s in all_vendor_orders):
        order.status="shipped"
    elif any(s=="cancelled" for s in all_vendor_orders):
        order.status="cancelled"
    else:
        order.status="pending"

    order.save()




