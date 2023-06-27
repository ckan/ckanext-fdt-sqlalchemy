from __future__ import annotations

import enum
import logging
from typing import TYPE_CHECKING, Any

from werkzeug.utils import import_string

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model

if TYPE_CHECKING:
    from ckan.common import CKANConfig
    from ckan.config.middleware.flask_app import CKANFlask


SQLAlchemy = import_string("flask_sqlalchemy:SQLAlchemy", silent=True)

# v2.5 class that records SQL queries
_EngineDebuggingSignalEvents: Any = import_string(
    "flask_sqlalchemy:_EngineDebuggingSignalEvents",
    True,
)

# v3.0 module that records SQL queries
record_queries = import_string("flask_sqlalchemy.record_queries", silent=True)

log = logging.getLogger(__name__)


class FdtSqlalchemyPlugin(p.SingletonPlugin):
    p.implements(p.IMiddleware, inherit=True)

    def make_middleware(self, app: CKANFlask, config: CKANConfig):
        if not tk.asbool(tk.config.get("debug")):
            return app

        pip_command = "pip install flask-sqlalchemy~=2.5"
        if FSVersion.is_(FSVersion.UNKNOWN):
            log.error(
                "Flask-SQLAlchemy is not installed."
                " Run `%s` and restart the application",
                pip_command,
            )
            return app

        if tk.check_ckan_version("2.10.0"):
            _csrf_exempt()

        # required config options for flask-sqlalchemy
        app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
        app.config["SQLALCHEMY_DATABASE_URI"] = config["sqlalchemy.url"]

        SQLAlchemy(app)

        if FSVersion.is_(FSVersion.V2):
            # set up event listeners for query recording. It must be called
            # only once for the app instance, because listeners are anonymous
            # and it's possible to register the same listener multiple times.
            #
            # NOT idempotent
            _EngineDebuggingSignalEvents(model.meta.engine, "ckan").register()

        elif FSVersion.is_(FSVersion.V3):
            # set up event listeners for query recording. It can be called
            # multiple times for the app instance, because listeners are named
            # and they won't be duplicated.
            #
            # idempotent
            log.warning(
                "SELECT/EXPLAIN pages from SQLAlchemy pane of"
                " Flask-DebugToolbar do not work with with"
                " flask-sqlalchemy>=3.0. Install fully-compatible version"
                " using the command `%s`",
                pip_command,
            )
            record_queries._listen(model.meta.engine)

        return app


def _csrf_exempt():
    """Disable CSRF protection for Flask-DebugToolbar.

    SELECT/EXPLAIN pages from SQLAlchemy pane are rendered using POST
    request. Flask-DebugToolbar uses it's own version of jQuery and we cannot
    add CSRF token to its AJAX requests. So we have to disable CSRF protection
    for FDT blueprint. As long as no one runs PROD in debug mode, it should be
    ok.

    """
    from flask_debugtoolbar import module

    from ckan.config.middleware.flask_app import csrf

    csrf.exempt(module)


class FSVersion(enum.Enum):
    """Flask-SQLAlchemy version."""

    V2 = enum.auto()
    V3 = enum.auto()
    UNKNOWN = enum.auto()

    @classmethod
    def detect(cls):
        if _EngineDebuggingSignalEvents:
            return cls.V2

        if record_queries:
            return cls.V3

        return cls.UNKNOWN

    @classmethod
    def is_(cls, version: FSVersion):
        return cls.detect() is version
