import typing

from ddtrace_asgi.middleware import TraceMiddleware
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import BaseRoute, Host, Mount, Route

from . import blog, resources, settings
from .endpoints import DomainRedirect
from .middleware import (
    LegacyRedirectMiddleware,
    PatchHeadersMiddleware,
    RequestedHostSpanTagMiddleware,
)


async def home(request: Request) -> Response:
    return resources.templates.TemplateResponse(
        "index.html.jinja", context={"request": request}
    )


async def error(request: Request) -> Response:
    if settings.TESTING:
        raise RuntimeError("Example server error")
    return RedirectResponse("/")  # pragma: no cover


routes: typing.List[BaseRoute] = [
    Host("florimondmanca.com", app=DomainRedirect("florimond.dev")),
    Host(
        "blog.florimondmanca.com",
        app=DomainRedirect("blog.florimond.dev"),
        name="legacy__blog_dot_com",
    ),
    Host(
        "blog.florimond.dev",
        app=DomainRedirect("florimond.dev", root_path="/blog"),
        name="legacy__blog_dot_dev",
    ),
    Route("/", home),
    Route("/error", error),
    Mount("/blog", routes=blog.routes, name="blog"),
    Mount("/static", resources.static, name="static"),
    # Make the SCSS source available to browsers for inspection.
    Mount("/sass", resources.sass),
    # These files need to be exposed at the root, not '/static/'.
    Route("/favicon.ico", resources.static, name="favicon"),
    Route("/robots.txt", resources.static, name="robots"),
    Route("/sitemap.xml", resources.static, name="sitemap"),
    Route(
        "/feed.rss",
        # Make sure clients always receive the correct MIME type for the RSS feed,
        # as the content type Starlette guesses may vary across operating systems.
        PatchHeadersMiddleware(
            resources.static, headers={"content-type": "application/rss+xml"}
        ),
        name="feed-rss",
    ),
]


middleware = [
    Middleware(
        TraceMiddleware,
        tracer=resources.tracer,
        service="www",
        tags=settings.WEB_DD_TRACE_TAGS,
    ),
    Middleware(RequestedHostSpanTagMiddleware),
    Middleware(
        LegacyRedirectMiddleware,
        url_mapping=settings.BLOG_LEGACY_URL_MAPPING,
        root_path="/blog",
    ),
]


async def not_found(request: Request, exc: Exception) -> Response:
    return resources.templates.TemplateResponse(
        "404.html.jinja", context={"request": request}, status_code=404
    )


async def internal_server_error(request: Request, exc: Exception) -> Response:
    return resources.templates.TemplateResponse(
        "500.html.jinja", context={"request": request}, status_code=500
    )


app = Starlette(
    debug=settings.DEBUG,
    middleware=middleware,
    routes=routes,
    exception_handlers={404: not_found, 500: internal_server_error},
    on_startup=[blog.on_startup],
)
