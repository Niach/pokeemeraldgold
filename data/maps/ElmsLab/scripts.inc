ElmsLab_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, ElmsLab_OnTransition
	.byte 0

ElmsLab_OnTransition:
	goto_if_set FLAG_JOHTO_GOT_STARTER_FROM_ELM, ElmsLab_EventScript_UpdateOfficerVisibility
	clearflag FLAG_HIDE_ELMS_LAB_CYNDAQUIL_BALL
	clearflag FLAG_HIDE_ELMS_LAB_TOTODILE_BALL
	clearflag FLAG_HIDE_ELMS_LAB_CHIKORITA_BALL
	setflag FLAG_HIDE_ELMS_LAB_OFFICER
	end

ElmsLab_EventScript_UpdateOfficerVisibility:
	goto_if_unset FLAG_JOHTO_GOT_MYSTERY_EGG, ElmsLab_EventScript_HideOfficer
	goto_if_set FLAG_JOHTO_OFFICER_SCENE_COMPLETE, ElmsLab_EventScript_HideOfficer
	clearflag FLAG_HIDE_ELMS_LAB_OFFICER
	end

ElmsLab_EventScript_HideOfficer:
	setflag FLAG_HIDE_ELMS_LAB_OFFICER
	end

ElmsLab_EventScript_Elm::
	lock
	faceplayer
	goto_if_lt VAR_JOHTO_INTRO_STATE, 2, ElmsLab_EventScript_ElmNeedMomFirst
	goto_if_unset FLAG_JOHTO_GOT_STARTER_FROM_ELM, ElmsLab_EventScript_ElmBeforeStarter
	goto_if_ge VAR_JOHTO_INTRO_STATE, 7, ElmsLab_EventScript_ElmAfterEggReturn
	goto_if_ge VAR_JOHTO_INTRO_STATE, 6, ElmsLab_EventScript_ElmReceiveEgg
	goto_if_set FLAG_JOHTO_GOT_MYSTERY_EGG, ElmsLab_EventScript_ElmWaitForOfficer
	msgbox ElmsLab_Text_ElmAfterStarter, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_ElmBeforeStarter:
	goto_if_set FLAG_JOHTO_ELM_INTRO_COMPLETE, ElmsLab_EventScript_ElmChooseStarterPrompt
	msgbox ElmsLab_Text_ElmFirstTalk, MSGBOX_DEFAULT
	setflag FLAG_JOHTO_ELM_INTRO_COMPLETE
	setvar VAR_JOHTO_INTRO_STATE, 3
	release
	end

ElmsLab_EventScript_ElmNeedMomFirst::
	msgbox ElmsLab_Text_ElmNeedMomFirst, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_ElmChooseStarterPrompt::
	msgbox ElmsLab_Text_ElmChooseStarterPrompt, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_ElmWaitForOfficer:
	msgbox ElmsLab_Text_ElmWaitForOfficer, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_ElmReceiveEgg:
	msgbox ElmsLab_Text_ElmReceiveEgg, MSGBOX_DEFAULT
	setflag FLAG_JOHTO_ROUTE29_TUTORIAL_UNLOCKED
	setvar VAR_JOHTO_ROUTE29_SCENE_STATE, 1
	setvar VAR_JOHTO_INTRO_STATE, 7
	release
	end

ElmsLab_EventScript_ElmAfterEggReturn:
	msgbox ElmsLab_Text_ElmAfterEggReturn, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_Aide::
	lock
	faceplayer
	goto_if_ge VAR_JOHTO_INTRO_STATE, 7, ElmsLab_EventScript_AideAfterOak
	goto_if_set FLAG_JOHTO_GOT_MYSTERY_EGG, ElmsLab_EventScript_AideTheftTestimony
	goto_if_set FLAG_JOHTO_GOT_STARTER_FROM_ELM, ElmsLab_EventScript_AideAfterStarter
	goto_if_set FLAG_JOHTO_ELM_INTRO_COMPLETE, ElmsLab_EventScript_AideChooseStarter
	msgbox ElmsLab_Text_AideBeforeIntro, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_AideChooseStarter::
	msgbox ElmsLab_Text_AideChooseStarter, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_AideAfterStarter::
	msgbox ElmsLab_Text_AideAfterStarter, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_AideAfterOak::
	msgbox ElmsLab_Text_AideAfterOak, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_AideTheftTestimony:
	msgbox ElmsLab_Text_AideTheftTestimony, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_OfficerSceneWest::
	lockall
	applymovement LOCALID_PLAYER, ElmsLab_Movement_MeetOfficerFromWest
	waitmovement 0
	goto ElmsLab_EventScript_OfficerReport

ElmsLab_EventScript_OfficerSceneEast::
	lockall
	applymovement LOCALID_PLAYER, ElmsLab_Movement_MeetOfficerFromEast
	waitmovement 0
	goto ElmsLab_EventScript_OfficerReport

ElmsLab_EventScript_Officer::
	lockall
	goto_if_set FLAG_JOHTO_OFFICER_SCENE_COMPLETE, ElmsLab_EventScript_OfficerAfterReport
	goto ElmsLab_EventScript_OfficerReport

ElmsLab_EventScript_OfficerReport:
	turnobject LOCALID_ELMS_LAB_OFFICER, DIR_WEST
	msgbox ElmsLab_Text_OfficerAskName, MSGBOX_DEFAULT
	special DoJohtoRivalNamingScreen
	special BufferJohtoRivalName
	msgbox ElmsLab_Text_OfficerGotName, MSGBOX_DEFAULT
	setflag FLAG_JOHTO_RIVAL_THEFT_REPORTED
	setflag FLAG_JOHTO_OFFICER_SCENE_COMPLETE
	setvar VAR_JOHTO_INTRO_STATE, 6
	applymovement LOCALID_ELMS_LAB_OFFICER, ElmsLab_Movement_OfficerExit
	waitmovement 0
	setflag FLAG_HIDE_ELMS_LAB_OFFICER
	removeobject LOCALID_ELMS_LAB_OFFICER
	releaseall
	end

ElmsLab_EventScript_OfficerAfterReport::
	msgbox ElmsLab_Text_OfficerAfterReport, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_CyndaquilBall::
	lock
	goto_if_unset FLAG_JOHTO_ELM_INTRO_COMPLETE, ElmsLab_EventScript_SeeElmFirst
	goto_if_set FLAG_JOHTO_GOT_STARTER_FROM_ELM, ElmsLab_EventScript_StarterAlreadyChosen
	showmonpic SPECIES_CYNDAQUIL, 10, 3
	msgbox ElmsLab_Text_CyndaquilBall, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ElmsLab_EventScript_TakeYourTime
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_CYNDAQUIL
	givemon SPECIES_CYNDAQUIL, 5
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PARTY, ElmsLab_EventScript_ReceivedCyndaquil
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, ElmsLab_EventScript_CyndaquilTransferredToPC
	hidemonpic
	goto Common_EventScript_NoMoreRoomForPokemon

ElmsLab_EventScript_CyndaquilTransferredToPC::
	hidemonpic
	call Common_EventScript_TransferredToPC
	goto ElmsLab_EventScript_ReceivedCyndaquil

ElmsLab_EventScript_ReceivedCyndaquil::
	hidemonpic
	setvar VAR_JOHTO_STARTER_SPECIES, SPECIES_CYNDAQUIL
	setvar VAR_JOHTO_INTRO_STATE, 4
	setflag FLAG_JOHTO_GOT_STARTER_FROM_ELM
	setflag FLAG_HIDE_ELMS_LAB_CYNDAQUIL_BALL
	removeobject LOCALID_ELMS_LAB_CYNDAQUIL_BALL
	msgbox ElmsLab_Text_ReceivedCyndaquil, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_TotodileBall::
	lock
	goto_if_unset FLAG_JOHTO_ELM_INTRO_COMPLETE, ElmsLab_EventScript_SeeElmFirst
	goto_if_set FLAG_JOHTO_GOT_STARTER_FROM_ELM, ElmsLab_EventScript_StarterAlreadyChosen
	showmonpic SPECIES_TOTODILE, 10, 3
	msgbox ElmsLab_Text_TotodileBall, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ElmsLab_EventScript_TakeYourTime
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_TOTODILE
	givemon SPECIES_TOTODILE, 5
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PARTY, ElmsLab_EventScript_ReceivedTotodile
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, ElmsLab_EventScript_TotodileTransferredToPC
	hidemonpic
	goto Common_EventScript_NoMoreRoomForPokemon

ElmsLab_EventScript_TotodileTransferredToPC::
	hidemonpic
	call Common_EventScript_TransferredToPC
	goto ElmsLab_EventScript_ReceivedTotodile

ElmsLab_EventScript_ReceivedTotodile::
	hidemonpic
	setvar VAR_JOHTO_STARTER_SPECIES, SPECIES_TOTODILE
	setvar VAR_JOHTO_INTRO_STATE, 4
	setflag FLAG_JOHTO_GOT_STARTER_FROM_ELM
	setflag FLAG_HIDE_ELMS_LAB_TOTODILE_BALL
	removeobject LOCALID_ELMS_LAB_TOTODILE_BALL
	msgbox ElmsLab_Text_ReceivedTotodile, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_ChikoritaBall::
	lock
	goto_if_unset FLAG_JOHTO_ELM_INTRO_COMPLETE, ElmsLab_EventScript_SeeElmFirst
	goto_if_set FLAG_JOHTO_GOT_STARTER_FROM_ELM, ElmsLab_EventScript_StarterAlreadyChosen
	showmonpic SPECIES_CHIKORITA, 10, 3
	msgbox ElmsLab_Text_ChikoritaBall, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, ElmsLab_EventScript_TakeYourTime
	setvar VAR_TEMP_TRANSFERRED_SPECIES, SPECIES_CHIKORITA
	givemon SPECIES_CHIKORITA, 5
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PARTY, ElmsLab_EventScript_ReceivedChikorita
	goto_if_eq VAR_RESULT, MON_GIVEN_TO_PC, ElmsLab_EventScript_ChikoritaTransferredToPC
	hidemonpic
	goto Common_EventScript_NoMoreRoomForPokemon

ElmsLab_EventScript_ChikoritaTransferredToPC::
	hidemonpic
	call Common_EventScript_TransferredToPC
	goto ElmsLab_EventScript_ReceivedChikorita

ElmsLab_EventScript_ReceivedChikorita::
	hidemonpic
	setvar VAR_JOHTO_STARTER_SPECIES, SPECIES_CHIKORITA
	setvar VAR_JOHTO_INTRO_STATE, 4
	setflag FLAG_JOHTO_GOT_STARTER_FROM_ELM
	setflag FLAG_HIDE_ELMS_LAB_CHIKORITA_BALL
	removeobject LOCALID_ELMS_LAB_CHIKORITA_BALL
	msgbox ElmsLab_Text_ReceivedChikorita, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_SeeElmFirst::
	msgbox ElmsLab_Text_SeeElmFirst, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_StarterAlreadyChosen::
	msgbox ElmsLab_Text_StarterAlreadyChosen, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_TakeYourTime::
	hidemonpic
	msgbox ElmsLab_Text_TakeYourTime, MSGBOX_DEFAULT
	release
	end

ElmsLab_EventScript_PC::
	msgbox ElmsLab_Text_PC, MSGBOX_SIGN
	end

ElmsLab_EventScript_Bookshelf::
	msgbox ElmsLab_Text_Bookshelf, MSGBOX_SIGN
	end

ElmsLab_EventScript_Machine::
	msgbox ElmsLab_Text_Machine, MSGBOX_SIGN
	end

ElmsLab_EventScript_TravelTip1::
	msgbox ElmsLab_Text_TravelTip1, MSGBOX_SIGN
	end

ElmsLab_EventScript_TravelTip2::
	msgbox ElmsLab_Text_TravelTip2, MSGBOX_SIGN
	end

ElmsLab_EventScript_TravelTip3::
	msgbox ElmsLab_Text_TravelTip3, MSGBOX_SIGN
	end

ElmsLab_EventScript_TravelTip4::
	msgbox ElmsLab_Text_TravelTip4, MSGBOX_SIGN
	end

ElmsLab_EventScript_Trashcan::
	msgbox ElmsLab_Text_Trashcan, MSGBOX_SIGN
	end

ElmsLab_EventScript_Window::
	msgbox ElmsLab_Text_Window, MSGBOX_SIGN
	end

ElmsLab_Movement_MeetOfficerFromWest:
	walk_up
	walk_up
	face_right
	step_end

ElmsLab_Movement_MeetOfficerFromEast:
	walk_left
	walk_up
	walk_up
	face_right
	step_end

ElmsLab_Movement_OfficerExit:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

ElmsLab_Text_ElmNeedMomFirst:
	.string "Before we begin, check in with your\n"
	.string "MOM at home.\p"
	.string "She said she was holding your travel\n"
	.string "gear for you.$"

ElmsLab_Text_ElmFirstTalk:
	.string "Hello, {PLAYER}!\p"
	.string "I need somebody I can trust for a\n"
	.string "special errand.\p"
	.string "Choose one of the three POKeMON on\n"
	.string "the table, then visit MR. POKeMON\n"
	.string "north of CHERRYGROVE.$"

ElmsLab_Text_ElmChooseStarterPrompt:
	.string "Take your time.\p"
	.string "You'll want the partner that feels\n"
	.string "right for a long Johto journey.$"

ElmsLab_Text_ElmWaitForOfficer:
	.string "A police officer is investigating the\n"
	.string "theft right now.\p"
	.string "Tell him what happened up north before\n"
	.string "we talk about the MYSTERY EGG.$"

ElmsLab_Text_ElmAfterStarter:
	.string "How is your errand going?\p"
	.string "MR. POKeMON lives north of\n"
	.string "CHERRYGROVE CITY, just past ROUTE 30.$"

ElmsLab_Text_ElmReceiveEgg:
	.string "That EGG came from MR. POKeMON?\p"
	.string "This is incredible...\p"
	.string "Officer, the red-haired boy who stole\n"
	.string "a POKeMON from this lab must be your\n"
	.string "culprit.\p"
	.string "Take your partner out and keep going.\n"
	.string "ROUTE 29 is a good place to sharpen\n"
	.string "your trainer skills.$"

ElmsLab_Text_ElmAfterEggReturn:
	.string "Thanks again, {PLAYER}.\p"
	.string "Keep raising your POKeMON and record\n"
	.string "what you find in the POKEDEX.$"

ElmsLab_Text_AideBeforeIntro:
	.string "PROF. ELM has been waiting for you.\p"
	.string "He has been preparing all morning for\n"
	.string "this errand of yours.$"

ElmsLab_Text_AideChooseStarter:
	.string "Go on, choose one.\p"
	.string "PROF. ELM only asks for help when it\n"
	.string "really matters.$"

ElmsLab_Text_AideAfterStarter:
	.string "MR. POKeMON is eager to see whatever\n"
	.string "PROF. ELM asked you to fetch.$"

ElmsLab_Text_AideAfterOak:
	.string "PROF. OAK gave you a POKEDEX?\p"
	.string "That makes this errand even more\n"
	.string "important to PROF. ELM.$"

ElmsLab_Text_AideTheftTestimony:
	.string "There was a loud noise outside...\p"
	.string "When we went to look, someone stole a\n"
	.string "POKeMON.\p"
	.string "It's unbelievable that anyone would do\n"
	.string "that!$"

ElmsLab_Text_OfficerAskName:
	.string "I heard a POKeMON was stolen here...\p"
	.string "I was just getting some information\n"
	.string "from PROF. ELM.\p"
	.string "Apparently, it was a young male with\n"
	.string "long, red hair...\p"
	.string "What?\p"
	.string "You battled a trainer like that?\p"
	.string "Did you happen to get his name?$"

ElmsLab_Text_OfficerGotName:
	.string "OK! So {STR_VAR_1} was his name.\p"
	.string "Thanks for helping my investigation!$"

ElmsLab_Text_OfficerAfterReport:
	.string "We'll keep searching for the thief.\p"
	.string "If you see that red-haired boy again,\n"
	.string "stay on your guard.$"

ElmsLab_Text_CyndaquilBall:
	.string "CYNDAQUIL is peering out eagerly.\p"
	.string "Take CYNDAQUIL?$"

ElmsLab_Text_TotodileBall:
	.string "TOTODILE snaps the air with a grin.\p"
	.string "Take TOTODILE?$"

ElmsLab_Text_ChikoritaBall:
	.string "CHIKORITA watches you calmly.\p"
	.string "Take CHIKORITA?$"

ElmsLab_Text_ReceivedCyndaquil:
	.string "CYNDAQUIL joined your team.\p"
	.string "PROF. ELM asks you to head north and\n"
	.string "visit MR. POKeMON.$"

ElmsLab_Text_ReceivedTotodile:
	.string "TOTODILE joined your team.\p"
	.string "PROF. ELM asks you to head north and\n"
	.string "visit MR. POKeMON.$"

ElmsLab_Text_ReceivedChikorita:
	.string "CHIKORITA joined your team.\p"
	.string "PROF. ELM asks you to head north and\n"
	.string "visit MR. POKeMON.$"

ElmsLab_Text_SeeElmFirst:
	.string "You should talk to PROF. ELM before\n"
	.string "touching the starter table.$"

ElmsLab_Text_StarterAlreadyChosen:
	.string "The remaining POKe BALLs are part of\n"
	.string "ELM's display now.\p"
	.string "Your partner has already been chosen.$"

ElmsLab_Text_TakeYourTime:
	.string "No rush.\p"
	.string "PROF. ELM wants the opening choice to\n"
	.string "feel deliberate.$"

ElmsLab_Text_PC:
	.string "Research data is being organized into\n"
	.string "a brand-new system.$"

ElmsLab_Text_Bookshelf:
	.string "The shelves are packed with books on\n"
	.string "POKeMON habitats and evolution.$"

ElmsLab_Text_Machine:
	.string "The machine is humming softly.\p"
	.string "It looks like it's still calibrating.$"

ElmsLab_Text_TravelTip1:
	.string "TRAVEL TIP 1\p"
	.string "Record your trip often while the\n"
	.string "Johto story systems come online.$"

ElmsLab_Text_TravelTip2:
	.string "TRAVEL TIP 2\p"
	.string "Facing, movement, and callbacks matter\n"
	.string "just as much as dialogue text.$"

ElmsLab_Text_TravelTip3:
	.string "TRAVEL TIP 3\p"
	.string "A clean starter handoff makes the rest\n"
	.string "of the port easier to trust.$"

ElmsLab_Text_TravelTip4:
	.string "TRAVEL TIP 4\p"
	.string "Crystal-only systems can use Emerald\n"
	.string "substitutes when parity is heavy.$"

ElmsLab_Text_Trashcan:
	.string "It's filled with failed printouts and\n"
	.string "discarded research notes.$"

ElmsLab_Text_Window:
	.string "You can see NEW BARK TOWN stretching\n"
	.string "out beyond the lab.$"
