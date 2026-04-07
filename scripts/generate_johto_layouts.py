#!/usr/bin/env python3

import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "johto_layouts"
ATLAS_PATH = ROOT / "data" / "johto_tilesets" / "tileset_inventory.json"


def load_atlas():
    return json.loads(ATLAS_PATH.read_text())


def load_semantic_tiles(atlas):
    semantic_tiles = {}
    for tile in atlas.get("semantic_tiles", []):
        semantic_tiles[tile["id"]] = int(tile["entry"], 16)
    return semantic_tiles


def load_block_templates(atlas):
    block_templates = {}
    for template_id, tokens in atlas.get("block_templates", {}).items():
        if len(tokens) != 4:
            raise ValueError(f"{ATLAS_PATH}: block template '{template_id}' must contain 4 metatile tokens")
        block_templates[template_id] = tokens
    return block_templates


ATLAS = load_atlas()
SEMANTIC_TILES = load_semantic_tiles(ATLAS)
BLOCK_TEMPLATES = load_block_templates(ATLAS)


def resolve_source_path(source: str) -> Path:
    path = Path(source)
    if path.is_absolute():
        return path

    candidates = [
        ROOT / path,
        ROOT.parent / path,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return ROOT / path


def is_hex_token(token: str):
    try:
        int(token, 16)
        return True
    except ValueError:
        return False


def parse_metatile_token(spec_path: Path, token: str, semantic_only: bool):
    if token in SEMANTIC_TILES:
        return SEMANTIC_TILES[token]
    if semantic_only and is_hex_token(token):
        raise ValueError(f"{spec_path}: raw metatile token '{token}' is not allowed in semantic_only specs")
    try:
        return int(token, 16)
    except ValueError as exc:
        raise ValueError(f"{spec_path}: unknown semantic tile '{token}'") from exc


def parse_hex_row(spec_path: Path, row_index: int, row: str, expected_width: int, semantic_only: bool):
    values = [parse_metatile_token(spec_path, part, semantic_only) for part in row.split()]
    if len(values) != expected_width:
        raise ValueError(
            f"{spec_path}: expected {expected_width} metatiles in row {row_index}, found {len(values)}"
        )
    return values


def expand_metatile_rows(spec_path: Path, spec) -> bytes:
    metatile_rows = spec["metatile_rows"]
    width = spec["width"]
    height = spec["height"]
    semantic_only = spec.get("semantic_only", False)
    if len(metatile_rows) != height:
        raise ValueError(f"{spec_path}: expected {height} metatile rows, found {len(metatile_rows)}")

    parsed_rows = [
        parse_hex_row(spec_path, row_index, row, width, semantic_only)
        for row_index, row in enumerate(metatile_rows)
    ]
    return b"".join(struct.pack("<H", value) for row in parsed_rows for value in row)


def parse_chunk_token(spec_path: Path, token: str, semantic_only: bool):
    if token in BLOCK_TEMPLATES:
        return [parse_metatile_token(spec_path, value, semantic_only) for value in BLOCK_TEMPLATES[token]]

    values = token.split()
    if len(values) != 4:
        raise ValueError(f"{spec_path}: chunk '{token}' does not contain 4 metatile values")
    return [parse_metatile_token(spec_path, value, semantic_only) for value in values]


def expand_chunk_rows(spec_path: Path, spec) -> bytes:
    chunk_rows = spec["chunk_rows"]
    chunk_width = spec["chunk_width"]
    chunk_height = spec["chunk_height"]
    semantic_only = spec.get("semantic_only", False)
    if len(chunk_rows) != chunk_height:
        raise ValueError(f"{spec_path}: expected {chunk_height} chunk rows, found {len(chunk_rows)}")

    metatile_rows = []
    for row_index, chunk_row in enumerate(chunk_rows):
        if len(chunk_row) != chunk_width:
            raise ValueError(
                f"{spec_path}: expected {chunk_width} chunks in row {row_index}, found {len(chunk_row)}"
            )

        top_row = []
        bottom_row = []
        for chunk in chunk_row:
            values = parse_chunk_token(spec_path, chunk, semantic_only)
            tl, tr, bl, br = values
            top_row.extend((tl, tr))
            bottom_row.extend((bl, br))

        metatile_rows.append(top_row)
        metatile_rows.append(bottom_row)

    return b"".join(struct.pack("<H", value) for row in metatile_rows for value in row)


def expand_crystal_blk(spec_path: Path, spec) -> bytes:
    crystal_blk_path = resolve_source_path(spec["crystal_blk"])
    block_width = spec["crystal_chunk_width"] if "crystal_chunk_width" in spec else spec["chunk_width"]
    block_height = spec["crystal_chunk_height"] if "crystal_chunk_height" in spec else spec["chunk_height"]
    semantic_only = spec.get("semantic_only", False)
    canvas_width = spec.get("canvas_chunk_width", block_width)
    canvas_height = spec.get("canvas_chunk_height", block_height)
    anchor_chunk_x = spec.get("anchor_chunk_x", 0)
    anchor_chunk_y = spec.get("anchor_chunk_y", 0)

    block_rows = crystal_blk_path.read_bytes()
    if len(block_rows) != block_width * block_height:
        raise ValueError(
            f"{spec_path}: expected {block_width * block_height} bytes in {crystal_blk_path}, found {len(block_rows)}"
        )
    if anchor_chunk_x + block_width > canvas_width or anchor_chunk_y + block_height > canvas_height:
        raise ValueError(
            f"{spec_path}: crystal block area {(block_width, block_height)} at anchor {(anchor_chunk_x, anchor_chunk_y)} "
            f"does not fit in canvas {(canvas_width, canvas_height)}"
        )

    block_map = {}
    for block_id, chunk in spec["block_map"].items():
        try:
            normalized_id = int(block_id, 16)
        except ValueError as exc:
            raise ValueError(f"{spec_path}: invalid block_map key '{block_id}'") from exc
        block_map[normalized_id] = parse_chunk_token(spec_path, chunk, semantic_only)

    if "canvas_chunk_rows" in spec:
        base_rows = spec["canvas_chunk_rows"]
        if len(base_rows) != canvas_height:
            raise ValueError(f"{spec_path}: expected {canvas_height} canvas chunk rows, found {len(base_rows)}")
        canvas_chunks = []
        for row_index, chunk_row in enumerate(base_rows):
            if len(chunk_row) != canvas_width:
                raise ValueError(
                    f"{spec_path}: expected {canvas_width} canvas chunks in row {row_index}, found {len(chunk_row)}"
                )
            canvas_chunks.append([parse_chunk_token(spec_path, chunk, semantic_only) for chunk in chunk_row])
    else:
        fill_chunk = parse_chunk_token(spec_path, spec.get("canvas_fill_chunk", "0000 0000 0000 0000"), semantic_only)
        canvas_chunks = [[list(fill_chunk) for _ in range(canvas_width)] for _ in range(canvas_height)]

    for row_index in range(block_height):
        for column_index in range(block_width):
            block_id = block_rows[row_index * block_width + column_index]
            if block_id not in block_map:
                raise ValueError(
                    f"{spec_path}: Crystal block 0x{block_id:02X} at ({column_index}, {row_index}) has no mapping"
                )
            canvas_chunks[anchor_chunk_y + row_index][anchor_chunk_x + column_index] = list(block_map[block_id])

    metatile_rows = []
    for chunk_row in canvas_chunks:
        top_row = []
        bottom_row = []
        for tl, tr, bl, br in chunk_row:
            top_row.extend((tl, tr))
            bottom_row.extend((bl, br))
        metatile_rows.append(top_row)
        metatile_rows.append(bottom_row)

    return b"".join(struct.pack("<H", value) for row in metatile_rows for value in row)


def write_border(spec_path: Path, spec) -> None:
    if "border_metatiles" not in spec:
        return

    border_metatiles = spec["border_metatiles"]
    if len(border_metatiles) != 4:
        raise ValueError(f"{spec_path}: border_metatiles must contain 4 metatile tokens")

    border_values = [
        parse_metatile_token(spec_path, token, spec.get("semantic_only", False))
        for token in border_metatiles
    ]
    border_output = Path(spec["output"]).with_name("border.bin")
    border_path = ROOT / border_output
    border_path.write_bytes(b"".join(struct.pack("<H", value) for value in border_values))
    print(f"updated {border_path.relative_to(ROOT)} from {spec_path.relative_to(ROOT)}")


def generate_layout(spec_path: Path) -> None:
    spec = json.loads(spec_path.read_text())
    output_path = ROOT / spec["output"]
    if "crystal_blk" in spec:
        output = expand_crystal_blk(spec_path, spec)
    elif "metatile_rows" in spec:
        output = expand_metatile_rows(spec_path, spec)
    else:
        output = expand_chunk_rows(spec_path, spec)
    output_path.write_bytes(output)
    print(f"updated {output_path.relative_to(ROOT)} from {spec_path.relative_to(ROOT)}")
    write_border(spec_path, spec)


def main() -> int:
    if not SOURCE_DIR.is_dir():
        print(f"missing source directory: {SOURCE_DIR}", file=sys.stderr)
        return 1

    for spec_path in sorted(SOURCE_DIR.glob("*.json")):
        generate_layout(spec_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
