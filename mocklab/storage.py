"""Bounded SQLite audit in a caller-owned private directory; one Lab per journal."""

import json
import os
import sqlite3
from pathlib import Path

from .core import LabError, identifier


class Journal:
    def __init__(self, directory, lab_id, limit=1000):
        identifier(lab_id)
        if type(limit) is not int or not 2 <= limit <= 10000:
            raise LabError("invalid_limit")
        directory = Path(directory).absolute()
        # Refuse symlink components and shared directories before opening SQLite.
        for component in (directory, *directory.parents):
            if component.is_symlink():
                raise LabError("unsafe_audit_directory")
        info = directory.stat()
        if not directory.is_dir() or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise LabError("unsafe_audit_directory")
        self.path = directory / "audit.sqlite3"
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        try:
            fd = os.open(self.path, flags, 0o600)
        except FileExistsError:
            info = self.path.lstat()
            if self.path.is_symlink() or not self.path.is_file():
                raise LabError("unsafe_audit_file") from None
            if (
                info.st_uid != os.getuid()
                or info.st_mode & 0o077
                or info.st_nlink != 1
                or info.st_size > 8 * 1024 * 1024
            ):
                raise LabError("unsafe_audit_file") from None
        else:
            os.close(fd)
        self._db = sqlite3.connect(self.path, timeout=1)
        self._db.execute("PRAGMA synchronous=FULL")
        self._db.execute("PRAGMA journal_mode=DELETE")
        self._db.execute("PRAGMA max_page_count=2048")
        with self._db:
            self._db.execute("CREATE TABLE IF NOT EXISTS metadata(lab TEXT, capacity INTEGER)")
            self._db.execute(
                "CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, body TEXT)"
            )
            rows = self._db.execute("SELECT lab, capacity FROM metadata").fetchall()
            if not rows:
                self._db.execute("INSERT INTO metadata VALUES (?, ?)", (lab_id, limit))
        if rows and rows != [(lab_id, limit)]:
            self.close()
            raise LabError("journal_scope_mismatch")
        self.limit = limit
        self.lab_id = lab_id
        # Load only a bounded number of rows from a potentially damaged journal.
        if self._db.execute("SELECT count(*) FROM events").fetchone()[0] > limit:
            self.close()
            raise LabError("journal_corrupt")

    def events(self):
        try:
            if self._db.execute("SELECT count(*) FROM events WHERE length(body)>4096").fetchone()[
                0
            ]:
                raise LabError("journal_corrupt")
            return [
                json.loads(row[0])
                for row in self._db.execute("SELECT body FROM events ORDER BY seq")
            ]
        except (ValueError, sqlite3.Error):
            raise LabError("journal_corrupt") from None

    def append(self, event):
        with self._db:
            count = self._db.execute("SELECT count(*) FROM events").fetchone()[0]
            if count >= self.limit or event["event_id"] != count + 1:
                raise LabError("journal_capacity")
            self._db.execute(
                "INSERT INTO events VALUES (?, ?)",
                (event["event_id"], json.dumps(event, allow_nan=False)),
            )

    def close(self):
        self._db.close()
