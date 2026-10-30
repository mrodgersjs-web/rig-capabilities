#!/usr/bin/env python3
"""Count first-five completion from local approval-linked receipt chains."""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path


def bound_file(item, root):
    path = Path(item["path"])
    if not path.is_absolute():
        path = root / path
    if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
        raise ValueError("Referenced evidence is missing or changed")
    return path


def check(record, root):
    identity = (record["employer"], record["requisition_id"], record["destination"])
    if not all(isinstance(x, str) and x.strip() for x in identity):
        raise ValueError("Missing application identity")
    draft = record["draft"]
    final = record["final_resume"]
    answers = record["answers"]
    for item in (draft, final, answers):
        bound_file(item, root)
    review = json.loads(bound_file(record["evidence_review"], root).read_text())
    approval = json.loads(bound_file(record["submission_approval"], root).read_text())
    receipt = json.loads(bound_file(record["submission_receipt"], root).read_text())
    if review.get("draft_sha256") != draft["sha256"] or review.get("final_resume_sha256") != final["sha256"] or review.get("status") != "factually_confirmed" or not review.get("human_response_reference") or not review.get("human_page_approval_reference"):
        raise ValueError("Missing exact factual review or human rendered-page approval")
    if approval.get("action") != "submit_this_application" or not approval.get("human_response_reference"):
        raise ValueError("Missing specific human submission approval")
    if approval.get("final_resume_sha256") != final["sha256"] or approval.get("answers_sha256") != answers["sha256"]:
        raise ValueError("Submission approval content mismatch")
    for event in (approval, receipt):
        if tuple(event.get(key) for key in ("employer", "requisition_id", "destination")) != identity:
            raise ValueError("Application identity mismatch")
    if receipt.get("status") != "submitted" or not receipt.get("provider_receipt_id"):
        raise ValueError("No actual provider receipt recorded")
    times = [datetime.fromisoformat(event[field].replace("Z", "+00:00")) for event, field in ((review, "reviewed_at"), (approval, "approved_at"), (receipt, "submitted_at"))]
    if any(value.tzinfo is None for value in times) or not times[0] <= times[1] <= times[2]:
        raise ValueError("Resume review, specific approval, and submission must have timezone-aware timestamps in that order")
    bound_file(receipt["provider_evidence"], root)
    return identity, receipt["provider_receipt_id"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="JSON object with an applications array; no data shipped")
    args = parser.parse_args()
    data = json.loads(args.ledger.read_text())
    records = data["applications"]
    if not isinstance(records, list):
        parser.error("applications must be an array")
    identities, receipts, rejected = set(), set(), []
    for index, record in enumerate(records):
        try:
            identity, receipt_id = check(record, args.ledger.parent)
            if identity in identities or receipt_id in receipts:
                raise ValueError("Duplicate application or receipt")
            identities.add(identity)
            receipts.add(receipt_id)
        except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            rejected.append({"index": index, "reason": str(exc)})
    print(json.dumps({"qualifying_receipt_count": len(identities), "pilot_progress": str(min(5, len(identities))) + "/5", "rejected": rejected, "independent_provider_authenticity": "NOT_VERIFIED_BY_THIS_OFFLINE_HELPER", "autonomous_submission_authorized": False}, indent=2))


if __name__ == "__main__":
    main()
