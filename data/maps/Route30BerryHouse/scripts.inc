Route30BerryHouse_MapScripts::
	.byte 0

Route30BerryHouse_EventScript_Pokefan::
	lock
	faceplayer
	goto_if_set FLAG_JOHTO_GOT_ROUTE30_BERRY_HOUSE_BERRY, Route30BerryHouse_EventScript_PokefanAfterGift
	msgbox Route30BerryHouse_Text_BeforeGift, MSGBOX_DEFAULT
	giveitem ITEM_ORAN_BERRY
	goto_if_eq VAR_RESULT, FALSE, Route30BerryHouse_EventScript_BagFull
	setflag FLAG_JOHTO_GOT_ROUTE30_BERRY_HOUSE_BERRY
	msgbox Route30BerryHouse_Text_AfterGift, MSGBOX_DEFAULT
	release
	end

Route30BerryHouse_EventScript_PokefanAfterGift:
	msgbox Route30BerryHouse_Text_AfterGift, MSGBOX_DEFAULT
	release
	end

Route30BerryHouse_EventScript_BagFull:
	msgbox gText_TooBadBagIsFull, MSGBOX_DEFAULT
	release
	end

Route30BerryHouse_EventScript_Bookshelf::
	msgbox Route30BerryHouse_Text_Bookshelf, MSGBOX_SIGN
	end

Route30BerryHouse_Text_BeforeGift:
	.string "Did you know POKeMON eat BERRIES?\p"
	.string "Here, take one with you.$"

Route30BerryHouse_Text_AfterGift:
	.string "Check berry trees whenever you spot\n"
	.string "them. They are worth the detour.$"

Route30BerryHouse_Text_Bookshelf:
	.string "It's packed with magazines about\n"
	.string "berries and POKeMON care.$"
