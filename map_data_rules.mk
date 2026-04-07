# Map JSON data

# Inputs
MAPS_DIR = $(DATA_ASM_SUBDIR)/maps
LAYOUTS_DIR = $(DATA_ASM_SUBDIR)/layouts

# Outputs
MAPS_OUTDIR := $(MAPS_DIR)
LAYOUTS_OUTDIR := $(LAYOUTS_DIR)
INCLUDECONSTS_OUTDIR := include/constants

AUTO_GEN_TARGETS += $(INCLUDECONSTS_OUTDIR)/map_groups.h
AUTO_GEN_TARGETS += $(INCLUDECONSTS_OUTDIR)/layouts.h
AUTO_GEN_TARGETS += $(INCLUDECONSTS_OUTDIR)/map_event_ids.h

MAP_DIRS := $(dir $(wildcard $(MAPS_DIR)/*/map.json))
MAP_CONNECTIONS := $(patsubst $(MAPS_DIR)/%/,$(MAPS_DIR)/%/connections.inc,$(MAP_DIRS))
MAP_EVENTS := $(patsubst $(MAPS_DIR)/%/,$(MAPS_DIR)/%/events.inc,$(MAP_DIRS))
MAP_HEADERS := $(patsubst $(MAPS_DIR)/%/,$(MAPS_DIR)/%/header.inc,$(MAP_DIRS))
MAP_JSONS := $(patsubst $(MAPS_DIR)/%/,$(MAPS_DIR)/%/map.json,$(MAP_DIRS))

JOHTO_TILESET_ATLAS := data/johto_tilesets/tileset_inventory.json
JOHTO_IMPORT_SCRIPT := scripts/import_johto_maps.py
JOHTO_IMPORT_COMMON := scripts/johto_import_common.py
JOHTO_IMPORT_TILESETS := data/johto_import/crystal_tilesets.json
JOHTO_IMPORT_MAPS := data/johto_import/maps.json
JOHTO_IMPORT_STAMP := data/johto_import/.stamp
JOHTO_IMPORTED_LAYOUT_BINARIES := \
	data/layouts/NewBarkTown/map.bin \
	data/layouts/NewBarkTown_PlayersHouse_1F/map.bin \
	data/layouts/NewBarkTown_PlayersHouse_2F/map.bin \
	data/layouts/PlayersNeighborsHouse/map.bin \
	data/layouts/ElmsHouse/map.bin \
	data/layouts/ElmsLab/map.bin
JOHTO_IMPORTED_BORDERS := \
	data/layouts/NewBarkTown/border.bin \
	data/layouts/NewBarkTown_PlayersHouse_1F/border.bin \
	data/layouts/NewBarkTown_PlayersHouse_2F/border.bin \
	data/layouts/PlayersNeighborsHouse/border.bin \
	data/layouts/ElmsHouse/border.bin \
	data/layouts/ElmsLab/border.bin

$(DATA_ASM_BUILDDIR)/maps.o: $(DATA_ASM_SUBDIR)/maps.s $(LAYOUTS_DIR)/layouts.inc $(LAYOUTS_DIR)/layouts_table.inc $(MAPS_DIR)/headers.inc $(MAPS_DIR)/groups.inc $(MAPS_DIR)/connections.inc $(MAP_CONNECTIONS) $(MAP_HEADERS) $(JOHTO_IMPORTED_LAYOUT_BINARIES) $(JOHTO_IMPORTED_BORDERS) $(JOHTO_IMPORT_STAMP)
	$(PREPROC) $< charmap.txt | $(CPP) -I include - | $(PREPROC) -ie $< charmap.txt | $(AS) $(ASFLAGS) -o $@
$(DATA_ASM_BUILDDIR)/map_events.o: $(DATA_ASM_SUBDIR)/map_events.s $(MAPS_DIR)/events.inc $(MAP_EVENTS)
	$(PREPROC) $< charmap.txt | $(CPP) -I include - | $(PREPROC) -ie $< charmap.txt | $(AS) $(ASFLAGS) -o $@

$(JOHTO_IMPORT_STAMP): $(JOHTO_IMPORT_SCRIPT) $(JOHTO_IMPORT_COMMON) $(JOHTO_IMPORT_TILESETS) $(JOHTO_IMPORT_MAPS) $(JOHTO_TILESET_ATLAS) $(LAYOUTS_DIR)/layouts.json
	python3 $(JOHTO_IMPORT_SCRIPT)
	@mkdir -p $(dir $@)
	@touch $@

$(JOHTO_IMPORTED_LAYOUT_BINARIES) $(JOHTO_IMPORTED_BORDERS): $(JOHTO_IMPORT_STAMP)

$(MAPS_OUTDIR)/%/header.inc $(MAPS_OUTDIR)/%/events.inc $(MAPS_OUTDIR)/%/connections.inc: $(MAPS_DIR)/%/map.json $(JOHTO_IMPORT_STAMP)
	$(MAPJSON) map emerald $< $(LAYOUTS_DIR)/layouts.json $(@D)

$(MAPS_OUTDIR)/connections.inc $(MAPS_OUTDIR)/groups.inc $(MAPS_OUTDIR)/events.inc $(MAPS_OUTDIR)/headers.inc $(INCLUDECONSTS_OUTDIR)/map_groups.h: $(MAPS_DIR)/map_groups.json
	$(MAPJSON) groups emerald $< $(MAPS_OUTDIR) $(INCLUDECONSTS_OUTDIR)

$(LAYOUTS_OUTDIR)/layouts.inc $(LAYOUTS_OUTDIR)/layouts_table.inc $(INCLUDECONSTS_OUTDIR)/layouts.h: $(LAYOUTS_DIR)/layouts.json
	$(MAPJSON) layouts emerald $< $(LAYOUTS_OUTDIR) $(INCLUDECONSTS_OUTDIR)

# Generate constants for map events, which depend on data that's distributed across the map.json files.
# There's a lot of map.json files, so we print an abbreviated output with echo.
$(INCLUDECONSTS_OUTDIR)/map_event_ids.h: $(MAP_JSONS)
	@$(MAPJSON) event_constants emerald $^ $(INCLUDECONSTS_OUTDIR)/map_event_ids.h
	@echo "$(MAPJSON) event_constants emerald <MAP_JSONS> $(INCLUDECONSTS_OUTDIR)/map_event_ids.h"
