GuideGentsHouse_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, GuideGentsHouse_OnTransition
	.byte 0

GuideGentsHouse_OnTransition:
	goto_if_set FLAG_JOHTO_CHERRYGROVE_GUIDE_COMPLETE, GuideGentsHouse_OnTransition_ShowGuide
	setflag FLAG_HIDE_GUIDE_GENTS_HOUSE_GUIDE_GENT
	clearflag FLAG_HIDE_CHERRYGROVE_CITY_GUIDE_GENT
	end

GuideGentsHouse_OnTransition_ShowGuide:
	clearflag FLAG_HIDE_GUIDE_GENTS_HOUSE_GUIDE_GENT
	setflag FLAG_HIDE_CHERRYGROVE_CITY_GUIDE_GENT
	end

GuideGentsHouse_EventScript_GuideGent::
	lock
	faceplayer
	msgbox Crystal_GuideGentsHouse_GuideGentsHouseGuideGentText, MSGBOX_DEFAULT
	release
	end

GuideGentsHouse_EventScript_Bookshelf::
	msgbox GuideGentsHouse_Text_Bookshelf, MSGBOX_SIGN
	end

GuideGentsHouse_Text_GuideGent:
	.string "When I was a wee lad, I was a hot-\n"
	.string "shot trainer!\p"
	.string "Here's a word of advice: Catch lots\n"
	.string "of POKéMON!\p"
	.string "Treat them all with kindness!$"

GuideGentsHouse_Text_Bookshelf:
	.string "Travel magazines and guidebooks are\n"
	.string "stacked to the ceiling.$"
