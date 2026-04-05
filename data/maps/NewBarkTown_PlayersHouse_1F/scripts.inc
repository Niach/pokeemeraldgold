NewBarkTown_PlayersHouse_1F_MapScripts::
	.byte 0

NewBarkTown_PlayersHouse_1F_EventScript_Mom::
	goto_if_lt VAR_JOHTO_INTRO_STATE, 2, NewBarkTown_PlayersHouse_1F_EventScript_MomFirstTalk
	msgbox NewBarkTown_PlayersHouse_1F_Text_MomRepeat, MSGBOX_NPC
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

NewBarkTown_PlayersHouse_1F_Text_MomRepeat:
	.string "Don't stay out too long.\p"
	.string "Until the roads open up, NEW BARK\n"
	.string "is the safest place to be.$"

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
