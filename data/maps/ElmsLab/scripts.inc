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

ElmsLab_EventScript_PC::
	msgbox ElmsLab_Text_PC, MSGBOX_SIGN
	end

ElmsLab_EventScript_Bookshelf::
	msgbox ElmsLab_Text_Bookshelf, MSGBOX_SIGN
	end

ElmsLab_EventScript_Machine::
	msgbox ElmsLab_Text_Machine, MSGBOX_SIGN
	end

ElmsLab_Text_ElmFirstTalk:
	.string "Hello, {PLAYER}!\p"
	.string "I'm PROF. ELM.\p"
	.string "I'm getting my lab in NEW BARK TOWN\n"
	.string "ready for a full round of research.\p"
	.string "For now, take a look around town and\n"
	.string "get your bearings.$"

ElmsLab_Text_ElmRepeat:
	.string "There's still a lot to prepare before\n"
	.string "JOHTO is fully open to explore.$"

ElmsLab_Text_Aide:
	.string "PROF. ELM has been revising his notes\n"
	.string "all morning.\p"
	.string "He says this is only the beginning.$"

ElmsLab_Text_PC:
	.string "Research data is being organized into\n"
	.string "a brand-new system.$"

ElmsLab_Text_Bookshelf:
	.string "The shelves are packed with books on\n"
	.string "POKeMON habitats and evolution.$"

ElmsLab_Text_Machine:
	.string "The machine is humming softly.\p"
	.string "It looks like it's still calibrating.$"
