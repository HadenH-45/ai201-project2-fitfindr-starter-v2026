"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── query parsing ─────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a max_price out of a plain-language query.

    Chosen approach: regex. Price is read from "under $X" first, falling back
    to a bare "$X" anywhere in the query. Size is read from "size X" (X can be
    letters, digits, or a slash-separated combo like "S/M"). Whatever text is
    left after stripping those phrases out becomes the description.
    """
    max_price = None
    under_match = re.search(r"under\s+\$?(\d+(?:\.\d+)?)", query, re.IGNORECASE)
    if under_match:
        max_price = float(under_match.group(1))
    else:
        price_match = re.search(r"\$(\d+(?:\.\d+)?)", query)
        if price_match:
            max_price = float(price_match.group(1))

    size = None
    size_match = re.search(r"\bsize\s+([A-Za-z0-9/]+)", query, re.IGNORECASE)
    if size_match:
        size = size_match.group(1)

    description = query
    description = re.sub(r"under\s+\$?\d+(?:\.\d+)?", "", description, flags=re.IGNORECASE)
    description = re.sub(r"\$\d+(?:\.\d+)?", "", description)
    description = re.sub(r"\bsize\s+[A-Za-z0-9/]+", "", description, flags=re.IGNORECASE)
    description = re.sub(r"\s+", " ", description).strip()

    return {"description": description, "size": size, "max_price": max_price}


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    session = new_session(query, wardrobe)

    count = 0
    count += 1
    trace.check_iterations(count)

    # 3. Parse the query into description / size / max_price.
    session["parsed"] = _parse_query(query)

    # 4. Search for listings. THIS IS THE BRANCH.
    results = search_listings(
        description=session["parsed"]["description"],
        size=session["parsed"]["size"],
        max_price=session["parsed"]["max_price"],
    )
    session["search_results"] = results

    if not results:
        parsed = session["parsed"]
        session["error"] = (
            "No listings matched "
            f"description={parsed['description']!r}, size={parsed['size']!r}, "
            f"max_price={parsed['max_price']!r}. Try a broader description, "
            "a higher max_price, or a different size."
        )
        return session

    # 5. Choose an item — the first result.
    session["selected_item"] = results[0]

    # 6. Suggest an outfit.
    session["outfit_suggestion"] = suggest_outfit(session["selected_item"], wardrobe)

    # 7. Create the fit card.
    session["fit_card"] = create_fit_card(session["outfit_suggestion"], session["selected_item"])

    # 8. Return the finished session.
    return session

    # ─────────────────────────────────────────────────────────────────────
    # IN UNIT 4 you come back and add two things:
    #
    #   • Trace calls. One per step. `trace.step("search_listings",
    #     inputs=..., returned=...)` — see trace.py. Your README needs the
    #     output.
    #
    #   • A handler for ModelUnavailable, so a bad key produces a message
    #     rather than a stack trace. The import is already at the top of
    #     this file.
    # ─────────────────────────────────────────────────────────────────────


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )