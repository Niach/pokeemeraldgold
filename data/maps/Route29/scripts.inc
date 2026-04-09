Route29_MapScripts::
	.byte 0

Route29_EventScript_CatchTutorialNorth::
	lockall
	applymovement LOCALID_ROUTE29_CATCHING_DUDE, Route29_Movement_DudeApproachNorth
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_WEST
	msgbox Crystal_Route29_CatchingTutorialIntroText, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route29_EventScript_TutorialDeclinedNorth
	special SavePlayerParty
	special LoadWallyZigzagoon
	follow LOCALID_ROUTE29_CATCHING_DUDE, LOCALID_PLAYER
	applymovement LOCALID_ROUTE29_CATCHING_DUDE, Route29_Movement_DudeReturnNorth
	waitmovement 0
	stopfollow
	special StartWallyTutorialBattle
	waitstate
	special LoadPlayerParty
	turnobject LOCALID_ROUTE29_CATCHING_DUDE, DIR_NORTH
	msgbox Crystal_Route29_CatchingTutorialDebriefText, MSGBOX_DEFAULT
	setvar VAR_JOHTO_ROUTE29_SCENE_STATE, 2
	releaseall
	end

Route29_EventScript_TutorialDeclinedNorth:
	msgbox Crystal_Route29_CatchingTutorialDeclinedText, MSGBOX_DEFAULT
	applymovement LOCALID_ROUTE29_CATCHING_DUDE, Route29_Movement_DudeReturnNorth
	waitmovement 0
	setvar VAR_JOHTO_ROUTE29_SCENE_STATE, 2
	releaseall
	end

Route29_EventScript_CatchTutorialSouth::
	lockall
	applymovement LOCALID_ROUTE29_CATCHING_DUDE, Route29_Movement_DudeApproachSouth
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_WEST
	msgbox Crystal_Route29_CatchingTutorialIntroText, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route29_EventScript_TutorialDeclinedSouth
	special SavePlayerParty
	special LoadWallyZigzagoon
	follow LOCALID_ROUTE29_CATCHING_DUDE, LOCALID_PLAYER
	applymovement LOCALID_ROUTE29_CATCHING_DUDE, Route29_Movement_DudeReturnSouth
	waitmovement 0
	stopfollow
	special StartWallyTutorialBattle
	waitstate
	special LoadPlayerParty
	turnobject LOCALID_ROUTE29_CATCHING_DUDE, DIR_NORTH
	msgbox Crystal_Route29_CatchingTutorialDebriefText, MSGBOX_DEFAULT
	setvar VAR_JOHTO_ROUTE29_SCENE_STATE, 2
	releaseall
	end

Route29_EventScript_TutorialDeclinedSouth:
	msgbox Crystal_Route29_CatchingTutorialDeclinedText, MSGBOX_DEFAULT
	applymovement LOCALID_ROUTE29_CATCHING_DUDE, Route29_Movement_DudeReturnSouth
	waitmovement 0
	setvar VAR_JOHTO_ROUTE29_SCENE_STATE, 2
	releaseall
	end

Route29_EventScript_CatchingDude::
	lock
	faceplayer
	goto_if_lt VAR_JOHTO_INTRO_STATE, 7, Route29_EventScript_CatchingDudeBeforeEgg
	goto_if_lt VAR_JOHTO_ROUTE29_SCENE_STATE, 2, Route29_EventScript_CatchingDudePrompt
	msgbox Crystal_Route29_CatchingTutorialDebriefText, MSGBOX_DEFAULT
	release
	end

Route29_EventScript_CatchingDudeBeforeEgg::
	msgbox Crystal_Route29_CatchingTutorialBoxFullText, MSGBOX_DEFAULT
	release
	end

Route29_EventScript_CatchingDudePrompt:
	msgbox Crystal_Route29_CatchingTutorialRepeatText, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, Route29_EventScript_CatchingDudeDeclined
	special SavePlayerParty
	special LoadWallyZigzagoon
	special StartWallyTutorialBattle
	waitstate
	special LoadPlayerParty
	msgbox Crystal_Route29_CatchingTutorialDebriefText, MSGBOX_DEFAULT
	release
	end

Route29_EventScript_CatchingDudeDeclined:
	msgbox Crystal_Route29_CatchingTutorialDeclinedText, MSGBOX_DEFAULT
	release
	end

Route29_EventScript_Youngster::
	msgbox Crystal_Route29_Route29YoungsterText, MSGBOX_NPC
	end

Route29_EventScript_Teacher::
	msgbox Crystal_Route29_Route29TeacherText, MSGBOX_NPC
	end

Route29_EventScript_Fisher::
	msgbox Crystal_Route29_Route29FisherText, MSGBOX_NPC
	end

Route29_EventScript_CooltrainerM::
	msgbox Crystal_Route29_Route29CooltrainerMText_WaitingForNight, MSGBOX_NPC
	end

Route29_EventScript_Tuscany::
	lock
	faceplayer
	msgbox Route29_Text_Tuscany, MSGBOX_DEFAULT
	release
	end

Route29_EventScript_ItemPotion::
	finditem ITEM_POTION
	end

Route29_EventScript_SignEast::
	msgbox Crystal_Route29_Route29Sign1Text, MSGBOX_SIGN
	end

Route29_EventScript_SignWest::
	msgbox Crystal_Route29_Route29Sign2Text, MSGBOX_SIGN
	end

Route29_Movement_DudeApproachNorth:
	walk_up
	walk_up
	walk_up
	walk_up
	walk_right
	walk_right
	step_end

Route29_Movement_DudeApproachSouth:
	walk_up
	walk_up
	walk_up
	walk_right
	walk_right
	step_end

Route29_Movement_DudeReturnNorth:
	walk_left
	walk_left
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

Route29_Movement_DudeReturnSouth:
	walk_left
	walk_left
	walk_down
	walk_down
	walk_down
	step_end

Route29_Text_CatchingDudeBeforeEgg:
	.string "POKéMON hide in the grass. Who knows\n"
	.string "when they'll pop out...$"

Route29_Text_CatchingTutorialIntro:
	.string "I've seen you a couple times. How\n"
	.string "many POKéMON have you caught?\p"
	.string "Would you like me to show you how to\n"
	.string "catch POKéMON?$"

Route29_Text_CatchingTutorialDebrief:
	.string "That's how you do it.\p"
	.string "If you weaken them first, POKéMON are\n"
	.string "easier to catch.$"

Route29_Text_CatchingTutorialDeclined:
	.string "Oh. Fine, then.\p"
	.string "Anyway, if you want to catch\n"
	.string "POKéMON, you have to walk a lot.$"

Route29_Text_CatchingTutorialRepeat:
	.string "Huh? You want me to show you how to\n"
	.string "catch POKéMON?$"

Route29_Text_CatchingTutorialRepeatInfo:
	.string "If you weaken them first, POKéMON are\n"
	.string "easier to catch.$"

Route29_Text_Youngster:
	.string "Yo. How are your POKéMON?\p"
	.string "If they're weak and not ready for\n"
	.string "battle, keep out of the grass.$"

Route29_Text_Teacher:
	.string "See those ledges?\p"
	.string "It's scary to jump off them.\p"
	.string "But you can go to NEW BARK without\n"
	.string "walking through the grass.$"

Route29_Text_Fisher:
	.string "I wanted to take a break, so I saved\n"
	.string "to record my progress.$"

Route29_Text_CooltrainerM:
	.string "I'm waiting for POKéMON that appear\n"
	.string "only at night.$"

Route29_Text_Tuscany:
	.string "I'm TUSCANY of Tuesday.\p"
	.string "Visit me on the right day, and I may\n"
	.string "have a gift for you.$"

Route29_Text_SignEast:
	.string "ROUTE 29\n"
	.string "{RIGHT_ARROW} CHERRYGROVE CITY$"

Route29_Text_SignWest:
	.string "ROUTE 29\n"
	.string "{LEFT_ARROW} NEW BARK TOWN$"
