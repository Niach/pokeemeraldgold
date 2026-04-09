CherrygroveCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, CherrygroveCity_OnTransition
	.byte 0

CherrygroveCity_OnTransition:
	goto_if_set FLAG_JOHTO_CHERRYGROVE_GUIDE_COMPLETE, CherrygroveCity_OnTransition_GuideInHouse
	clearflag FLAG_HIDE_CHERRYGROVE_CITY_GUIDE_GENT
	setflag FLAG_HIDE_GUIDE_GENTS_HOUSE_GUIDE_GENT
	end

CherrygroveCity_OnTransition_GuideInHouse:
	setflag FLAG_HIDE_CHERRYGROVE_CITY_GUIDE_GENT
	clearflag FLAG_HIDE_GUIDE_GENTS_HOUSE_GUIDE_GENT
	end

CherrygroveCity_EventScript_GuideGent::
	lock
	faceplayer
	goto_if_set FLAG_JOHTO_CHERRYGROVE_GUIDE_COMPLETE, CherrygroveCity_EventScript_GuideAfterTour
	msgbox Crystal_CherrygroveCity_GuideGentIntroText, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, CherrygroveCity_EventScript_GuideNo
	lockall
	playbgm MUS_FOLLOW_ME, FALSE
	msgbox Crystal_CherrygroveCity_GuideGentTourText1, MSGBOX_DEFAULT
	follow LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, LOCALID_PLAYER
	applymovement LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, CherrygroveCity_Movement_Guide1
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_NORTH
	msgbox Crystal_CherrygroveCity_GuideGentPokecenterText, MSGBOX_DEFAULT
	applymovement LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, CherrygroveCity_Movement_Guide2
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_NORTH
	msgbox Crystal_CherrygroveCity_GuideGentMartText, MSGBOX_DEFAULT
	applymovement LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, CherrygroveCity_Movement_Guide3
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_NORTH
	msgbox Crystal_CherrygroveCity_GuideGentRoute30Text, MSGBOX_DEFAULT
	applymovement LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, CherrygroveCity_Movement_Guide4
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_WEST
	msgbox Crystal_CherrygroveCity_GuideGentSeaText, MSGBOX_DEFAULT
	applymovement LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, CherrygroveCity_Movement_Guide5
	waitmovement 0
	stopfollow
	turnobject LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, DIR_WEST
	turnobject LOCALID_PLAYER, DIR_EAST
	msgbox Crystal_CherrygroveCity_GuideGentGiftText, MSGBOX_DEFAULT
	msgbox CherrygroveCity_Text_GuideGiftUpdated, MSGBOX_DEFAULT
	msgbox CherrygroveCity_Text_GuidePokenav, MSGBOX_DEFAULT
	setflag FLAG_JOHTO_CHERRYGROVE_GUIDE_COMPLETE
	setflag FLAG_HIDE_CHERRYGROVE_CITY_GUIDE_GENT
	clearflag FLAG_HIDE_GUIDE_GENTS_HOUSE_GUIDE_GENT
	turnobject LOCALID_PLAYER, DIR_NORTH
	applymovement LOCALID_CHERRYGROVE_CITY_GUIDE_GENT, CherrygroveCity_Movement_Guide6
	waitmovement 0
	playse SE_DOOR
	waitse
	removeobject LOCALID_CHERRYGROVE_CITY_GUIDE_GENT
	fadedefaultbgm
	releaseall
	end

CherrygroveCity_EventScript_GuideNo:
	msgbox Crystal_CherrygroveCity_GuideGentNoText, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_GuideAfterTour:
	msgbox CherrygroveCity_Text_GuideAfterTour, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_Rival::
	msgbox Crystal_CherrygroveCity_CherrygroveRivalText_Seen, MSGBOX_NPC
	end

CherrygroveCity_EventScript_RivalSceneNorth::
	setobjectxy LOCALID_CHERRYGROVE_CITY_RIVAL, 39, 6
	goto CherrygroveCity_EventScript_RivalEncounter

CherrygroveCity_EventScript_RivalSceneSouth::
	setobjectxy LOCALID_CHERRYGROVE_CITY_RIVAL, 39, 7
	goto CherrygroveCity_EventScript_RivalEncounter

CherrygroveCity_EventScript_RivalEncounter:
	lockall
	turnobject LOCALID_PLAYER, DIR_EAST
	applymovement LOCALID_CHERRYGROVE_CITY_RIVAL, CherrygroveCity_Movement_RivalApproach
	waitmovement 0
	setflag FLAG_JOHTO_ALLOW_LOSS_CONTINUE
	goto_if_eq VAR_JOHTO_STARTER_SPECIES, SPECIES_TOTODILE, CherrygroveCity_EventScript_RivalBattleChikorita
	goto_if_eq VAR_JOHTO_STARTER_SPECIES, SPECIES_CHIKORITA, CherrygroveCity_EventScript_RivalBattleCyndaquil
	goto CherrygroveCity_EventScript_RivalBattleTotodile

CherrygroveCity_EventScript_RivalBattleTotodile:
	trainerbattle_single TRAINER_SILVER_TOTODILE, Crystal_CherrygroveCity_CherrygroveRivalText_Seen, Crystal_CherrygroveCity_RivalCherrygroveWinText, CherrygroveCity_EventScript_RivalAfterBattle, NO_MUSIC

CherrygroveCity_EventScript_RivalBattleChikorita:
	trainerbattle_single TRAINER_SILVER_CHIKORITA, Crystal_CherrygroveCity_CherrygroveRivalText_Seen, Crystal_CherrygroveCity_RivalCherrygroveWinText, CherrygroveCity_EventScript_RivalAfterBattle, NO_MUSIC

CherrygroveCity_EventScript_RivalBattleCyndaquil:
	trainerbattle_single TRAINER_SILVER_CYNDAQUIL, Crystal_CherrygroveCity_CherrygroveRivalText_Seen, Crystal_CherrygroveCity_RivalCherrygroveWinText, CherrygroveCity_EventScript_RivalAfterBattle, NO_MUSIC

CherrygroveCity_EventScript_RivalAfterBattle:
	msgbox Crystal_CherrygroveCity_CherrygroveRivalText_YouWon, MSGBOX_DEFAULT
	playse SE_BANG
	applymovement LOCALID_PLAYER, CherrygroveCity_Movement_RivalPush
	waitmovement 0
	waitse
	turnobject LOCALID_PLAYER, DIR_WEST
	applymovement LOCALID_CHERRYGROVE_CITY_RIVAL, CherrygroveCity_Movement_RivalExit
	waitmovement 0
	setvar VAR_JOHTO_CHERRYGROVE_SCENE_STATE, 2
	setflag FLAG_HIDE_CHERRYGROVE_CITY_RIVAL
	removeobject LOCALID_CHERRYGROVE_CITY_RIVAL
	special HealPlayerParty
	releaseall
	end

CherrygroveCity_EventScript_Teacher::
	lock
	faceplayer
	goto_if_set FLAG_JOHTO_CHERRYGROVE_GUIDE_COMPLETE, CherrygroveCity_EventScript_TeacherHaveMap
	msgbox Crystal_CherrygroveCity_CherrygroveTeacherText_NoMapCard, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_TeacherHaveMap:
	msgbox Crystal_CherrygroveCity_CherrygroveTeacherText_HaveMapCard, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_Youngster::
	lock
	faceplayer
	goto_if_set FLAG_SYS_POKEDEX_GET, CherrygroveCity_EventScript_YoungsterHavePokedex
	msgbox Crystal_CherrygroveCity_CherrygroveYoungsterText_NoPokedex, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_YoungsterHavePokedex:
	msgbox Crystal_CherrygroveCity_CherrygroveYoungsterText_HavePokedex, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_Fisher::
	lock
	faceplayer
	goto_if_set FLAG_JOHTO_GOT_CHERRYGROVE_MYSTIC_WATER, CherrygroveCity_EventScript_FisherAfterGift
	msgbox Crystal_CherrygroveCity_MysticWaterGuyTextBefore, MSGBOX_DEFAULT
	giveitem ITEM_MYSTIC_WATER
	goto_if_eq VAR_RESULT, FALSE, CherrygroveCity_EventScript_FisherBagFull
	setflag FLAG_JOHTO_GOT_CHERRYGROVE_MYSTIC_WATER
	msgbox Crystal_CherrygroveCity_MysticWaterGuyTextAfter, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_FisherAfterGift:
	msgbox Crystal_CherrygroveCity_MysticWaterGuyTextAfter, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_FisherBagFull:
	msgbox gText_TooBadBagIsFull, MSGBOX_DEFAULT
	release
	end

CherrygroveCity_EventScript_CitySign::
	msgbox Crystal_CherrygroveCity_CherrygroveCitySignText, MSGBOX_SIGN
	end

CherrygroveCity_EventScript_GuideHouseSign::
	msgbox Crystal_CherrygroveCity_GuideGentsHouseSignText, MSGBOX_SIGN
	end

CherrygroveCity_EventScript_MartSign::
	msgbox CherrygroveCity_Text_MartSign, MSGBOX_SIGN
	end

CherrygroveCity_EventScript_PokecenterSign::
	msgbox CherrygroveCity_Text_PokecenterSign, MSGBOX_SIGN
	end

CherrygroveCity_Movement_Guide1:
	walk_left
	walk_left
	walk_up
	walk_left
	step_end

CherrygroveCity_Movement_Guide2:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

CherrygroveCity_Movement_Guide3:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

CherrygroveCity_Movement_Guide4:
	walk_left
	walk_left
	walk_left
	walk_down
	walk_left
	walk_left
	walk_left
	walk_down
	step_end

CherrygroveCity_Movement_Guide5:
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	walk_down
	walk_down
	walk_right
	walk_right
	walk_right
	walk_right
	walk_right
	step_end

CherrygroveCity_Movement_Guide6:
	walk_up
	walk_up
	step_end

CherrygroveCity_Movement_RivalApproach:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_left
	step_end

CherrygroveCity_Movement_RivalPush:
	walk_fast_down
	face_up
	step_end

CherrygroveCity_Movement_RivalExit:
	walk_left
	walk_left
	walk_left
	walk_left
	walk_up
	walk_up
	walk_left
	walk_left
	step_end

CherrygroveCity_Text_GuideIntro:
	.string "You're a rookie trainer, aren't you?\n"
	.string "I can tell!\p"
	.string "That's OK! Everyone is a rookie at\n"
	.string "some point!\p"
	.string "If you'd like, I can teach you a few\n"
	.string "things.$"

CherrygroveCity_Text_GuideNo:
	.string "Oh... It's something I enjoy doing.\p"
	.string "Fine. Come see me when you like.$"

CherrygroveCity_Text_GuideTourPokecenterLead:
	.string "OK, then!\p"
	.string "Follow me!$"

CherrygroveCity_Text_GuidePokecenter:
	.string "This is a POKeMON CENTER.\p"
	.string "They heal your POKeMON in no time at\n"
	.string "all.\p"
	.string "You'll be relying on them a lot, so\n"
	.string "you'd better learn about them.$"

CherrygroveCity_Text_GuideMart:
	.string "This is a POKeMON MART.\p"
	.string "They sell BALLS for catching wild\n"
	.string "POKeMON and other useful items.$"

CherrygroveCity_Text_GuideRoute30:
	.string "ROUTE 30 is out this way.\p"
	.string "Trainers will be battling their prized\n"
	.string "POKeMON there.$"

CherrygroveCity_Text_GuideSea:
	.string "This is the sea, as you can see.\p"
	.string "Some POKeMON are found only in water.$"

CherrygroveCity_Text_GuideGift:
	.string "Here...\p"
	.string "It's my house! Thanks for your\n"
	.string "company.\p"
	.string "Let me give you a small gift.$"

CherrygroveCity_Text_GuideGiftUpdated:
	.string "{PLAYER}'s POKENAV now has a JOHTO\n"
	.string "map!$"

CherrygroveCity_Text_GuidePokenav:
	.string "Your POKENAV becomes more useful as\n"
	.string "you add more features.\p"
	.string "I wish you luck on your journey!$"

CherrygroveCity_Text_GuideAfterTour:
	.string "Your POKENAV map should make getting\n"
	.string "around JOHTO much easier.$"

CherrygroveCity_Text_RivalSeen:
	.string "<...> <...> <...>\p"
	.string "You got a POKeMON at the lab.\p"
	.string "What a waste. A wimp like you.\p"
	.string "<...> <...> <...>\p"
	.string "Don't you get what I'm saying?\p"
	.string "Well, I, too, have a good POKeMON.\p"
	.string "I'll show you what I mean!$"

CherrygroveCity_Text_RivalBattleLoss:
	.string "Humph. Are you happy you won?$"

CherrygroveCity_Text_RivalAfterBattle:
	.string "<...> <...> <...>\p"
	.string "My name's ???.\p"
	.string "I'm going to be the world's greatest\n"
	.string "POKeMON trainer.$"

CherrygroveCity_Text_TeacherNoMap:
	.string "Did you talk to the old man by the\n"
	.string "POKeMON CENTER?\p"
	.string "He'll put a map of JOHTO on your\n"
	.string "POKENAV.$"

CherrygroveCity_Text_TeacherHaveMap:
	.string "When you're with POKeMON, going\n"
	.string "anywhere is fun.$"

CherrygroveCity_Text_YoungsterNoPokedex:
	.string "MR. POKeMON's house is still farther\n"
	.string "up ahead.$"

CherrygroveCity_Text_YoungsterHavePokedex:
	.string "I battled the trainers on the road.\p"
	.string "My POKeMON lost. They're a mess!\p"
	.string "I must take them to a POKeMON\n"
	.string "CENTER.$"

CherrygroveCity_Text_FisherBeforeGift:
	.string "A POKeMON I caught had an item.\p"
	.string "I think it's MYSTIC WATER.\p"
	.string "I don't need it, so do you want it?$"

CherrygroveCity_Text_FisherAfterGift:
	.string "Back to fishing for me, then.$"

CherrygroveCity_Text_CitySign:
	.string "CHERRYGROVE CITY\p"
	.string "The City of Cute, Fragrant Flowers$"

CherrygroveCity_Text_GuideHouseSign:
	.string "GUIDE GENT'S HOUSE$"

CherrygroveCity_Text_MartSign:
	.string "POKeMON MART$"

CherrygroveCity_Text_PokecenterSign:
	.string "POKeMON CENTER$"
