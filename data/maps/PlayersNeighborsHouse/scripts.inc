PlayersNeighborsHouse_MapScripts::
	.byte 0

PlayersNeighborsHouse_EventScript_Daughter::
	lock
	faceplayer
	msgbox PlayersNeighborsHouse_Text_Daughter, MSGBOX_DEFAULT
	release
	end

PlayersNeighborsHouse_EventScript_Neighbor::
	lock
	faceplayer
	msgbox PlayersNeighborsHouse_Text_Neighbor, MSGBOX_DEFAULT
	release
	end

PlayersNeighborsHouse_EventScript_Bookshelf::
	msgbox PlayersNeighborsHouse_Text_Bookshelf, MSGBOX_SIGN
	end

PlayersNeighborsHouse_EventScript_Radio::
	msgbox PlayersNeighborsHouse_Text_Radio, MSGBOX_SIGN
	end

PlayersNeighborsHouse_Text_Daughter:
	.string "PIKACHU is an evolved POKeMON.\p"
	.string "PROF. ELM's research on evolution is\n"
	.string "amazing, isn't it?$"

PlayersNeighborsHouse_Text_Neighbor:
	.string "My daughter is determined to become\n"
	.string "PROF. ELM's assistant someday.$"

PlayersNeighborsHouse_Text_Bookshelf:
	.string "Magazines and guidebooks are stacked\n"
	.string "neatly on the shelf.$"

PlayersNeighborsHouse_Text_Radio:
	.string "The radio is buzzing with another\n"
	.string "POKeMON talk show.$"
