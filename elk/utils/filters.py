def request_filters(request, allowed):
    """
    Get list of allowed parameters from request.GET.
    """
    result = {}
    for i in allowed:
        if request.GET.get(i):
            result[i] = request.GET.get(i)
    return result
