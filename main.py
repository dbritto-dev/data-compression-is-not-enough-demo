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
def api_demo():
    data = read_json_response(path.Path(__file__).parent / "data.json") * 5

    compact = request.args.get("compact") == "true"
    compress = request.args.get("compress")
    normalize = request.args.get("normalize") == "true"
    lean = request.args.get("lean") == "true"

    response_headers = {}

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

    return Response(
        response_data, content_type="application/json", headers=response_headers
    )


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
    ticket_type_ids = {}
    ticket_types = {}
    provider_ids = {}
    providers = {}
    section_ids = {}
    sections = {}
    block_ids = {}
    blocks = {}
    row_ids = {}
    rows = {}
    for item in items:
        normalized_listing = {
            "id": item["listingId"],
            "quantity": item["quantity"],
            "deep_link": item["deepLink"],
            "price": item.get("sellValue", 0),
            "final_price": item.get("sellValue", 0) + item.get("totalFee", 0),
        }

        if not event:
            event = {"id": item["eventId"], "slug": item["eventSlug"]}

        category_blocks = item.get("categoryBlocks")
        if category_blocks:
            normalized_listing["category_blocks"] = unique_list(category_blocks)

        seating_quantity = item.get("seatingQty")
        if seating_quantity:
            normalized_listing["seating_quantity"] = seating_quantity

        ticket_type = item.get("ticketType")
        ticket_type_id = None
        if ticket_type:
            ticket_type_id_key = slugify(ticket_type)
            ticket_type_id = ticket_type_ids.get(ticket_type_id_key)
            if not ticket_type_id:
                ticket_type_id = len(ticket_type_ids.keys()) + 1
                ticket_type_ids[ticket_type_id_key] = ticket_type_id
            if ticket_type_id and ticket_type_id not in ticket_types:
                ticket_types[ticket_type_id] = {
                    "id": ticket_type_id,
                    "name": ticket_type,
                }
            normalized_listing["ticket_type_id"] = ticket_type_id

        provider = item.get("providerName")
        provider_id = None
        if provider:
            provider_id_key = slugify(provider)
            provider_id = provider_ids.get(provider_id_key)
            if not provider_id:
                provider_id = len(provider_ids.keys()) + 1
                provider_ids[provider_id_key] = provider_id
            if provider_id and provider_id not in providers:
                providers[provider_id] = {
                    "id": provider_id,
                    "name": provider,
                }
            normalized_listing["provider_id"] = provider_id

        section = item.get("section")
        section_id = None
        if section:
            section_id_key = slugify(section)
            section_id = section_ids.get(section_id_key)
            if not section_id:
                section_id = len(section_ids.keys()) + 1
                section_ids[section_id_key] = section_id
            if section_id and section_id not in sections:
                sections[section_id] = {
                    "id": section_id,
                    "name": section,
                }
            normalized_listing["section_id"] = section_id

        block = item.get("block")
        block_id = None
        if block:
            block_id_key = slugify(block)
            block_id = block_ids.get(block_id_key)
            if not block_id:
                block_id = len(block_ids.keys()) + 1
                block_ids[block_id_key] = block_id
            if block_id and block_id not in blocks:
                blocks[block_id] = {
                    "id": block_id,
                    "name": block,
                }
            normalized_listing["block_id"] = block_id

        row = item.get("row")
        row_id = None
        if row:
            row_id_key = slugify(row)
            row_id = row_ids.get(row_id_key)
            if not row_id:
                row_id = len(row_ids.keys()) + 1
                row_ids[row_id_key] = row_id
            if row_id and row_id not in rows:
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


def unique_list(values: list) -> list:
    return list(set(values))
