import csv

from backend.logic import (
    Visit,
    build_summary,
    load_members,
    load_visits,
    validate_and_group_visits,
    write_output,
)


def write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def test_load_members_dedupes_and_skips_invalid(tmp_path):
    members_path = tmp_path / "members.csv"
    write_csv(
        members_path,
        ["member_id", "barcode"],
        [
            ["m1", "b1"],
            ["", "b2"],  # invalid missing member_id
            ["m2", ""],  # invalid missing barcode
            ["m3", "b1"],  # duplicate barcode
        ],
    )

    members = load_members(members_path)

    assert members == {"b1": "m1"}


def test_load_visits_skips_missing_visit_id_and_normalizes_reservation(tmp_path):
    visits_path = tmp_path / "visits.csv"
    write_csv(
        visits_path,
        ["visit_id", "barcode", "reservation_id"],
        [
            ["v1", "b1", ""],
            ["", "b2", "r2"],  # invalid missing visit_id
        ],
    )

    visits = load_visits(visits_path)

    assert len(visits) == 1
    assert visits[0].visit_id == "v1"
    assert visits[0].reservation_id is None


def test_validate_and_group_visits_and_walkins():
    members = {"b1": "m1"}
    visits = [
        Visit(visit_id="v1", barcode="b1", reservation_id=None),
        Visit(visit_id="v2", barcode="", reservation_id="r2"),
        Visit(visit_id="v3", barcode="b2", reservation_id="r3"),
    ]

    grouped, walkins = validate_and_group_visits(members, visits)

    assert grouped == {("m1", "b1"): ["v1"]}
    assert walkins == 1


def test_write_output_format(tmp_path):
    output_path = tmp_path / "output.csv"
    grouped = {("m1", "b1"): ["v1", "v2"]}

    write_output(output_path, grouped)

    content = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert content[0] == "member_id,barcode,visits"
    assert content[1] == "m1,b1,[v1, v2]"


def test_build_summary_includes_bonus_fields():
    members = {"b1": "m1", "b2": "m2"}
    visits = [
        Visit(visit_id="v1", barcode="b1", reservation_id=None),
        Visit(visit_id="v2", barcode="b1", reservation_id="r2"),
        Visit(visit_id="v3", barcode="b2", reservation_id=None),
    ]
    grouped = {
        ("m1", "b1"): ["v1", "v2"],
        ("m2", "b2"): ["v3"],
    }

    summary = build_summary(
        members_path="members.csv",
        visits_path="visits.csv",
        output_path="output.csv",
        members=members,
        visits=visits,
        grouped_data=grouped,
        walk_in_count=2,
        top_n=5,
    )

    assert summary["total_walk_ins"] == 2
    assert summary["top_members"][0]["member_id"] == "m1"
    assert summary["top_members"][0]["visit_count"] == 2
