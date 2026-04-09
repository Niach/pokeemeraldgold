#ifndef GUARD_JOHTO_STORY_H
#define GUARD_JOHTO_STORY_H

enum
{
    JOHTO_SCENE_NEW_BARK_TOWN,
    JOHTO_SCENE_ELMS_LAB,
    JOHTO_SCENE_PLAYERS_HOUSE_1F,
    JOHTO_SCENE_PLAYERS_HOUSE_2F,
    JOHTO_SCENE_CHERRYGROVE_CITY,
    JOHTO_SCENE_GUIDE_GENTS_HOUSE,
    JOHTO_SCENE_ROUTE_29,
    JOHTO_SCENE_ROUTE_30,
    JOHTO_SCENE_MR_POKEMONS_HOUSE,
    JOHTO_SCENE_SLOT_COUNT_BOOTSTRAP,
};

const u8 *GetJohtoRivalName(void);
const u8 *GetTrainerNameWithJohtoOverride(u16 trainerId);
u8 GetJohtoSceneState(u16 sceneSlot);
void SetJohtoSceneState(u16 sceneSlot, u8 state);
void ResetJohtoPortState(void);
void ResetJohtoRivalName(void);
void BufferJohtoRivalName(void);
void DoJohtoRivalNamingScreen(void);
void SyncJohtoPlayersHouse2FDecorations(void);
void GetJohtoUnownCount(void);
void BufferCurrentLandmarkName(void);
void GetJohtoWeekday(void);

#endif // GUARD_JOHTO_STORY_H
