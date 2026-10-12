from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BENCH=ROOT/"benchmarks"; DATA=ROOT/"data"; MODELS=ROOT/"models"; RESULTS=ROOT/"results"
EXPERIMENTS=DATA/"experiments.csv"; FEEDBACK=DATA/"feedback.csv"; FEEDBACK_QUARANTINE=DATA/"feedback.quarantine.csv"; MODEL=MODELS/"reward_model.joblib"
# These are compiler configurations, not four isolated transformation passes.
CONFIGS={
 "O3":["-O3"],
 "O2":["-O2"],
 "O3_no_vectorize":["-O3","-fno-vectorize","-fno-slp-vectorize"],
 "O3_no_unroll":["-O3","-fno-unroll-loops"],
}
FEATURES=["ir_instruction_count","ir_basic_block_count","ir_function_count","ir_branch_count","ir_cond_branch_count","ir_load_count","ir_store_count","ir_call_count","ir_integer_ops","ir_float_ops","source_loop_count","source_nested_loop_hint","source_array_refs","source_branch_count","source_line_count"]
for d in [DATA,MODELS,RESULTS]: d.mkdir(parents=True,exist_ok=True)
