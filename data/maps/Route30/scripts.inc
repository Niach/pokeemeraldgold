Route30_MapScripts::
	.byte 0

Route30_EventScript_JoeyScene::
	lockall
	msgbox Route30_Text_JoeySceneIntro, MSGBOX_DEFAULT
	playse SE_BANG
	applymovement LOCALID_ROUTE30_JOEY_MON_2, Route30_Movement_JoeyMonAttack
	waitmovement 0
	msgbox Route30_Text_JoeySceneAfter, MSGBOX_DEFAULT
	playse SE_BANG
	applymovement LOCALID_ROUTE30_JOEY_MON_1, Route30_Movement_MikeyMonAttack
	waitmovement 0
	setflag FLAG_HIDE_ROUTE30_JOEY_SCENE
	setflag FLAG_HIDE_ROUTE30_JOEY_MON_1
	setflag FLAG_HIDE_ROUTE30_JOEY_MON_2
	clearflag FLAG_HIDE_ROUTE30_JOEY_TRAINER
	removeobject LOCALID_ROUTE30_JOEY_SCENE
	removeobject LOCALID_ROUTE30_JOEY_MON_1
	removeobject LOCALID_ROUTE30_JOEY_MON_2
	addobject LOCALID_ROUTE30_JOEY_TRAINER
	releaseall
	end

Route30_EventScript_Joey::
	trainerbattle_single TRAINER_ROUTE30_JOEY, Route30_Text_JoeyIntro, Route30_Text_JoeyDefeat
	msgbox Route30_Text_JoeyAfter, MSGBOX_AUTOCLOSE
	end

Route30_EventScript_Mikey::
	trainerbattle_single TRAINER_ROUTE30_MIKEY, Route30_Text_MikeyIntro, Route30_Text_MikeyDefeat
	msgbox Route30_Text_MikeyAfter, MSGBOX_AUTOCLOSE
	end

Route30_EventScript_Don::
	trainerbattle_single TRAINER_ROUTE30_DON, Route30_Text_DonIntro, Route30_Text_DonDefeat
	msgbox Route30_Text_DonAfter, MSGBOX_AUTOCLOSE
	end

Route30_EventScript_Youngster::
	msgbox Route30_Text_Youngster, MSGBOX_NPC
	end

Route30_EventScript_CooltrainerF::
	msgbox Route30_Text_CooltrainerF, MSGBOX_NPC
	end

Route30_EventScript_ItemAntidote::
	finditem ITEM_ANTIDOTE
	end

Route30_EventScript_Sign::
	msgbox Route30_Text_Sign, MSGBOX_SIGN
	end

Route30_EventScript_DirectionsSign::
	msgbox Route30_Text_DirectionsSign, MSGBOX_SIGN
	end

Route30_EventScript_MrPokemonSign::
	msgbox Route30_Text_MrPokemonSign, MSGBOX_SIGN
	end

Route30_EventScript_TrainerTips::
	msgbox Route30_Text_TrainerTips, MSGBOX_SIGN
	end

Route30_Movement_JoeyMonAttack:
	walk_in_place_fast_up
	walk_in_place_fast_down
	step_end

Route30_Movement_MikeyMonAttack:
	walk_in_place_fast_down
	walk_in_place_fast_up
	step_end

Route30_Text_JoeySceneIntro:
	.string "Go, little guy!\p"
	.string "Use TACKLE!$"

Route30_Text_JoeySceneAfter:
	.string "What? This is a serious battle!\p"
	.string "Quit staring at us.$"

Route30_Text_JoeyIntro:
	.string "I just lost, so I'm looking for more\n"
	.string "POKeMON.\p"
	.string "You look weak. Come on, let's battle!$"

Route30_Text_JoeyDefeat:
	.string "Ack! I lost again!$"

Route30_Text_JoeyAfter:
	.string "I'm sticking with my favorite partner\n"
	.string "no matter what.$"

Route30_Text_MikeyIntro:
	.string "You're a POKeMON trainer, right?\p"
	.string "Then you have to battle!$"

Route30_Text_MikeyDefeat:
	.string "That's strange.\p"
	.string "I won before.$"

Route30_Text_MikeyAfter:
	.string "Becoming a good trainer takes a lot\n"
	.string "of practice.$"

Route30_Text_DonIntro:
	.string "Instead of a bug POKeMON, I found a\n"
	.string "trainer!$"

Route30_Text_DonDefeat:
	.string "Argh! You're too strong!$"

Route30_Text_DonAfter:
	.string "I ran out of POKE BALLS while I was\n"
	.string "catching POKeMON.$"

Route30_Text_Youngster:
	.string "MR. POKeMON's house is still a bit\n"
	.string "farther ahead.$"

Route30_Text_CooltrainerF:
	.string "I'm not a trainer, but I do like\n"
	.string "watching people pass through here.$"

Route30_Text_Sign:
	.string "ROUTE 30\n"
	.string "{DOWN_ARROW} CHERRYGROVE CITY$"

Route30_Text_DirectionsSign:
	.string "TRAINER TIPS\p"
	.string "Battle other trainers to make your\n"
	.string "POKeMON stronger.$"

Route30_Text_MrPokemonSign:
	.string "MR. POKeMON'S HOUSE\n"
	.string "{RIGHT_ARROW} AHEAD$"

Route30_Text_TrainerTips:
	.string "TRAINER TIPS\p"
	.string "POKeMON grow by battling and walking\n"
	.string "alongside you.$"
