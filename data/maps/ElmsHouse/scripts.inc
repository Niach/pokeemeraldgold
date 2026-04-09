ElmsHouse_MapScripts::
	.byte 0

ElmsHouse_EventScript_Wife::
	lock
	faceplayer
	msgbox ElmsHouse_Text_Wife, MSGBOX_DEFAULT
	release
	end

ElmsHouse_EventScript_Son::
	lock
	faceplayer
	msgbox ElmsHouse_Text_Son, MSGBOX_DEFAULT
	release
	end

ElmsHouse_EventScript_PC::
	msgbox ElmsHouse_Text_PC, MSGBOX_SIGN
	end

ElmsHouse_EventScript_Bookshelf::
	msgbox ElmsHouse_Text_Bookshelf, MSGBOX_SIGN
	end

ElmsHouse_Text_Wife:
	.string "My husband gets so wrapped up in his\n"
	.string "POKeMON research that he forgets to eat.$"

ElmsHouse_Text_Son:
	.string "When I grow up, I'm going to help my\n"
	.string "dad and become a POKeMON professor!$"

ElmsHouse_Text_PC:
	.string "It's part of PROF. ELM's research.\p"
	.string "He keeps wondering where POKeMON\n"
	.string "come from and where they go.$"

ElmsHouse_Text_Bookshelf:
	.string "Difficult books about POKeMON are\n"
	.string "lined up in perfect order.$"
