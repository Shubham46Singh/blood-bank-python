"""Pure donor-matching rules.

No database, no HTTP, no Redis. This is the file to unit test, and it is
unusually rewarding: blood compatibility is a fixed, well-defined table of
8 x 8 = 64 cases, so you can test every single one.

The rules are NOT hard-coded as a table on purpose. They are derived from
what is actually in the blood, which is both shorter and harder to get
subtly wrong:

    A blood group carries up to three antigens - A, B and RhD.
    A donor is compatible with a recipient when every antigen the DONOR
    carries is also carried by the RECIPIENT.

Everything famous falls out of that one rule:
    O negative carries nothing   -> compatible with everybody
    AB positive carries all three -> can receive from everybody
"""
from datetime import date, timedelta

GROUPS = ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"]

#: Minimum gap between whole-blood donations.
DONATION_GAP_DAYS = 90

#: Age limits for donating.
MIN_AGE = 18
MAX_AGE = 65


class UnknownGroup(ValueError):
    """Raised when a blood group is not one of the eight."""


def antigens(group):
    """The set of antigens a blood group carries."""
    g = str(group).strip().upper()
    if g not in GROUPS:
        raise UnknownGroup(f"{group!r} is not a blood group")
    out = set()
    letters = g[:-1]          # strip the trailing + or -
    if "A" in letters:
        out.add("A")
    if "B" in letters:
        out.add("B")
    if g.endswith("+"):
        out.add("RhD")
    return out


def can_donate(donor, recipient):
    """True when `donor` blood may be given to `recipient`.

    Note this is NOT symmetric. O- can donate to A+, but A+ cannot donate
    to O-. Students invert this constantly, so test both directions.
    """
    return antigens(donor).issubset(antigens(recipient))


def compatible_donors(recipient):
    """Every group that may donate to this recipient, in a stable order."""
    return [g for g in GROUPS if can_donate(g, recipient)]


def compatible_recipients(donor):
    """Every group this donor may give to, in a stable order."""
    return [g for g in GROUPS if can_donate(donor, g)]


def is_eligible(last_donation, today=None, age=None):
    """Can this person donate today?

    Returns (True, None) or (False, reason).
    """
    today = today or date.today()

    if age is not None and not (MIN_AGE <= age <= MAX_AGE):
        return False, f"age must be between {MIN_AGE} and {MAX_AGE}"

    if last_donation is None:
        return True, None

    if last_donation > today:
        return False, "last donation is in the future"

    next_allowed = last_donation + timedelta(days=DONATION_GAP_DAYS)
    if today < next_allowed:
        days = (next_allowed - today).days
        return False, f"must wait {days} more day(s)"

    return True, None


def rank_donors(donors, recipient_group, today=None):
    """Compatible, eligible donors, nearest first.

    `donors` is a list of dicts with group, distance_km and last_donation.
    """
    today = today or date.today()
    out = []
    for d in donors:
        if not can_donate(d["group"], recipient_group):
            continue
        ok, reason = is_eligible(d.get("last_donation"), today, d.get("age"))
        if not ok:
            continue
        out.append(d)
    return sorted(out, key=lambda d: (d.get("distance_km", 9999), d["group"]))
