"""One-shot remap: bring existing service rows in line with the new
official Category enum (Phase 3 prep).

Uses raw SQL UPDATE so it bypasses SQLModel's enum validation - the new
enum no longer accepts the old names, so loading rows through SQLModel
would fail before we have a chance to remap them.

Idempotent: running twice has no effect (the old names disappear after
the first pass).

Usage (from backend/):
    python -m scripts.remap_categories
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.database import engine  # noqa: E402
from app.models import Category  # noqa: E402


# Old enum NAME -> new enum NAME. SQLite stores .name (e.g. "JARDINAGE"),
# not the human-readable .value, so we remap by name.
NAME_REMAP = {
    "ELECTRICITE_MACONNERIE": Category.REPARATIONS_TRAVAUX.name,
    "JARDINAGE": Category.JARDINAGE_ENTRETIEN.name,
    "PECHE_CHASSE": Category.REPARATIONS_TRAVAUX.name,
    "RESTAURATION_PROMO": Category.RESTAURATION_BONS_PLANS.name,
}

VALID_NAMES = {member.name for member in Category}


def remap() -> None:
    with engine.begin() as conn:
        before = dict(conn.execute(text(
            "SELECT category, COUNT(*) FROM service GROUP BY category"
        )).all())
        print("BEFORE:")
        for cat, n in sorted(before.items()):
            print(f"  {n:>2}  {cat}")

        for old_name, new_name in NAME_REMAP.items():
            result = conn.execute(
                text("UPDATE service SET category = :new WHERE category = :old"),
                {"new": new_name, "old": old_name},
            )
            print(f"  remapped {result.rowcount:>2}  {old_name} -> {new_name}")

        after = dict(conn.execute(text(
            "SELECT category, COUNT(*) FROM service GROUP BY category"
        )).all())
        print("AFTER:")
        for cat, n in sorted(after.items()):
            marker = " " if cat in VALID_NAMES else " !!"
            print(f"  {n:>2} {marker} {cat}")

        invalid = {cat: n for cat, n in after.items() if cat not in VALID_NAMES}
        if invalid:
            raise RuntimeError(
                f"Invalid categories remain after remap: {invalid}"
            )

    total_before = sum(before.values())
    total_after = sum(after.values())
    if total_before != total_after:
        raise RuntimeError(
            f"Row-count drift: {total_before} -> {total_after}"
        )
    print(f"OK - {total_after} services, all categories valid.")


if __name__ == "__main__":
    remap()
