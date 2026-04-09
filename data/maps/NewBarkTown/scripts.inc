NewBarkTown_MapScripts::
	.byte 0

@ VAR_JOHTO_INTRO_STATE
@ 1 = bedroom spawn
@ 2 = Mom handed over the POKENAV substitute
@ 3 = Elm intro complete, starter choice unlocked
@ 4 = received starter
@ 5 = met Mr. Pokemon and Oak
@ 6 = officer report complete, rival named
@ 7 = returned the Mystery Egg to Elm

NewBarkTown_EventScript_TeacherStopsYouNorth::
	lockall
	playbgm MUS_ENCOUNTER_GIRL, FALSE
	turnobject LOCALID_NEW_BARK_TOWN_TEACHER, DIR_WEST
	msgbox Crystal_NewBarkTown_Text_WaitPlayer, MSGBOX_DEFAULT
	turnobject LOCALID_PLAYER, DIR_EAST
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherRunsToYouNorth
	waitmovement 0
	msgbox Crystal_NewBarkTown_Text_WhatDoYouThinkYoureDoing, MSGBOX_DEFAULT
	follow LOCALID_NEW_BARK_TOWN_TEACHER, LOCALID_PLAYER
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherReturnsNorth
	waitmovement 0
	stopfollow
	turnobject LOCALID_NEW_BARK_TOWN_TEACHER, DIR_WEST
	msgbox Crystal_NewBarkTown_Text_ItsDangerousToGoAlone, MSGBOX_DEFAULT
	fadedefaultbgm
	releaseall
	end

NewBarkTown_EventScript_TeacherStopsYouSouth::
	lockall
	playbgm MUS_ENCOUNTER_GIRL, FALSE
	turnobject LOCALID_NEW_BARK_TOWN_TEACHER, DIR_WEST
	msgbox Crystal_NewBarkTown_Text_WaitPlayer, MSGBOX_DEFAULT
	turnobject LOCALID_PLAYER, DIR_EAST
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherRunsToYouSouth
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_NORTH
	msgbox Crystal_NewBarkTown_Text_WhatDoYouThinkYoureDoing, MSGBOX_DEFAULT
	follow LOCALID_NEW_BARK_TOWN_TEACHER, LOCALID_PLAYER
	applymovement LOCALID_NEW_BARK_TOWN_TEACHER, NewBarkTown_Movement_TeacherReturnsSouth
	waitmovement 0
	stopfollow
	turnobject LOCALID_NEW_BARK_TOWN_TEACHER, DIR_WEST
	msgbox Crystal_NewBarkTown_Text_ItsDangerousToGoAlone, MSGBOX_DEFAULT
	fadedefaultbgm
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
	face_down
	step_end

NewBarkTown_Movement_TeacherReturnsNorth:
	walk_right
	walk_right
	walk_right
	walk_right
	face_left
	step_end

NewBarkTown_Movement_TeacherReturnsSouth:
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	face_left
	step_end

NewBarkTown_Movement_RivalPushesYouAway:
	face_up
	walk_down
	step_end

NewBarkTown_Movement_RivalReturnsToTheShadows:
	walk_right
	step_end

NewBarkTown_EventScript_Teacher::
	lock
	faceplayer
	goto_if_ge VAR_JOHTO_INTRO_STATE, 7, NewBarkTown_EventScript_TeacherCallMom
	goto_if_set FLAG_JOHTO_GOT_MYSTERY_EGG, NewBarkTown_EventScript_TeacherTellMomIfLeaving
	goto_if_set FLAG_JOHTO_GOT_STARTER_FROM_ELM, NewBarkTown_EventScript_TeacherMonIsAdorable
	msgbox Crystal_NewBarkTown_Text_GearIsImpressive, MSGBOX_DEFAULT
	release
	end

NewBarkTown_EventScript_TeacherMonIsAdorable:
	msgbox Crystal_NewBarkTown_Text_YourMonIsAdorable, MSGBOX_DEFAULT
	release
	end

NewBarkTown_EventScript_TeacherTellMomIfLeaving:
	msgbox Crystal_NewBarkTown_Text_TellMomIfLeaving, MSGBOX_DEFAULT
	release
	end

NewBarkTown_EventScript_TeacherCallMom:
	msgbox Crystal_NewBarkTown_Text_CallMomOnGear, MSGBOX_DEFAULT
	release
	end

NewBarkTown_EventScript_Fisher::
	lock
	faceplayer
	msgbox Crystal_NewBarkTown_Text_ElmDiscoveredNewMon, MSGBOX_DEFAULT
	release
	end

NewBarkTown_EventScript_Rival::
	lockall
	msgbox Crystal_NewBarkTown_NewBarkTownRivalText1, MSGBOX_DEFAULT
	turnobject LOCALID_NEW_BARK_TOWN_RIVAL, DIR_WEST
	msgbox Crystal_NewBarkTown_NewBarkTownRivalText2, MSGBOX_DEFAULT
	follow LOCALID_PLAYER, LOCALID_NEW_BARK_TOWN_RIVAL
	applymovement LOCALID_PLAYER, Crystal_NewBarkTown_NewBarkTown_RivalPushesYouAwayMovement
	waitmovement 0
	stopfollow
	delay 5
	turnobject LOCALID_NEW_BARK_TOWN_RIVAL, DIR_SOUTH
	delay 5
	playse SE_BANG
	applymovement LOCALID_PLAYER, Crystal_NewBarkTown_NewBarkTown_RivalShovesYouOutMovement
	waitmovement 0
	waitse
	applymovement LOCALID_NEW_BARK_TOWN_RIVAL, Crystal_NewBarkTown_NewBarkTown_RivalReturnsToTheShadowsMovement
	waitmovement 0
	releaseall
	end

NewBarkTown_EventScript_TownSign::
	msgbox Crystal_NewBarkTown_NewBarkTownSignText, MSGBOX_SIGN
	end

NewBarkTown_EventScript_PlayersHouseSign::
	msgbox Crystal_NewBarkTown_NewBarkTownPlayersHouseSignText, MSGBOX_SIGN
	end

NewBarkTown_EventScript_ElmsLabSign::
	msgbox Crystal_NewBarkTown_NewBarkTownElmsLabSignText, MSGBOX_SIGN
	end

NewBarkTown_EventScript_ElmsHouseSign::
	msgbox Crystal_NewBarkTown_NewBarkTownElmsHouseSignText, MSGBOX_SIGN
	end

NewBarkTown_Text_WaitPlayer:
	.string "Wait, {PLAYER}!$"

NewBarkTown_Text_WhatDoYouThinkYoureDoing:
	.string "What do you think you're doing?$"

NewBarkTown_Text_ItsDangerousToGoAlone:
	.string "It's dangerous to go out without a\n"
	.string "POKéMON!\p"
	.string "Wild POKéMON jump out of the grass on\n"
	.string "the way to the next town.$"

NewBarkTown_Text_GearIsImpressive:
	.string "Wow, your POKENAV is impressive!\p"
	.string "Did your mom get it for you?$"

NewBarkTown_Text_YourMonIsAdorable:
	.string "Oh! Your POKéMON is adorable!\p"
	.string "I wish I had one!$"

NewBarkTown_Text_TellMomIfLeaving:
	.string "Hi, {PLAYER}!\p"
	.string "Leaving again?\p"
	.string "You should tell your mom if you are\n"
	.string "leaving.$"

NewBarkTown_Text_ElmDiscoveredNewMon:
	.string "Yo, {PLAYER}!\p"
	.string "I hear PROF. ELM discovered some new\n"
	.string "POKéMON.$"

NewBarkTown_Text_RivalIntro:
	.string "<...>\p"
	.string "So this is the famous ELM POKéMON\n"
	.string "LAB...$"

NewBarkTown_Text_RivalStaring:
	.string "...What are you staring at?$"

NewBarkTown_Text_TownSign:
	.string "NEW BARK TOWN\p"
	.string "The Town Where the Winds of a New\n"
	.string "Beginning Blow$"

NewBarkTown_Text_PlayersHouseSign:
	.string "{PLAYER}'s HOUSE$"

NewBarkTown_Text_ElmsLabSign:
	.string "ELM POKéMON LAB$"

NewBarkTown_Text_ElmsHouseSign:
	.string "ELM'S HOUSE$"
