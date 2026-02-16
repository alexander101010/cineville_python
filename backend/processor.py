import argparse
import logging

from logic import (
    build_summary,
    load_members,
    load_visits,
    print_top_members,
    print_total_walk_ins,
    validate_and_group_visits,
    write_output,
    write_summary,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Cineville visits-per-member report generator.")
    parser.add_argument(
        "--members",
        default="backend/data/members.csv",
        help="Path to members.csv",
    )
    parser.add_argument(
        "--visits",
        default="backend/data/visits.csv",
        help="Path to visits.csv",
    )
    parser.add_argument(
        "--output",
        default="backend/data/output.csv",
        help="Path to output CSV",
    )
    parser.add_argument(
        "--summary",
        default="backend/data/summary.json",
        help="Path to summary JSON (used by the FastAPI UI)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s: %(message)s",
    )

    members = load_members(args.members)
    visits = load_visits(args.visits)
    grouped_data, walk_in_count = validate_and_group_visits(members, visits)

    write_output(args.output, grouped_data)
    summary = build_summary(
        grouped_data=grouped_data,
        walk_in_count=walk_in_count,
        top_n=5,
    )
    write_summary(args.summary, summary)

    # Bonus outputs
    print_top_members(grouped_data, top_n=5)
    print_total_walk_ins(walk_in_count)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
