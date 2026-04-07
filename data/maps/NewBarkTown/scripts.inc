NewBarkTown_MapScripts::
	.byte 0

@ VAR_JOHTO_INTRO_STATE
@ 1 = bedroom spawn
@ 2 = spoke to Mom
@ 3 = spoke to Elm
@ 4 = reserved for the next starter/bootstrap checkpoint

NewBarkTown_EventScript_TeacherStopsYouNorth::
	lockall
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherRunsToYouNorth
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_EAST
	msgbox NewBarkTown_Text_TeacherStopsYou, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PLAYER, NewBarkTown_Movement_PushPlayerBackFromRoute
	waitmovement 0
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherReturnsNorth
	waitmovement 0
	turnobject LOCALID_NEW_BARK_TOWN_TEACHER, DIR_WEST
	releaseall
	end

NewBarkTown_EventScript_TeacherStopsYouSouth::
	lockall
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherRunsToYouSouth
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_NORTH
	msgbox NewBarkTown_Text_TeacherStopsYou, MSGBOX_DEFAULT
	closemessage
	applymovement LOCALID_PLAYER, NewBarkTown_Movement_PushPlayerBackFromRoute
	waitmovement 0
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherReturnsSouth
	waitmovement 0
	turnobject LOCALID_NEW_BARK_TOWN_TEACHER, DIR_WEST
	releaseall
	end

NewBarkTown_Movement_TeacherRunsToYouNorth:
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

NewBarkTown_Movement_TeacherRunsToYouSouth:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

NewBarkTown_Movement_PushPlayerBackFromRoute:
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

NewBarkTown_Movement_TeacherReturnsNorth:
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

NewBarkTown_Movement_TeacherReturnsSouth:
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

NewBarkTown_EventScript_Teacher::
	goto_if_lt VAR_JOHTO_INTRO_STATE, 3, NewBarkTown_EventScript_TeacherBeforeElm
	msgbox NewBarkTown_Text_Route29AideAfterElm, MSGBOX_NPC
	end

NewBarkTown_EventScript_TeacherBeforeElm::
	msgbox NewBarkTown_Text_Route29AideBeforeElm, MSGBOX_NPC
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

NewBarkTown_Text_TeacherStopsYou:
	.string "Wait, {PLAYER}!\p"
	.string "ROUTE 29 isn't ready yet.\n"
	.string "PROF. ELM asked everyone to stay\n"
	.string "close to town for now.$"

NewBarkTown_Text_Route29AideBeforeElm:
	.string "PROF. ELM still needs you at the lab.\p"
	.string "You should check in with him before\n"
	.string "you even think about ROUTE 29.$"

NewBarkTown_Text_Route29AideAfterElm:
	.string "NEW BARK is quiet today, isn't it?\p"
	.string "Once the west road is finished, it\n"
	.string "will feel like a real beginning.$"

NewBarkTown_Text_Fisher:
	.string "PROF. ELM says the best journeys start\n"
	.string "in small places like this.$"

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
