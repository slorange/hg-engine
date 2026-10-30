#include "config.h"
#include "pokemon.h"
#include "wild_encounter_finalize.h"
#include "wild_level_caps.h"

#ifdef IMPLEMENT_ECOLOGY_GENERATION
#include "ecology/ecology_encounter.h"
#endif

extern u32 space_for_setmondata;

u16 WildEncounterFinalize(struct PartyPokemon *pp, u16 vanillaTableSpecies)
{
    u16 species;

    if (pp == NULL) {
        return vanillaTableSpecies;
    }

#ifdef IMPLEMENT_ECOLOGY_GENERATION
    species = EcologyApplyGrassSpeciesOverride(vanillaTableSpecies);
#else
    species = vanillaTableSpecies;
#endif

    SetMonData(pp, MON_DATA_SPECIES, &species);
    SetMonData(pp, MON_DATA_FORM, (u8 *)&space_for_setmondata);

    UpdatePassiveForms(pp);
    ApplyWildDistanceLevelCapToMon(pp);

    ResetPartyPokemonAbility(pp);
    InitBoxMonMoveset(&pp->box);

    return (u16)(GetMonData(pp, MON_DATA_SPECIES, NULL) & 0x07FF);
}
