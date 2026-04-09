MrPokemonsHouse_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, MrPokemonsHouse_OnFrame
	.byte 0

MrPokemonsHouse_OnFrame:
	map_script_2 VAR_JOHTO_INTRO_STATE, 4, MrPokemonsHouse_EventScript_MeetMrPokemon
	.2byte 0

MrPokemonsHouse_EventScript_MeetMrPokemon:
	lockall
	turnobject LOCALID_MR_POKEMONS_HOUSE_MR_POKEMON, DIR_SOUTH
	msgbox MrPokemonsHouse_Text_MrPokemonIntro1, MSGBOX_DEFAULT
	msgbox MrPokemonsHouse_Text_MrPokemonIntro2, MSGBOX_DEFAULT
	setflag FLAG_JOHTO_GOT_MYSTERY_EGG
	setvar VAR_JOHTO_INTRO_STATE, 5
	msgbox MrPokemonsHouse_Text_MrPokemonIntro3, MSGBOX_DEFAULT
	applymovement LOCALID_MR_POKEMONS_HOUSE_OAK, MrPokemonsHouse_Movement_OakApproach
	waitmovement 0
	turnobject LOCALID_PLAYER, DIR_EAST
	msgbox MrPokemonsHouse_Text_OakIntro, MSGBOX_DEFAULT
	playfanfare MUS_OBTAIN_ITEM
	message MrPokemonsHouse_Text_ReceivedPokedex
	waitfanfare
	setflag FLAG_SYS_POKEDEX_GET
	special SetUnlockedPokedexFlags
	setflag FLAG_ADVENTURE_STARTED
	msgbox MrPokemonsHouse_Text_OakAfterDex, MSGBOX_DEFAULT
	turnobject LOCALID_PLAYER, DIR_SOUTH
	applymovement LOCALID_MR_POKEMONS_HOUSE_OAK, MrPokemonsHouse_Movement_OakExit
	waitmovement 0
	setflag FLAG_HIDE_MR_POKEMONS_HOUSE_OAK
	removeobject LOCALID_MR_POKEMONS_HOUSE_OAK
	setflag FLAG_HIDE_NEW_BARK_TOWN_RIVAL
	clearflag FLAG_HIDE_CHERRYGROVE_CITY_RIVAL
	setvar VAR_JOHTO_CHERRYGROVE_SCENE_STATE, 1
	special HealPlayerParty
	msgbox MrPokemonsHouse_Text_MrPokemonHeal, MSGBOX_DEFAULT
	releaseall
	end

MrPokemonsHouse_EventScript_MrPokemon::
	lock
	faceplayer
	goto_if_set FLAG_JOHTO_GOT_MYSTERY_EGG, MrPokemonsHouse_EventScript_MrPokemonAfterEgg
	msgbox MrPokemonsHouse_Text_MrPokemonBeforeEgg, MSGBOX_DEFAULT
	release
	end

MrPokemonsHouse_EventScript_MrPokemonAfterEgg:
	msgbox MrPokemonsHouse_Text_MrPokemonAfterEgg, MSGBOX_DEFAULT
	release
	end

MrPokemonsHouse_EventScript_Oak::
	lock
	faceplayer
	msgbox MrPokemonsHouse_Text_OakAfterDex, MSGBOX_DEFAULT
	release
	end

MrPokemonsHouse_EventScript_Magazines::
	msgbox MrPokemonsHouse_Text_Magazines, MSGBOX_SIGN
	end

MrPokemonsHouse_EventScript_BrokenComputer::
	msgbox MrPokemonsHouse_Text_BrokenComputer, MSGBOX_SIGN
	end

MrPokemonsHouse_EventScript_StrangeCoins::
	msgbox MrPokemonsHouse_Text_StrangeCoins, MSGBOX_SIGN
	end

MrPokemonsHouse_Movement_OakApproach:
	walk_down
	walk_left
	walk_left
	step_end

MrPokemonsHouse_Movement_OakExit:
	walk_down
	walk_left
	step_end

MrPokemonsHouse_Text_MrPokemonIntro1:
	.string "Hello, hello! You must be {PLAYER}.\p"
	.string "PROF. ELM said you would visit.$"

MrPokemonsHouse_Text_MrPokemonIntro2:
	.string "I wanted him to examine this strange\n"
	.string "EGG for me.$"

MrPokemonsHouse_Text_MrPokemonIntro3:
	.string "Please take the MYSTERY EGG back to\n"
	.string "PROF. ELM.\p"
	.string "He'll know more about it than I do.$"

MrPokemonsHouse_Text_OakIntro:
	.string "So you're the one helping PROF. ELM.\p"
	.string "I'm PROF. OAK.\p"
	.string "Since you're already traveling, you\n"
	.string "should start recording your encounters.$"

MrPokemonsHouse_Text_ReceivedPokedex:
	.string "{PLAYER} received the POKEDEX!$"

MrPokemonsHouse_Text_OakAfterDex:
	.string "The POKEDEX automatically records\n"
	.string "data on POKeMON you've seen or caught.\p"
	.string "Treat your partner well, and you'll\n"
	.string "learn a lot together.$"

MrPokemonsHouse_Text_MrPokemonHeal:
	.string "Heading back to ELM?\p"
	.string "Let me heal your POKeMON before you\n"
	.string "go.$"

MrPokemonsHouse_Text_MrPokemonBeforeEgg:
	.string "PROF. ELM said you'd be coming.\p"
	.string "Take your time and have a look around.$"

MrPokemonsHouse_Text_MrPokemonAfterEgg:
	.string "I'm counting on you to get that EGG\n"
	.string "back to PROF. ELM safely.$"

MrPokemonsHouse_Text_Magazines:
	.string "It's full of foreign magazines.\p"
	.string "The pictures are fascinating.$"

MrPokemonsHouse_Text_BrokenComputer:
	.string "A battered computer hums quietly.\p"
	.string "It has clearly seen better days.$"

MrPokemonsHouse_Text_StrangeCoins:
	.string "Odd coins from distant regions are\n"
	.string "lined up on the table.$"
