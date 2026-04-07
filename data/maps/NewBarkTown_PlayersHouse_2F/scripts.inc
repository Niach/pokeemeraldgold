NewBarkTown_PlayersHouse_2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, NewBarkTown_PlayersHouse_2F_OnTransition
	.byte 0

NewBarkTown_PlayersHouse_2F_OnTransition:
	setflag FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_CONSOLE
	setflag FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_DOLL_1
	setflag FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_DOLL_2
	setflag FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_BIG_DOLL
	end

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

NewBarkTown_PlayersHouse_2F_EventScript_Doll1::
	msgbox NewBarkTown_PlayersHouse_2F_Text_Doll1, MSGBOX_NPC
	end

NewBarkTown_PlayersHouse_2F_EventScript_Doll2::
	msgbox NewBarkTown_PlayersHouse_2F_Text_Doll2, MSGBOX_NPC
	end

NewBarkTown_PlayersHouse_2F_EventScript_BigDoll::
	msgbox NewBarkTown_PlayersHouse_2F_Text_BigDoll, MSGBOX_NPC
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

NewBarkTown_PlayersHouse_2F_Text_Doll1:
	.string "A CYNDAQUIL doll.\p"
	.string "Someone set it beside the bed with\n"
	.string "extra care.$"

NewBarkTown_PlayersHouse_2F_Text_Doll2:
	.string "A TOTODILE doll splays its arms wide.\p"
	.string "It looks ready to leap into battle.$"

NewBarkTown_PlayersHouse_2F_Text_BigDoll:
	.string "A huge SNORLAX doll takes up almost\n"
	.string "the whole corner.$"
