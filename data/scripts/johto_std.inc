JohtoCommon_EventScript_DifficultBookshelf::
	msgbox JohtoCommon_Text_DifficultBookshelf, MSGBOX_SIGN
	end

JohtoCommon_EventScript_PictureBookshelf::
	msgbox JohtoCommon_Text_PictureBookshelf, MSGBOX_SIGN
	end

JohtoCommon_EventScript_MagazineBookshelf::
	msgbox JohtoCommon_Text_MagazineBookshelf, MSGBOX_SIGN
	end

JohtoCommon_EventScript_ElevatorButton::
	playse SE_SELECT
	delay 15
	playse SE_ELEVATOR
	end

JohtoCommon_EventScript_Radio1::
	msgbox JohtoCommon_Text_Radio1, MSGBOX_SIGN
	end

JohtoCommon_EventScript_Radio2::
	msgbox JohtoCommon_Text_Radio2, MSGBOX_SIGN
	end

JohtoCommon_EventScript_GymStatue1::
	special BufferCurrentLandmarkName
	msgbox JohtoCommon_Text_GymStatueCityGym, MSGBOX_SIGN
	end

JohtoCommon_EventScript_GymStatue2::
	special BufferCurrentLandmarkName
	message JohtoCommon_Text_GymStatueCityGym
	waitmessage
	waitbuttonpress
	msgbox JohtoCommon_Text_GymStatueWinningTrainers, MSGBOX_SIGN
	end

JohtoCommon_EventScript_TeamRocketOath::
	msgbox JohtoCommon_Text_TeamRocketOath, MSGBOX_SIGN
	end

JohtoCommon_EventScript_TrashCan::
	msgbox JohtoCommon_Text_TrashCan, MSGBOX_SIGN
	end

JohtoCommon_EventScript_HappinessCheck::
	lock
	faceplayer
	bufferleadmonspeciesname STR_VAR_3
	msgbox Crystal_GoldenrodHappinessRater_GoldenrodHappinessRaterTeacherText, MSGBOX_DEFAULT
	specialvar VAR_RESULT, GetLeadMonFriendshipScore
	switch VAR_RESULT
	case FRIENDSHIP_NONE, JohtoCommon_EventScript_HappinessCheck_LooksMean
	case FRIENDSHIP_1_TO_49, JohtoCommon_EventScript_HappinessCheck_NotUsedToYou
	case FRIENDSHIP_50_TO_99, JohtoCommon_EventScript_HappinessCheck_QuiteCute
	case FRIENDSHIP_100_TO_149, JohtoCommon_EventScript_HappinessCheck_SortOfHappy
	case FRIENDSHIP_150_TO_199, JohtoCommon_EventScript_HappinessCheck_ReallyTrustsYou
	case FRIENDSHIP_200_TO_254, JohtoCommon_EventScript_HappinessCheck_LovesYouALot
	case FRIENDSHIP_MAX, JohtoCommon_EventScript_HappinessCheck_LovesYouALot
	release
	end

JohtoCommon_EventScript_HappinessCheck_LovesYouALot:
	msgbox Crystal_GoldenrodHappinessRater_GoldenrodHappinessRatingText_LovesYouALot, MSGBOX_DEFAULT
	release
	end

JohtoCommon_EventScript_HappinessCheck_ReallyTrustsYou:
	msgbox Crystal_GoldenrodHappinessRater_GoldenrodHappinessRatingText_ReallyTrustsYou, MSGBOX_DEFAULT
	release
	end

JohtoCommon_EventScript_HappinessCheck_SortOfHappy:
	msgbox Crystal_GoldenrodHappinessRater_GoldenrodHappinessRatingText_SortOfHappy, MSGBOX_DEFAULT
	release
	end

JohtoCommon_EventScript_HappinessCheck_QuiteCute:
	msgbox Crystal_GoldenrodHappinessRater_GoldenrodHappinessRatingText_QuiteCute, MSGBOX_DEFAULT
	release
	end

JohtoCommon_EventScript_HappinessCheck_NotUsedToYou:
	msgbox Crystal_GoldenrodHappinessRater_GoldenrodHappinessRatingText_NotUsedToYou, MSGBOX_DEFAULT
	release
	end

JohtoCommon_EventScript_HappinessCheck_LooksMean:
	msgbox Crystal_GoldenrodHappinessRater_GoldenrodHappinessRatingText_LooksMean, MSGBOX_DEFAULT
	release
	end

JohtoCommon_EventScript_ElmsAideTogepiEgg::
	lock
	faceplayer
	opentext
	checkevent EVENT_REFUSED_TOGEPI_EGG_FROM_ELMS_AIDE
	iftrue JohtoCommon_EventScript_ElmsAideTogepiEgg_AskAgain
	writetext Crystal_VioletPokecenter1F_VioletPokecenterElmsAideFavorText
	promptbutton
	goto JohtoCommon_EventScript_ElmsAideTogepiEgg_Prompt

JohtoCommon_EventScript_ElmsAideTogepiEgg_AskAgain::
	writetext Crystal_VioletPokecenter1F_VioletPokecenterElmsAideAskEggText
	promptbutton

JohtoCommon_EventScript_ElmsAideTogepiEgg_Prompt::
	yesorno
	iffalse JohtoCommon_EventScript_ElmsAideTogepiEgg_Refused
	getpartysize
	goto_if_eq VAR_RESULT, PARTY_SIZE, JohtoCommon_EventScript_ElmsAideTogepiEgg_PartyFull
	playfanfare MUS_OBTAIN_ITEM
	message JohtoCommon_Text_ReceivedTheEgg
	waitmessage
	waitfanfare
	giveegg SPECIES_TOGEPI
	setevent EVENT_GOT_TOGEPI_EGG_FROM_ELMS_AIDE
	clearevent EVENT_REFUSED_TOGEPI_EGG_FROM_ELMS_AIDE
	setvar VAR_JOHTO_VIOLET_SCENE_STATE, 1
	writetext Crystal_VioletPokecenter1F_VioletPokecenterElmsAideGiveEggText
	waitbutton
	closetext
	release
	end

JohtoCommon_EventScript_ElmsAideTogepiEgg_Refused::
	setevent EVENT_REFUSED_TOGEPI_EGG_FROM_ELMS_AIDE
	writetext Crystal_VioletPokecenter1F_VioletPokecenterElmsAideRefuseText
	waitbutton
	closetext
	release
	end

JohtoCommon_EventScript_ElmsAideTogepiEgg_PartyFull::
	writetext Crystal_VioletPokecenter1F_VioletCityElmsAideFullPartyText
	waitbutton
	closetext
	release
	end

JohtoCommon_Text_DifficultBookshelf:
	.string "It's full of difficult books.$"

JohtoCommon_Text_PictureBookshelf:
	.string "A whole collection of POKéMON\n"
	.string "picture books!$"

JohtoCommon_Text_MagazineBookshelf:
	.string "POKéMON magazines... POKéMON PAL,\p"
	.string "POKéMON HANDBOOK, POKéMON GRAPH...$"

JohtoCommon_Text_Radio1:
	.string "POKéMON CHANNEL...\p"
	.string "The radio is playing a cheerful\n"
	.string "program about POKéMON.$"

JohtoCommon_Text_Radio2:
	.string "LUCKY NUMBER SHOW!\p"
	.string "Today's drawing is being announced\n"
	.string "on the radio.$"

JohtoCommon_Text_GymStatueCityGym:
	.string "{STR_VAR_1}\n"
	.string "POKéMON GYM.$"

JohtoCommon_Text_GymStatueWinningTrainers:
	.string "LEADER: {STR_VAR_2}\p"
	.string "WINNING TRAINERS:\n"
	.string "{PLAYER}.$"

JohtoCommon_Text_TeamRocketOath:
	.string "TEAM ROCKET OATH\p"
	.string "Steal POKéMON for profit!\p"
	.string "Exploit POKéMON for profit!\p"
	.string "All POKéMON exist for the glory of\n"
	.string "TEAM ROCKET!$"

JohtoCommon_Text_TrashCan:
	.string "There's nothing in here...$"

JohtoCommon_Text_ReceivedTheEgg:
	.string "{PLAYER} received the EGG.$"
