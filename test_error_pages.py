#!/usr/bin/env python3
"""
Test script to verify error page styling and handling
"""

from aiohttp import web
import asyncio

def get_error_page(error_title, error_message):
    """Generate styled error page matching the home page design"""
    html_content = f'''<html>
<head>
    <title>{error_title} - LinkerX CDN</title>
    <style>
        body{{ margin:0; padding:0; width:100%; height:100%; color:#b0bec5; display:table; font-weight:100; font-family:Lato }}
        .container{{ text-align:center; display:table-cell; vertical-align:middle }}
        .content{{ text-align:center; display:inline-block }}
        .message{{ font-size:80px; margin-bottom:40px }}
        .submessage{{ font-size:40px; margin-bottom:40px; color:#e74c3c }}
        .error-detail{{ font-size:20px; margin-bottom:30px; color:#95a5a6 }}
        .copyright{{ font-size:20px; }}
        a{{ text-decoration:none; color:#3498db }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <div class="message">LinkerX CDN</div>
            <div class="submessage">{error_message}</div>
            <div class="error-detail">{error_title}</div>
            <div class="copyright">Hash Hackers and LiquidX Projects</div>
        </div>
    </div>
</body>
</html>'''
    return html_content

HOME_PAGE = '''<html>
<head>
    <title>LinkerX CDN</title>
    <style>
        body{ margin:0; padding:0; width:100%; height:100%; color:#b0bec5; display:table; font-weight:100; font-family:Lato }
        .container{ text-align:center; display:table-cell; vertical-align:middle }
        .content{ text-align:center; display:inline-block }
        .message{ font-size:80px; margin-bottom:40px }
        .submessage{ font-size:40px; margin-bottom:40px }
        .copyright{ font-size:20px; }
        a{ text-decoration:none; color:#3498db }
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <div class="message">LinkerX CDN</div>
            <div class="submessage">All Systems Operational</div>
            <div class="copyright">Hash Hackers and LiquidX Projects</div>
        </div>
    </div>
</body>
</html>'''

@web.middleware
async def error_middleware(request, handler):
    """Custom 404 handler middleware"""
    try:
        response = await handler(request)
        if response.status == 404:
            error_page = get_error_page("Page Not Found", "Link Expired")
            return web.Response(text=error_page, content_type="text/html", status=404)
        return response
    except web.HTTPException as ex:
        if ex.status == 404:
            error_page = get_error_page("Page Not Found", "Link Expired")
            return web.Response(text=error_page, content_type="text/html", status=404)
        raise

async def home(request):
    """Home page handler"""
    return web.Response(text=HOME_PAGE, content_type="text/html")

async def test_file_ref_expired(request):
    """Simulate FILE_REFERENCE_EXPIRED error"""
    error_page = get_error_page("File Reference Expired", "Link Expired")
    return web.Response(text=error_page, content_type="text/html", status=410)

async def test_rate_limit(request):
    """Simulate FLOOD_WAIT error"""
    error_page = get_error_page("Rate Limit Exceeded", "Too Many Requests")
    return web.Response(text=error_page, content_type="text/html", status=429)

async def test_invalid_file(request):
    """Simulate FILE_ID_INVALID error"""
    error_page = get_error_page("Invalid File ID", "Link Expired")
    return web.Response(text=error_page, content_type="text/html", status=410)

async def test_access_denied(request):
    """Simulate CHANNEL_PRIVATE error"""
    error_page = get_error_page("Access Denied", "File Not Available")
    return web.Response(text=error_page, content_type="text/html", status=403)

async def test_generic_error(request):
    """Simulate generic error"""
    error_page = get_error_page("Service Error", "Failed to Stream File")
    return web.Response(text=error_page, content_type="text/html", status=500)

def create_app():
    """Create and configure the web application"""
    app = web.Application(middlewares=[error_middleware])
    app.router.add_get('/', home)
    app.router.add_get('/test/file-ref-expired', test_file_ref_expired)
    app.router.add_get('/test/rate-limit', test_rate_limit)
    app.router.add_get('/test/invalid-file', test_invalid_file)
    app.router.add_get('/test/access-denied', test_access_denied)
    app.router.add_get('/test/generic-error', test_generic_error)
    return app

if __name__ == '__main__':
    print("=" * 80)
    print("Testing Error Page Implementation")
    print("=" * 80)
    print()
    print("Starting test server on http://0.0.0.0:8081")
    print()
    print("Test URLs:")
    print("  - Home page:                 http://0.0.0.0:8081/")
    print("  - 404 Error:                 http://0.0.0.0:8081/any-invalid-path")
    print("  - File Reference Expired:    http://0.0.0.0:8081/test/file-ref-expired")
    print("  - Rate Limit:                http://0.0.0.0:8081/test/rate-limit")
    print("  - Invalid File:              http://0.0.0.0:8081/test/invalid-file")
    print("  - Access Denied:             http://0.0.0.0:8081/test/access-denied")
    print("  - Generic Error:             http://0.0.0.0:8081/test/generic-error")
    print()
    print("All error pages:")
    print("  ✓ Use the same CSS/HTML structure as the home page")
    print("  ✓ Display user-friendly error messages")
    print("  ✓ Show error details without exposing sensitive information")
    print("  ✓ Use red color (#e74c3c) for error messages")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 80)
    print()
    
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8081)
