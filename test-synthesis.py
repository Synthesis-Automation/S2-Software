from chem_robox.chemical_synthesis import synthesis
from pathlib import Path

if __name__ == "__main__":
    chem_synthesis = synthesis.Synthesis(
        reagent_file=Path("user_files/reagent_index.xlsx"))
    chem_synthesis.load_reagent_index(Path("user_files/reagent_index.xlsx"))
    txt = "Pd(OAc)2 (0.15 mol/L, 2 mL); Phenethyl-alcohol (0.2 mmol, 0.024 mL); DEAD (0.4 mmol); Reaction-temperature (25 degree); Reaction-time (12.0 h); Workup (none)."
    chem_synthesis.load_synthesis_plan(Path("user_files/amination.txt"))
    # # chem_synthesis.load_synthesis_plan_from_string(txt)
    # chem_synthesis.save_plan(save_file='test_save.txt')
    # reagent_name = "7732-18-5"
    # res = chem_synthesis.locate_reagent(reagent_name)
    # print("Water is located at ", res)
    reagent_name = "liquid1"
    res = chem_synthesis.locate_reagent(reagent_name)
    print("liquid1 is located at ", res)
    # chem_synthesis.load_synthesis_plan_excel(Path("user_files/plan-excel.xlsx"))
    chem_synthesis.parse_plan_to_json()
    # print(chem_synthesis.synthesis_plan_json)
    plan = chem_synthesis.convert_plan_to_saver_mode()
    print(plan["first"])
    print(len(plan["first"]))
    print()
    print(plan["main"])
    print()
    print(plan["last"])
    # print(chem_synthesis.reagent_index)
