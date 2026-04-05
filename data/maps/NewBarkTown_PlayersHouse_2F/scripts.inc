NewBarkTown_PlayersHouse_2F_MapScripts::
	.byte 0

NewBarkTown_PlayersHouse_2F_EventScript_PC::
	msgbox NewBarkTown_PlayersHouse_2F_Text_PC, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_EventScript_Radio::
	msgbox NewBarkTown_PlayersHouse_2F_Text_Radio, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_EventScript_GameConsole::
	msgbox NewBarkTown_PlayersHouse_2F_Text_GameConsole, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_EventScript_Bookshelf::
	msgbox NewBarkTown_PlayersHouse_2F_Text_Bookshelf, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_EventScript_Poster::
	msgbox NewBarkTown_PlayersHouse_2F_Text_Poster, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_Text_PC:
	.string "The PC is freshly set up.\p"
	.string "A note says: ELM can help once the\n"
	.string "rest of the equipment arrives.$"

NewBarkTown_PlayersHouse_2F_Text_Radio:
	.string "The radio is on.\p"
	.string "A cheerful host is talking about\n"
	.string "POKeMON discoveries across JOHTO.$"

NewBarkTown_PlayersHouse_2F_Text_GameConsole:
	.string "A game console is connected.\p"
	.string "It looks well loved.$"

NewBarkTown_PlayersHouse_2F_Text_Bookshelf:
	.string "Picture books and travel guides are\n"
	.string "lined up in perfect order.$"

NewBarkTown_PlayersHouse_2F_Text_Poster:
	.string "It's a poster of a POKeMON trainer\n"
	.string "setting out on a journey.$"
