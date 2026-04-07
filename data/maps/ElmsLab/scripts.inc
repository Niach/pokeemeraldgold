ElmsLab_MapScripts::
	.byte 0

ElmsLab_EventScript_Elm::
	goto_if_lt VAR_JOHTO_INTRO_STATE, 3, ElmsLab_EventScript_ElmFirstTalk
	msgbox ElmsLab_Text_ElmRepeat, MSGBOX_NPC
	end

ElmsLab_EventScript_ElmFirstTalk::
	msgbox ElmsLab_Text_ElmFirstTalk, MSGBOX_NPC
	setvar VAR_JOHTO_INTRO_STATE, 3
	end

ElmsLab_EventScript_Aide::
	msgbox ElmsLab_Text_Aide, MSGBOX_NPC
	end

ElmsLab_EventScript_Officer::
	msgbox ElmsLab_Text_Officer, MSGBOX_NPC
	end

ElmsLab_EventScript_CyndaquilBall::
	msgbox ElmsLab_Text_CyndaquilBall, MSGBOX_DEFAULT
	end

ElmsLab_EventScript_TotodileBall::
	msgbox ElmsLab_Text_TotodileBall, MSGBOX_DEFAULT
	end

ElmsLab_EventScript_ChikoritaBall::
	msgbox ElmsLab_Text_ChikoritaBall, MSGBOX_DEFAULT
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

ElmsLab_Text_ElmFirstTalk:
	.string "Hello, {PLAYER}!\p"
	.string "I'm PROF. ELM.\p"
	.string "I'm still getting my NEW BARK lab in\n"
	.string "working order.\p"
	.string "For now, have a look around town.\n"
	.string "We'll tackle the next step soon.$"

ElmsLab_Text_ElmRepeat:
	.string "There's still a lot to prepare before\n"
	.string "JOHTO is fully open to explore.$"

ElmsLab_Text_Aide:
	.string "PROF. ELM has been revising his notes\n"
	.string "all morning.\p"
	.string "He says this is only the beginning.$"

ElmsLab_Text_Officer:
	.string "I'm keeping an eye on the lab while\n"
	.string "everything settles down.$"

ElmsLab_Text_CyndaquilBall:
	.string "A CYNDAQUIL waits inside.\p"
	.string "ELM hasn't started the handoff yet.$"

ElmsLab_Text_TotodileBall:
	.string "A TOTODILE splashes around inside.\p"
	.string "The starter display is almost ready.$"

ElmsLab_Text_ChikoritaBall:
	.string "A CHIKORITA is resting calmly inside.\p"
	.string "ELM is still preparing the lab.$"

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
	.string "Open your MENU and record your trip\n"
	.string "often while JOHTO is still growing.$"

ElmsLab_Text_TravelTip2:
	.string "TRAVEL TIP 2\p"
	.string "Talk to people in town.\n"
	.string "They always know what's changing.$"

ElmsLab_Text_TravelTip3:
	.string "TRAVEL TIP 3\p"
	.string "A calm beginning makes room for a\n"
	.string "bigger adventure later.$"

ElmsLab_Text_TravelTip4:
	.string "TRAVEL TIP 4\p"
	.string "Even a small town can feel huge when\n"
	.string "it's the first step of a journey.$"

ElmsLab_Text_Trashcan:
	.string "It's filled with failed printouts and\n"
	.string "discarded research notes.$"

ElmsLab_Text_Window:
	.string "You can see NEW BARK TOWN stretching\n"
	.string "out beyond the lab.$"
