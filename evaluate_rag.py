import requests
import json
from dataclasses import dataclass
from typing import List, Optional

API_URL = "http://127.0.0.1:8000/query"


@dataclass
@dataclass
class TestCase:
    query: str
    expected_articles: List[int]   # at least one must appear in top-k
    note: str
    language: str = "en"           # "en" or "ar"

GROUND_TRUTH = [
    TestCase(
        query="My uncle was declared legally restricted and sold his car two weeks before the court decision was officially recorded. The buyer knew about his condition. Can the sale be undone?",
        expected_articles=[115],
        note="Interdiction before registration — core Article 115 case",
    ),
    TestCase(
        query="If someone under a prodigality ruling signs a lease after the judgment is registered, is that lease valid?",
        expected_articles=[115],
        note="Interdiction after registration — second part of Article 115",
    ),
    TestCase(
        query="A man was placed under interdiction for wasteful spending. He made a gift to a friend before registration. The friend clearly took advantage of him. Is the gift valid?",
        expected_articles=[115],
        note="Fraudulent collusion pre-registration — Article 115 edge case",
    ),
    TestCase(
        query="Can a person under interdiction for imbecility create a wakf if the court authorizes it?",
        expected_articles=[116],
        note="Wakf by interdicted person — Article 116",
    ),
    TestCase(
        query="A deaf-blind person cannot communicate their will. Can the court appoint someone to help them with legal acts?",
        expected_articles=[117],
        note="Judicial adviser for sensory-impaired person — Article 117",
    ),
    TestCase(
        query="Someone promised to sell me their apartment but is now refusing. Can I go to court and force the sale?",
        expected_articles=[102],
        note="Promise to contract and refusal — Article 102",
    ),
    TestCase(
        query="I signed a contract but I made a serious mistake about the nature of the thing I was buying. Can I cancel it?",
        expected_articles=[121],
        note="Essential mistake — Article 121",
    ),
    TestCase(
        query="I was threatened into signing a contract. Is that contract valid?",
        expected_articles=[127],
        note="Duress/coercion — Article 127",
    ),
    TestCase(
        query="Someone took advantage of my desperate financial situation and made me sign an unfair contract. Can a judge reduce my obligations?",
        expected_articles=[129],
        note="Exploitation/lesion — Article 129",
    ),
    TestCase(
        query="We agreed on a contract for something that turned out to be impossible to do. Is the contract void?",
        expected_articles=[132],
        note="Impossible object of contract — Article 132",
    ),
    TestCase(
        query="Part of a contract I signed is illegal. Does that mean the whole contract is void?",
        expected_articles=[143],
        note="Partial voidness — Article 143",
    ),
    TestCase(
        query="If a contract is annulled because one party had no legal capacity, how much must they return?",
        expected_articles=[142],
        note="Restitution after annulment due to incapacity — Article 142",
    ),
    TestCase(
        query="The wording of the contract is very clear. Can the judge still interpret it differently to find the parties' true intention?",
        expected_articles=[150],
        note="Contract interpretation — Article 150",
    ),

    # ── Liability & Tort ──────────────────────────────────────────────
    TestCase(
        query="My employee caused damage to someone while doing his job. Am I responsible as his employer?",
        expected_articles=[174],
        note="Employer liability for employee acts — Article 174",
    ),
    TestCase(
        query="Someone's dog bit me and caused injury. Who is liable?",
        expected_articles=[176],
        note="Animal liability — Article 176",
    ),
    TestCase(
        query="A wall in my neighbor's building collapsed and damaged my property. Who is responsible?",
        expected_articles=[177],
        note="Building collapse liability — Article 177",
    ),
    TestCase(
        query="My neighbor's factory makes a lot of noise and smoke that affects my property beyond normal limits. What can I do?",
        expected_articles=[807],
        note="Neighborhood nuisance — Article 807",
    ),
    TestCase(
        query="Someone caused me harm through their fault. Can I claim compensation?",
        expected_articles=[163],
        note="General tort liability — Article 163",
    ),

    # ── Names & Personal Status ───────────────────────────────────────
    TestCase(
        query="Can someone legally change their first name?",
        expected_articles=[38, 39],
        note="Name change — Articles 38/39, known retrieval gap",
    ),
    TestCase(
        query="Someone is using my name illegally. What can I do?",
        expected_articles=[51],
        note="Name protection — Article 51",
    ),

    # ── Property & Ownership ──────────────────────────────────────────
    TestCase(
        query="I own land next to a lake. The water level dropped and revealed new land. Do I own that land?",
        expected_articles=[920],
        note="Still water land ownership — Article 920",
    ),
    TestCase(
        query="I sold something I didn't actually own. Can the buyer cancel the sale?",
        expected_articles=[466],
        note="Sale of thing not owned — Article 466",
    ),

    # ── Inheritance ───────────────────────────────────────────────────
    TestCase(
        query="How are inheritance shares determined in Egypt?",
        expected_articles=[875],
        note="Inheritance rules — Article 875",
    ),

    # ── Interest & Debt ───────────────────────────────────────────────
    TestCase(
        query="Can interest accumulate on top of unpaid interest?",
        expected_articles=[232],
        note="Compound interest prohibition — Article 232",
    ),

    # ── Arabic queries ────────────────────────────────────────────────
    TestCase(
        query="جدي اتحط تحت الحجر بسبب السفه وقبل ما الحكم يتسجل باع عقار. المشتري كان عارف بحالته. هل البيع ده ممكن يتبطل؟",
        expected_articles=[115],
        note="Arabic: interdiction before registration — Article 115",
        language="ar",
    ),
    TestCase(
        query="اتهددت إني أوقع على عقد وإلا هيحصلي حاجة وحشة. العقد ده قانوني؟",
        expected_articles=[127],
        note="Arabic: duress — Article 127",
        language="ar",
    ),
    TestCase(
        query="كلبي عض جار ليا. أنا مسؤول؟",
        expected_articles=[176],
        note="Arabic colloquial: animal liability — Article 176",
        language="ar",
    ),
    TestCase(
        query="موظف عندي عمل حادثة وهو شغال. أنا مسؤول عن التعويض؟",
        expected_articles=[174],
        note="Arabic: employer liability — Article 174",
        language="ar",
    ),
]


# ─────────────────────────────────────────────
# Evaluation Runner
# ─────────────────────────────────────────────

def run_query(query: str) -> Optional[dict]:
    try:
        response = requests.post(
            API_URL,
            json={"question": query, "chat_history": []},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  ✗ HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"  ✗ Request failed: {e}")
        return None


def evaluate():
    print("=" * 70)
    print("RAG EVALUATION — Egyptian Civil Code Assistant")
    print("=" * 70)

    total = len(GROUND_TRUTH)
    hits_at_3 = 0
    hits_at_5 = 0  # sources list capped at top_k in backend; we check what's returned
    failures = []

    en_total, en_hits = 0, 0
    ar_total, ar_hits = 0, 0

    for i, tc in enumerate(GROUND_TRUTH, 1):
        print(f"\n[{i:02d}/{total}] {tc.note}")
        print(f"  Query ({tc.language}): {tc.query[:90]}{'...' if len(tc.query) > 90 else ''}")
        print(f"  Expected: Article(s) {tc.expected_articles}")

        data = run_query(tc.query)
        if data is None:
            failures.append((tc, "API error", []))
            continue

        retrieved_articles = [src["article"] for src in data.get("sources", [])]
        print(f"  Retrieved: {retrieved_articles}")

        hit = any(art in retrieved_articles for art in tc.expected_articles)

        if hit:
            hits_at_3 += 1
            print(f"  ✓ HIT")
            if tc.language == "en":
                en_hits += 1
            else:
                ar_hits += 1
        else:
            print(f"  ✗ MISS")
            failures.append((tc, data.get("answer", "")[:200], retrieved_articles))

        if tc.language == "en":
            en_total += 1
        else:
            ar_total += 1

    # ── Summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"  Overall Retrieval Accuracy:  {hits_at_3}/{total} = {hits_at_3/total*100:.1f}%")
    print(f"  English queries:             {en_hits}/{en_total} = {en_hits/en_total*100:.1f}%" if en_total else "  English: N/A")
    print(f"  Arabic queries:              {ar_hits}/{ar_total} = {ar_hits/ar_total*100:.1f}%" if ar_total else "  Arabic: N/A")

    # ── Failure Analysis ─────────────────────────────────────────────
    if failures:
        print(f"\n{'=' * 70}")
        print(f"FAILURE CASES ({len(failures)} total)")
        print("=" * 70)
        for tc, answer_snippet, retrieved in failures:
            print(f"\n  Query:    {tc.query[:100]}")
            print(f"  Expected: {tc.expected_articles}")
            print(f"  Got:      {retrieved if retrieved else 'nothing (below threshold)'}")
            print(f"  Note:     {tc.note}")

    print("\n" + "=" * 70)
    print("Done.")
    print("=" * 70)


if __name__ == "__main__":
    evaluate()