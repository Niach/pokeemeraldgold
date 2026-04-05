NewBarkTown_MapScripts::
	.byte 0

@ VAR_JOHTO_INTRO_STATE
@ 1 = bedroom spawn
@ 2 = spoke to Mom
@ 3 = spoke to Elm
@ 4 = reserved for the next starter/bootstrap checkpoint

NewBarkTown_EventScript_Route29Blocked::
	lockall
	msgbox NewBarkTown_Text_Route29Blocked, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PLAYER, NewBarkTown_Movement_PushPlayerBackFromRoute
	waitmovement 0
	releaseall
	end

NewBarkTown_Movement_PushPlayerBackFromRoute:
	walk_right
	step_end

NewBarkTown_EventScript_Teacher::
	msgbox NewBarkTown_Text_Route29Aide, MSGBOX_NPC
	end

NewBarkTown_EventScript_Fisher::
	msgbox NewBarkTown_Text_Fisher, MSGBOX_NPC
	end

NewBarkTown_EventScript_Rival::
	msgbox NewBarkTown_Text_Rival, MSGBOX_NPC
	end

NewBarkTown_EventScript_TownSign::
	msgbox NewBarkTown_Text_TownSign, MSGBOX_SIGN
	end

NewBarkTown_EventScript_PlayersHouseSign::
	msgbox NewBarkTown_Text_PlayersHouseSign, MSGBOX_SIGN
	end

NewBarkTown_EventScript_ElmsLabSign::
	msgbox NewBarkTown_Text_ElmsLabSign, MSGBOX_SIGN
	end

NewBarkTown_EventScript_ElmsHouseSign::
	msgbox NewBarkTown_Text_ElmsHouseSign, MSGBOX_SIGN
	end

NewBarkTown_Text_Route29Blocked:
	.string "The west road is still closed while\n"
	.string "the town's work crews finish up.$"

NewBarkTown_Text_Route29Aide:
	.string "You can't head for ROUTE 29 just yet.\p"
	.string "PROF. ELM still needs you here in\n"
	.string "NEW BARK TOWN.$"

NewBarkTown_Text_Fisher:
	.string "PROF. ELM says this town feels small,\n"
	.string "but that's what makes beginnings feel\n"
	.string "important.$"

NewBarkTown_Text_Rival:
	.string "...\p"
	.string "What are you staring at?\n"
	.string "I'm busy.$"

NewBarkTown_Text_TownSign:
	.string "NEW BARK TOWN\p"
	.string "The winds of a new beginning.$"

NewBarkTown_Text_PlayersHouseSign:
	.string "{PLAYER}'s HOUSE$"

NewBarkTown_Text_ElmsLabSign:
	.string "ELM POKeMON LAB$"

NewBarkTown_Text_ElmsHouseSign:
	.string "ELM'S HOUSE$"
