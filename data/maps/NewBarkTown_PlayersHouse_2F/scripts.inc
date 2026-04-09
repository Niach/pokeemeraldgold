NewBarkTown_PlayersHouse_2F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, NewBarkTown_PlayersHouse_2F_OnTransition
	.byte 0

NewBarkTown_PlayersHouse_2F_OnTransition:
	special SyncJohtoPlayersHouse2FDecorations
	end

NewBarkTown_PlayersHouse_2F_EventScript_PC::
	lockall
	setvar VAR_0x8004, PC_LOCATION_BRENDANS_HOUSE
	special DoPCTurnOnEffect
	playse SE_PC_ON
	msgbox gText_PlayerHouseBootPC, MSGBOX_DEFAULT
	special BedroomPC
	waitstate
	releaseall
	end

NewBarkTown_PlayersHouse_2F_EventScript_Radio::
	goto_if_set FLAG_JOHTO_GOT_STARTER_FROM_ELM, NewBarkTown_PlayersHouse_2F_EventScript_RadioRepeat
	goto_if_set FLAG_JOHTO_PLAYERS_HOUSE_RADIO_HEARD, NewBarkTown_PlayersHouse_2F_EventScript_RadioRepeat
	msgbox Crystal_NewBarkTown_PlayersHouse_2F_PlayersRadioText1, MSGBOX_SIGN
	msgbox Crystal_NewBarkTown_PlayersHouse_2F_PlayersRadioText2, MSGBOX_SIGN
	msgbox Crystal_NewBarkTown_PlayersHouse_2F_PlayersRadioText3, MSGBOX_SIGN
	msgbox Crystal_NewBarkTown_PlayersHouse_2F_PlayersRadioText4, MSGBOX_SIGN
	setflag FLAG_JOHTO_PLAYERS_HOUSE_RADIO_HEARD
	end

NewBarkTown_PlayersHouse_2F_EventScript_RadioRepeat::
	msgbox Crystal_NewBarkTown_PlayersHouse_2F_PlayersRadioText4, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_EventScript_GameConsole::
	msgbox NewBarkTown_PlayersHouse_2F_Text_GameConsole, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_EventScript_Bookshelf::
	msgbox NewBarkTown_PlayersHouse_2F_Text_Bookshelf, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_2F_EventScript_Poster::
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

NewBarkTown_PlayersHouse_2F_Text_RadioIntro1:
	.string "PROF.OAK'S POKéMON TALK!\n"
	.string "Please tune in next time!$"

NewBarkTown_PlayersHouse_2F_Text_RadioIntro2:
	.string "POKéMON CHANNEL!$"

NewBarkTown_PlayersHouse_2F_Text_RadioIntro3:
	.string "This is DJ MARY, your co-host!$"

NewBarkTown_PlayersHouse_2F_Text_RadioIntro4:
	.string "POKéMON!\n"
	.string "POKéMON CHANNEL...$"

NewBarkTown_PlayersHouse_2F_Text_GameConsole:
	.string "A game console is connected.\p"
	.string "It looks well loved.$"

NewBarkTown_PlayersHouse_2F_Text_Bookshelf:
	.string "A whole collection of POKéMON picture\n"
	.string "books!$"

NewBarkTown_PlayersHouse_2F_Text_Doll1:
	.string "A CYNDAQUIL doll.$"

NewBarkTown_PlayersHouse_2F_Text_Doll2:
	.string "A TOTODILE doll.$"

NewBarkTown_PlayersHouse_2F_Text_BigDoll:
	.string "A huge SNORLAX doll.$"
