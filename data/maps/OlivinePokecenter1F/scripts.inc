@ Manually maintained after Johto import. Imported scaffold replaced.

OlivinePokecenter1F_MapScripts::
	.byte 0

JohtoScript_OlivinePokecenter1F_OlivinePokecenter1FFisherScript::
	lock
	faceplayer
	msgbox Crystal_OlivinePokecenter1F_OlivinePokecenter1FFisherText, MSGBOX_DEFAULT
	release
	end

JohtoScript_OlivinePokecenter1F_OlivinePokecenter1FFishingGuruScript::
	goto JohtoCommon_EventScript_HappinessCheck

JohtoScript_OlivinePokecenter1F_OlivinePokecenter1FNurseScript::
	setorcopyvar VAR_0x800B, LOCALID_OLIVINEPOKECENTER1F_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

JohtoScript_OlivinePokecenter1F_OlivinePokecenter1FTeacherScript::
	lock
	faceplayer
	msgbox Crystal_OlivinePokecenter1F_OlivinePokecenter1FTeacherText, MSGBOX_DEFAULT
	release
	end
