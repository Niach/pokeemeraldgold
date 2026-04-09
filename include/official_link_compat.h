#ifndef GUARD_OFFICIAL_LINK_COMPAT_H
#define GUARD_OFFICIAL_LINK_COMPAT_H

#include "global.h"

enum OfficialLinkCompatibilityBlockReason
{
    OFFICIAL_LINK_COMPAT_NONE,
    OFFICIAL_LINK_COMPAT_UNSUPPORTED_MON_DATA,
    OFFICIAL_LINK_COMPAT_UNSUPPORTED_HELD_ITEM,
    OFFICIAL_LINK_COMPAT_UNSUPPORTED_MOVE_OR_ABILITY,
    OFFICIAL_LINK_COMPAT_UNSUPPORTED_MAIL_DATA,
    OFFICIAL_LINK_COMPAT_UNSUPPORTED_PARTY_STATE,
};

bool8 IsRetailSafePartyForOfficialLink(void);
bool8 IsRetailSafeTradeMon(const struct Pokemon *mon, u16 partnerVersion);
u8 GetOfficialLinkCompatibilityBlockReason(void);

u16 CheckOfficialLinkCompatibility(void);
void BufferOfficialLinkCompatibilityMessage(void);
bool8 ShouldValidateOfficialLinkForLinkGroup(u8 linkGroup);

#endif // GUARD_OFFICIAL_LINK_COMPAT_H
