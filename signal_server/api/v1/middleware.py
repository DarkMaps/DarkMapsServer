def x_robots_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = get_response(request)

        response['X-Robots-Tag'] = 'none'

        return response

    return middleware