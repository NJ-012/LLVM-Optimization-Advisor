import re, shutil, subprocess
from pathlib import Path
from .config import ROOT,RESULTS,FEATURES

def clang_path(): return shutil.which("clang")
def run(cmd,timeout=60):
    p=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,timeout=timeout)
    if p.returncode: raise RuntimeError(f"Command failed: {' '.join(map(str,cmd))}\n{p.stderr}")
    return p.stdout,p.stderr
def extract(source:Path):
    clang=clang_path()
    if not clang: raise RuntimeError("clang not found. Install LLVM/Clang and ensure clang is on PATH.")
    ir=RESULTS/(source.stem+"_features.ll")
    run([clang,"-S","-emit-llvm","-O0",source,"-o",ir])
    text=ir.read_text(errors="replace")
    lines=text.splitlines()
    inst=[x for x in lines if x.strip() and not x.lstrip().startswith((";","define ","declare ","attributes ","!","source_filename","target ")) and not x.strip().endswith(":") and x.strip() not in ("{","}")]
    loops=len(re.findall(r'\bfor\s*\(|\bwhile\s*\(|\bdo\s*\{',source.read_text(errors="replace")))
    src=source.read_text(errors="replace")
    vals={
      "ir_instruction_count":len(inst),
      "ir_basic_block_count":len(re.findall(r'^[-A-Za-z$._0-9]+:\s*(?:;.*)?$',text,re.M)),
      "ir_function_count":len(re.findall(r'^\s*define\b',text,re.M)),
      "ir_branch_count":len(re.findall(r'\bbr\b',text)),
      "ir_cond_branch_count":len(re.findall(r'\bbr\s+i1\b',text)),
      "ir_load_count":len(re.findall(r'\bload\b',text)),
      "ir_store_count":len(re.findall(r'\bstore\b',text)),
      "ir_call_count":len(re.findall(r'\bcall\b|\binvoke\b',text)),
      "ir_integer_ops":len(re.findall(r'\b(add|sub|mul|sdiv|udiv|srem|urem|shl|lshr|ashr|and|or|xor)\b',text)),
      "ir_float_ops":len(re.findall(r'\b(fadd|fsub|fmul|fdiv|frem)\b',text)),
      "source_loop_count":loops,
      "source_nested_loop_hint":int(bool(re.search(r'for\s*\([^\n]*\)[^{]*\{[\s\S]{0,300}for\s*\(',src))),
      "source_array_refs":len(re.findall(r'\b[A-Za-z_]\w*\s*\[[^]]+\]',src)),
      "source_branch_count":len(re.findall(r'\b(if|switch|case)\b',src)),
      "source_line_count":len(src.splitlines()),
    }
    return vals
