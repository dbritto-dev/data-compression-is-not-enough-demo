import json
import pathlib as path
import unicodedata
import re

from flask import Flask, Response, request


app = Flask(__name__)


@app.route("/")
def hello_world():
    data = {"message": "Hello World!"}
    response = Response(json.dumps(data), content_type="application/json")

    return response


@app.route("/api/demo")
def optimized_json_response():
    data = read_json_response(path.Path(__file__).parent / "data.json") * 5

    compact = request.args.get("compact") == "true"
    compress = request.args.get("compress")
    normalize = request.args.get("normalize") == "true"
    lean = request.args.get("lean") == "true"

    response_headers = {"content-type": "application/json"}

    response_data = data.copy()

    if lean:
        response_data = lean_data(response_data)

    if normalize:
        response_data = normalize_data(response_data)

    response_data = json.dumps(
        response_data, separators=(",", ":") if compact else None
    ).encode()

    # Move to NGINX (HTTP/Web Server). Just for testing purposes, DO NOT DO THIS ON PRODUCTION.
    if compress == "gzip":
        import gzip

        response_data = gzip.compress(response_data)
        response_headers["content-encoding"] = "gzip"

    # Move to NGINX (HTTP/Web Server). Just for testing purposes, DO NOT DO THIS ON PRODUCTION.
    if compress == "brotli":
        import brotli

        response_data = brotli.compress(response_data)
        response_headers["content-encoding"] = "br"

    return Response(response_data, headers=response_headers)


def read_json_response(filepath: path.Path) -> list[dict]:
    with open(filepath, "r") as f:
        return json.loads(f.read())


def exclude_falsy_values(item: dict):
    return {key: value for key, value in item.items() if value}


def lean_data(items: list[dict]) -> list[dict]:
    return [exclude_falsy_values(item) for item in items]


def normalize_data(items: list[dict]) -> dict:
    if not items:
        return items

    event = None
    listings = []
    ticket_types = {}
    providers = {}
    sections = {}
    blocks = {}
    rows = {}
    for item in items:
        normalized_listing = {
            "id": item["listingId"],
            "quantity": item["quantity"],
            "deep_link": item["deepLink"],
            "price": item.get("sellValue", 0),
            "final_rice": item.get("sellValue", 0) + item.get("totalFee", 0),
        }

        if not event:
            event = {"id": item["eventId"], "slug": item["eventSlug"]}

        category_blocks = item.get("catBlocks")
        if category_blocks:
            normalized_listing["category_blocks"] = category_blocks

        seating_quantity = item.get("seatingQty")
        if seating_quantity:
            normalized_listing["seating_quantity"] = seating_quantity

        ticket_type = item.get("ticketType")
        ticket_type_id = None
        if ticket_type:
            ticket_type_id = slugify(ticket_type)
            if ticket_type_id not in ticket_types:
                ticket_types[ticket_type_id] = {
                    "id": ticket_type_id,
                    "name": ticket_type,
                }
            normalized_listing["ticket_type_id"] = ticket_type_id

        provider = item.get("providerName")
        provider_id = None
        if provider:
            provider_id = slugify(provider)
            if provider_id not in providers:
                providers[provider_id] = {
                    "id": provider_id,
                    "name": provider,
                }
            normalized_listing["provider_id"] = provider_id

        section = item.get("section")
        section_id = None
        if section:
            section_id = slugify(section)
            if section_id not in sections:
                sections[section_id] = {
                    "id": section_id,
                    "name": section,
                }
            normalized_listing["section_id"] = section_id

        block = item.get("block")
        block_id = None
        if block:
            block_id = slugify(block)
            if block_id not in blocks:
                blocks[block_id] = {
                    "id": block_id,
                    "name": block,
                }
            normalized_listing["block_id"] = block_id

        row = item.get("row")
        row_id = None
        if row:
            row_id = slugify(row)
            if row_id not in rows:
                rows[row_id] = {
                    "id": row_id,
                    "name": row,
                }
            normalized_listing["row_id"] = row_id

        listings.append(normalized_listing)

    return {
        "event": event,
        "providers": providers,
        "ticket_types": ticket_types,
        "sections": sections,
        "blocks": blocks,
        "rows": rows,
        "listings": listings,
    }


def slugify(value: str) -> str:
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")
