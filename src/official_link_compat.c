#include "global.h"
#include "event_data.h"
#include "mail.h"
#include "official_link_compat.h"
#include "pokemon.h"
#include "string_util.h"
#include "constants/abilities.h"
#include "constants/cable_club.h"
#include "constants/global.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/species.h"
#include "constants/trainers.h"
#include "constants/union_room.h"
#include "link.h"

STATIC_ASSERT(GAME_VERSION == VERSION_EMERALD, OfficialLinkGameVersionMustRemainRetailEmerald);
STATIC_ASSERT(sizeof(struct PokemonSubstruct0) == 12, OfficialLinkPokemonSubstruct0SizeMustRemainRetail);
STATIC_ASSERT(sizeof(struct PokemonSubstruct1) == 12, OfficialLinkPokemonSubstruct1SizeMustRemainRetail);
STATIC_ASSERT(sizeof(struct PokemonSubstruct2) == 12, OfficialLinkPokemonSubstruct2SizeMustRemainRetail);
STATIC_ASSERT(sizeof(struct PokemonSubstruct3) == 12, OfficialLinkPokemonSubstruct3SizeMustRemainRetail);
STATIC_ASSERT(sizeof(struct BoxPokemon) == 80, OfficialLinkBoxPokemonSizeMustRemainRetail);
STATIC_ASSERT(sizeof(struct Pokemon) == 100, OfficialLinkPokemonSizeMustRemainRetail);
STATIC_ASSERT(sizeof(struct LinkPlayer) == 0x1C, OfficialLinkPlayerSizeMustRemainRetail);
STATIC_ASSERT(SPECIES_EGG == 412, OfficialLinkSpeciesLayoutMustRemainRetail);
STATIC_ASSERT(NUM_SPECIES == SPECIES_EGG, OfficialLinkSpeciesCountMustRemainRetail);
STATIC_ASSERT(MOVES_COUNT == 355, OfficialLinkMovesCountMustRemainRetail);
STATIC_ASSERT(ITEMS_COUNT == 377, OfficialLinkItemsCountMustRemainRetail);
STATIC_ASSERT(ABILITIES_COUNT == 78, OfficialLinkAbilitiesCountMustRemainRetail);
STATIC_ASSERT(VERSION_RUBY == 2, OfficialLinkRubyVersionIdMustRemainRetail);
STATIC_ASSERT(VERSION_SAPPHIRE == 1, OfficialLinkSapphireVersionIdMustRemainRetail);
STATIC_ASSERT(VERSION_EMERALD == 3, OfficialLinkEmeraldVersionIdMustRemainRetail);
STATIC_ASSERT(VERSION_FIRE_RED == 4, OfficialLinkFireRedVersionIdMustRemainRetail);
STATIC_ASSERT(VERSION_LEAF_GREEN == 5, OfficialLinkLeafGreenVersionIdMustRemainRetail);
STATIC_ASSERT(LINKTYPE_TRADE == 0x1111, OfficialLinkTradeTypeMustRemainRetail);
STATIC_ASSERT(LINKTYPE_BATTLE == 0x2211, OfficialLinkBattleTypeMustRemainRetail);
STATIC_ASSERT(TRAINER_LINK_OPPONENT == 2048, OfficialLinkOpponentTrainerIdMustRemainRetail);
STATIC_ASSERT(TRAINER_UNION_ROOM == 3072, OfficialUnionRoomTrainerIdMustRemainRetail);

static u8 sOfficialLinkCompatibilityBlockReason = OFFICIAL_LINK_COMPAT_NONE;

static void SetOfficialLinkCompatibilityBlockReason(u8 reason)
{
    sOfficialLinkCompatibilityBlockReason = reason;
}

static bool8 IsRetailSafeMoveId(u16 move)
{
    return move < MOVES_COUNT;
}

static bool8 IsRetailSafeItemId(u16 itemId)
{
    return itemId < ITEMS_COUNT;
}

static bool8 IsRetailSafeSpeciesId(u16 species)
{
    return species <= SPECIES_EGG;
}

static bool8 ValidateOfficialLinkMail(const struct Pokemon *mon, u16 heldItem)
{
    struct Pokemon *checkedMon = (struct Pokemon *)mon;
    u8 mailId = GetMonData(checkedMon, MON_DATA_MAIL, NULL);
    const struct Mail *mail;

    if (mailId == MAIL_NONE)
        return !ItemIsMail(heldItem);

    if (mailId >= MAIL_COUNT)
        return FALSE;

    if (!ItemIsMail(heldItem))
        return FALSE;

    mail = &gSaveBlock1Ptr->mail[mailId];
    if (!IsRetailSafeItemId(mail->itemId))
        return FALSE;
    if (!IsRetailSafeSpeciesId(mail->species))
        return FALSE;
    if (mail->itemId != heldItem)
        return FALSE;

    return TRUE;
}

static bool8 ValidateOfficialLinkMonInternal(const struct Pokemon *mon)
{
    struct Pokemon *checkedMon = (struct Pokemon *)mon;
    u16 species = GetMonData(checkedMon, MON_DATA_SPECIES, NULL);
    u16 speciesOrEgg = GetMonData(checkedMon, MON_DATA_SPECIES_OR_EGG, NULL);
    u16 heldItem = GetMonData(checkedMon, MON_DATA_HELD_ITEM, NULL);
    u8 abilityNum = GetMonData(checkedMon, MON_DATA_ABILITY_NUM, NULL);
    u8 ability;
    int i;

    if (speciesOrEgg == SPECIES_NONE)
    {
        SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_UNSUPPORTED_PARTY_STATE);
        return FALSE;
    }

    if (!IsRetailSafeSpeciesId(speciesOrEgg) || !IsRetailSafeSpeciesId(species))
    {
        SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_UNSUPPORTED_MON_DATA);
        return FALSE;
    }

    if (!IsRetailSafeItemId(heldItem))
    {
        SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_UNSUPPORTED_HELD_ITEM);
        return FALSE;
    }

    for (i = 0; i < MAX_MON_MOVES; i++)
    {
        u16 move = GetMonData(checkedMon, MON_DATA_MOVE1 + i, NULL);
        if (!IsRetailSafeMoveId(move))
        {
            SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_UNSUPPORTED_MOVE_OR_ABILITY);
            return FALSE;
        }
    }

    ability = GetAbilityBySpecies(species, abilityNum);
    if (ability >= ABILITIES_COUNT)
    {
        SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_UNSUPPORTED_MOVE_OR_ABILITY);
        return FALSE;
    }

    if (!ValidateOfficialLinkMail(mon, heldItem))
    {
        SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_UNSUPPORTED_MAIL_DATA);
        return FALSE;
    }

    return TRUE;
}

bool8 IsRetailSafePartyForOfficialLink(void)
{
    int i;

    SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_NONE);

    if (gPlayerPartyCount == 0 || gPlayerPartyCount > PARTY_SIZE)
    {
        SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_UNSUPPORTED_PARTY_STATE);
        return FALSE;
    }

    for (i = 0; i < gPlayerPartyCount; i++)
    {
        if (!ValidateOfficialLinkMonInternal(&gPlayerParty[i]))
            return FALSE;
    }

    return TRUE;
}

bool8 IsRetailSafeTradeMon(const struct Pokemon *mon, u16 partnerVersion)
{
    (void)partnerVersion;
    SetOfficialLinkCompatibilityBlockReason(OFFICIAL_LINK_COMPAT_NONE);
    return ValidateOfficialLinkMonInternal(mon);
}

u8 GetOfficialLinkCompatibilityBlockReason(void)
{
    return sOfficialLinkCompatibilityBlockReason;
}

u16 CheckOfficialLinkCompatibility(void)
{
    return IsRetailSafePartyForOfficialLink();
}

void BufferOfficialLinkCompatibilityMessage(void)
{
    static const u8 sUnsupportedMonText[] = _("A POKeMON in your party has data\nthat an official GBA game can't use.\pPlease use a retail-safe party.");
    static const u8 sUnsupportedHeldItemText[] = _("A POKeMON in your party is holding\nan item that an official GBA game\ncan't use.\pPlease use a retail-safe party.");
    static const u8 sUnsupportedMoveOrAbilityText[] = _("A POKeMON in your party knows a\nmove or has an Ability that an\nofficial GBA game can't use.\pPlease use a retail-safe party.");
    static const u8 sUnsupportedMailText[] = _("A POKeMON in your party has MAIL or\nrelated data that an official GBA\ngame can't use.\pPlease use a retail-safe party.");
    static const u8 sUnsupportedPartyStateText[] = _("Your party isn't in a retail-safe\nstate for official link play.\pPlease use a retail-safe party.");

    switch (GetOfficialLinkCompatibilityBlockReason())
    {
    case OFFICIAL_LINK_COMPAT_UNSUPPORTED_MON_DATA:
        StringCopy(gStringVar4, sUnsupportedMonText);
        break;
    case OFFICIAL_LINK_COMPAT_UNSUPPORTED_HELD_ITEM:
        StringCopy(gStringVar4, sUnsupportedHeldItemText);
        break;
    case OFFICIAL_LINK_COMPAT_UNSUPPORTED_MOVE_OR_ABILITY:
        StringCopy(gStringVar4, sUnsupportedMoveOrAbilityText);
        break;
    case OFFICIAL_LINK_COMPAT_UNSUPPORTED_MAIL_DATA:
        StringCopy(gStringVar4, sUnsupportedMailText);
        break;
    case OFFICIAL_LINK_COMPAT_UNSUPPORTED_PARTY_STATE:
    default:
        StringCopy(gStringVar4, sUnsupportedPartyStateText);
        break;
    }
}

bool8 ShouldValidateOfficialLinkForLinkGroup(u8 linkGroup)
{
    switch (linkGroup)
    {
    case LINK_GROUP_SINGLE_BATTLE:
    case LINK_GROUP_DOUBLE_BATTLE:
    case LINK_GROUP_MULTI_BATTLE:
    case LINK_GROUP_TRADE:
    case LINK_GROUP_BATTLE_TOWER:
    case LINK_GROUP_BATTLE_TOWER_OPEN:
        return TRUE;
    default:
        return FALSE;
    }
}
