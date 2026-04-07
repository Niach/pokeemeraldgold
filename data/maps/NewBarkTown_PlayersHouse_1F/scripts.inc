NewBarkTown_PlayersHouse_1F_MapScripts::
	.byte 0

NewBarkTown_PlayersHouse_1F_EventScript_Mom::
	goto_if_lt VAR_JOHTO_INTRO_STATE, 2, NewBarkTown_PlayersHouse_1F_EventScript_MomFirstTalk
	goto_if_lt VAR_JOHTO_INTRO_STATE, 3, NewBarkTown_PlayersHouse_1F_EventScript_MomBeforeElm
	msgbox NewBarkTown_PlayersHouse_1F_Text_MomAfterElm, MSGBOX_NPC
	end

NewBarkTown_PlayersHouse_1F_EventScript_MomBeforeElm::
	msgbox NewBarkTown_PlayersHouse_1F_Text_MomBeforeElm, MSGBOX_NPC
	end

NewBarkTown_PlayersHouse_1F_EventScript_MomFirstTalk::
	msgbox NewBarkTown_PlayersHouse_1F_Text_MomFirstTalk, MSGBOX_NPC
	setvar VAR_JOHTO_INTRO_STATE, 2
	end

NewBarkTown_PlayersHouse_1F_EventScript_Stove::
	msgbox NewBarkTown_PlayersHouse_1F_Text_Stove, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_EventScript_Sink::
	msgbox NewBarkTown_PlayersHouse_1F_Text_Sink, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_EventScript_Fridge::
	msgbox NewBarkTown_PlayersHouse_1F_Text_Fridge, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_EventScript_TV::
	msgbox NewBarkTown_PlayersHouse_1F_Text_TV, MSGBOX_SIGN
	end

NewBarkTown_PlayersHouse_1F_Text_MomFirstTalk:
	.string "Good morning, {PLAYER}.\p"
	.string "PROF. ELM has been waiting for you\n"
	.string "at the lab next door since sunrise.$"

NewBarkTown_PlayersHouse_1F_Text_MomBeforeElm:
	.string "ELM's lab is right next door.\p"
	.string "You know how he gets when he's eager\n"
	.string "to share a new idea.$"

NewBarkTown_PlayersHouse_1F_Text_MomAfterElm:
	.string "I'm glad you checked in with PROF.\n"
	.string "ELM.\p"
	.string "For now, stay close to NEW BARK\n"
	.string "until the roads open.$"

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
