from combinewave.chemical_synthesis import synthesis
from pathlib import Path

if __name__ == "__main__":
    chem_synthesis = synthesis.Synthesis(
        reagent_file=Path("user_files/reagent_index.xlsx"))
    print(chem_synthesis.reagent_index)    
    txt = "p-Nitrobenzoic-acid-in-THF (0.15 mol/L, 2 mL); Phenethyl-alcohol (0.2 mmol, 0.024 mL); DEAD (0.4 mmol); Reaction-temperature (25 degree); Reaction-time (12.0 h); Workup (none)."
    chem_synthesis.load_synthesis_plan(Path("user_files/test.txt"))
    chem_synthesis.load_synthesis_plan_from_string(txt)
    chem_synthesis.save_plan(save_file='test_save.txt')
    reagent_name = "dCm"
    res = chem_synthesis.locate_reagent(reagent_name)
    print("DCM is located at ", res)
    chem_synthesis.load_synthesis_plan_excel(Path("user_files/plan-excel.xlsx"))