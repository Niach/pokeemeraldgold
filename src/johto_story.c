#include "global.h"
#include "johto_story.h"
#include "data.h"
#include "event_data.h"
#include "main.h"
#include "naming_screen.h"
#include "overworld.h"
#include "pokedex.h"
#include "pokemon.h"
#include "region_map.h"
#include "rtc.h"
#include "string_util.h"
#include "strings.h"
#include "constants/characters.h"
#include "constants/global.h"
#include "constants/opponents.h"
#include "constants/trainers.h"

static const u8 sJohtoDefaultRivalName[] = _("SILVER");

static struct JohtoPortSave *GetJohtoPortSave(void)
{
    return &gSaveBlock1Ptr->johtoPort;
}

static bool8 IsSilverTrainerId(u16 trainerId)
{
    switch (trainerId)
    {
    case TRAINER_SILVER_TOTODILE:
    case TRAINER_SILVER_CHIKORITA:
    case TRAINER_SILVER_CYNDAQUIL:
        return TRUE;
    default:
        return FALSE;
    }
}

static u8 *GetJohtoRivalNameBuffer(void)
{
    return GetJohtoPortSave()->rivalName;
}

u8 GetJohtoSceneState(u16 sceneSlot)
{
    if (sceneSlot >= JOHTO_PORT_SCENE_SLOT_COUNT)
        return 0;

    return GetJohtoPortSave()->sceneStates[sceneSlot];
}

void SetJohtoSceneState(u16 sceneSlot, u8 state)
{
    if (sceneSlot >= JOHTO_PORT_SCENE_SLOT_COUNT)
        return;

    GetJohtoPortSave()->sceneStates[sceneSlot] = state;
}

void ResetJohtoPortState(void)
{
    CpuFill32(0, GetJohtoPortSave(), sizeof(*GetJohtoPortSave()));
}

void ResetJohtoRivalName(void)
{
    GetJohtoRivalNameBuffer()[0] = EOS;
}

const u8 *GetJohtoRivalName(void)
{
    if (GetJohtoRivalNameBuffer()[0] == EOS)
        return gText_ThreeQuestionMarks;

    return GetJohtoRivalNameBuffer();
}

const u8 *GetTrainerNameWithJohtoOverride(u16 trainerId)
{
    if (trainerId >= TRAINERS_COUNT)
        trainerId = TRAINER_NONE;

    if (trainerId == TRAINER_LINK_OPPONENT || trainerId == TRAINER_UNION_ROOM)
        return gTrainers[trainerId].trainerName;

    if (IsSilverTrainerId(trainerId))
        return GetJohtoRivalName();

    return gTrainers[trainerId].trainerName;
}

void BufferJohtoRivalName(void)
{
    StringCopy(gStringVar1, GetJohtoRivalName());
}

static void CB2_ReturnFromJohtoRivalNamingScreen(void)
{
    if (gStringVar2[0] == EOS)
        StringCopy(GetJohtoRivalNameBuffer(), sJohtoDefaultRivalName);
    else
        StringCopyN(GetJohtoRivalNameBuffer(), gStringVar2, PLAYER_NAME_LENGTH + 1);

    BufferJohtoRivalName();
    CB2_ReturnToFieldContinueScriptPlayMapMusic();
}

void DoJohtoRivalNamingScreen(void)
{
    if (GetJohtoRivalNameBuffer()[0] == EOS)
        StringCopy(gStringVar2, sJohtoDefaultRivalName);
    else
        StringCopy(gStringVar2, GetJohtoRivalNameBuffer());

    DoNamingScreen(NAMING_SCREEN_RIVAL, gStringVar2, MALE, 0, 0, CB2_ReturnFromJohtoRivalNamingScreen);
}

void SyncJohtoPlayersHouse2FDecorations(void)
{
    u8 decorFlags = GetJohtoPortSave()->bedroomDecorationFlags;

    if (decorFlags & (1 << JOHTO_BEDROOM_DECOR_CONSOLE))
        FlagClear(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_CONSOLE);
    else
        FlagSet(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_CONSOLE);

    if (decorFlags & (1 << JOHTO_BEDROOM_DECOR_DOLL_1))
        FlagClear(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_DOLL_1);
    else
        FlagSet(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_DOLL_1);

    if (decorFlags & (1 << JOHTO_BEDROOM_DECOR_DOLL_2))
        FlagClear(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_DOLL_2);
    else
        FlagSet(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_DOLL_2);

    if (decorFlags & (1 << JOHTO_BEDROOM_DECOR_BIG_DOLL))
        FlagClear(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_BIG_DOLL);
    else
        FlagSet(FLAG_HIDE_NEW_BARK_TOWN_PLAYERS_HOUSE_2F_BIG_DOLL);
}

void GetJohtoUnownCount(void)
{
    u16 count = 0;
    u16 species;

    if (GetSetPokedexFlag(SpeciesToNationalPokedexNum(SPECIES_UNOWN), FLAG_GET_CAUGHT))
        count++;

    for (species = SPECIES_UNOWN_B; species <= SPECIES_UNOWN_Z; species++)
    {
        if (GetSetPokedexFlag(SpeciesToNationalPokedexNum(species), FLAG_GET_CAUGHT))
            count++;
    }

    gSpecialVar_Result = count;
}

void BufferCurrentLandmarkName(void)
{
    GetMapName(gStringVar1, gMapHeader.regionMapSectionId, 0);
}

void GetJohtoWeekday(void)
{
    struct SiiRtcInfo rtc;

    if (!FlagGet(FLAG_SYS_CLOCK_SET))
    {
        gSpecialVar_Result = 0;
        return;
    }

    RtcGetInfo(&rtc);
    gSpecialVar_Result = rtc.dayOfWeek % 7;
}
