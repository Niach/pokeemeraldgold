NewBarkTown_PlayersHouse_1F_MapScripts::
	.byte 0

NewBarkTown_PlayersHouse_1F_EventScript_Mom::
	lock
	faceplayer
	goto_if_lt VAR_JOHTO_INTRO_STATE, 2, NewBarkTown_PlayersHouse_1F_EventScript_MomFirstTalkFromObject
	goto_if_lt VAR_JOHTO_INTRO_STATE, 3, NewBarkTown_PlayersHouse_1F_EventScript_MomBeforeElm
	msgbox Crystal_NewBarkTown_PlayersHouse_1F_SoWhatWasProfElmsErrandText, MSGBOX_DEFAULT
	release
	end

NewBarkTown_PlayersHouse_1F_EventScript_MomBeforeElm::
	msgbox Crystal_NewBarkTown_PlayersHouse_1F_HurryUpElmIsWaitingText, MSGBOX_DEFAULT
	release
	end

NewBarkTown_PlayersHouse_1F_EventScript_MomFirstTalkFromObject::
	call NewBarkTown_PlayersHouse_1F_EventScript_MomReceivePokenav
	applymovement LOCALID_NEW_BARK_TOWN_PLAYERS_HOUSE_1F_MOM, Common_Movement_FaceLeft
	waitmovement 0
	release
	end

NewBarkTown_PlayersHouse_1F_EventScript_MomFirstTalkNear::
	lockall
	applymovement LOCALID_NEW_BARK_TOWN_PLAYERS_HOUSE_1F_MOM, Common_Movement_FaceRight
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_WEST
	call NewBarkTown_PlayersHouse_1F_EventScript_MomReceivePokenav
	applymovement LOCALID_NEW_BARK_TOWN_PLAYERS_HOUSE_1F_MOM, Common_Movement_FaceLeft
	waitmovement 0
	releaseall
	end

NewBarkTown_PlayersHouse_1F_EventScript_MomFirstTalkFar::
	lockall
	applymovement LOCALID_NEW_BARK_TOWN_PLAYERS_HOUSE_1F_MOM, NewBarkTown_PlayersHouse_1F_Movement_MomStepRight
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_WEST
	call NewBarkTown_PlayersHouse_1F_EventScript_MomReceivePokenav
	applymovement LOCALID_NEW_BARK_TOWN_PLAYERS_HOUSE_1F_MOM, NewBarkTown_PlayersHouse_1F_Movement_MomStepLeft
	waitmovement 0
	applymovement LOCALID_NEW_BARK_TOWN_PLAYERS_HOUSE_1F_MOM, Common_Movement_FaceLeft
	waitmovement 0
	releaseall
	end

NewBarkTown_PlayersHouse_1F_EventScript_MomReceivePokenav::
	msgbox Crystal_NewBarkTown_PlayersHouse_1F_ElmsLookingForYouText, MSGBOX_DEFAULT
	closemessage
	goto_if_set FLAG_RECEIVED_POKENAV, NewBarkTown_PlayersHouse_1F_EventScript_MomReceivePokenavFinish
	playfanfare MUS_OBTAIN_ITEM
	msgbox NewBarkTown_PlayersHouse_1F_Text_MomGavePokenav, MSGBOX_DEFAULT
	waitfanfare
	closemessage
	setflag FLAG_RECEIVED_POKENAV
	setflag FLAG_SYS_POKENAV_GET
	setflag FLAG_HAS_MATCH_CALL
	setflag FLAG_JOHTO_MOM_GAVE_POKENAV
	playfanfare MUS_REGISTER_MATCH_CALL
	msgbox NewBarkTown_PlayersHouse_1F_Text_MomRegisteredMatchCall, MSGBOX_DEFAULT
	waitfanfare
	closemessage
	setflag FLAG_ENABLE_MOM_MATCH_CALL

NewBarkTown_PlayersHouse_1F_EventScript_MomReceivePokenavFinish::
	setvar VAR_JOHTO_INTRO_STATE, 2
	return

NewBarkTown_PlayersHouse_1F_Movement_MomStepRight:
	walk_right
	step_end

NewBarkTown_PlayersHouse_1F_Movement_MomStepLeft:
	walk_left
	step_end

NewBarkTown_PlayersHouse_1F_EventScript_Stove::
	msgbox Crystal_NewBarkTown_PlayersHouse_1F_PlayersHouse1FStoveText, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_EventScript_Sink::
	msgbox Crystal_NewBarkTown_PlayersHouse_1F_PlayersHouse1FSinkText, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_EventScript_Fridge::
	msgbox Crystal_NewBarkTown_PlayersHouse_1F_PlayersHouse1FFridgeText, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_EventScript_TV::
	msgbox Crystal_NewBarkTown_PlayersHouse_1F_PlayersHouse1FTVText, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_Text_MomFirstTalk:
	.string "Oh, {PLAYER}...!\p"
	.string "Our neighbor, PROF. ELM, was looking\n"
	.string "for you.\p"
	.string "He said he wanted you to do something\n"
	.string "for him.\p"
	.string "Oh! I almost forgot! Your POKENAV is\n"
	.string "back from the repair shop.\p"
	.string "Here you go!$"

NewBarkTown_PlayersHouse_1F_Text_MomGavePokenav:
	.string "POKENAV, or just POKENAV.\p"
	.string "It's essential if you want to be a\n"
	.string "good trainer.$"

NewBarkTown_PlayersHouse_1F_Text_MomRegisteredMatchCall:
	.string "Your phone card is set up in MATCH\n"
	.string "CALL now.\p"
	.string "Call me if you need anything.$"

NewBarkTown_PlayersHouse_1F_Text_MomBeforeElm:
	.string "Hurry up! PROF. ELM is waiting right\n"
	.string "next door.$"

NewBarkTown_PlayersHouse_1F_Text_MomAfterElm:
	.string "So what was PROF. ELM's errand?\p"
	.string "That sounds exciting!$"

NewBarkTown_PlayersHouse_1F_Text_Stove:
	.string "The stove is spotless.\p"
	.string "MOM must have been up early.$"

NewBarkTown_PlayersHouse_1F_Text_Sink:
	.string "Everything in the kitchen has been\n"
	.string "put neatly in place.$"

NewBarkTown_PlayersHouse_1F_Text_Fridge:
	.string "Fresh food is packed inside.\p"
	.string "MOM never forgets to stock up.$"

NewBarkTown_PlayersHouse_1F_Text_TV:
	.string "A movie is on TV.\p"
	.string "The hero looks ready for an adventure.$"
