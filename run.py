import argparse
from src.pipeline import (
    collect,
    doctor,
    evaluate,
    feedback,
    incorporate_feedback,
    quarantine_feedback,
    recommend,
    run_all,
    show_dataset,
    train,
)
from src.validation import validate_release

def main():
    p=argparse.ArgumentParser(description="ML-guided LLVM optimization with runtime feedback")
    sub=p.add_subparsers(dest="cmd",required=True)
    for name in ["doctor","collect","train","evaluate","all","dataset","incorporate-feedback","quarantine-feedback","validate"]: sub.add_parser(name)
    for name in ["recommend","feedback"]:
        q=sub.add_parser(name); q.add_argument("--benchmark",default="matrix_multiply")
    a=p.parse_args()
    funcs={
        "doctor":doctor,
        "collect":collect,
        "train":train,
        "evaluate":evaluate,
        "all":run_all,
        "dataset":show_dataset,
        "incorporate-feedback":incorporate_feedback,
        "quarantine-feedback":quarantine_feedback,
        "recommend":lambda:recommend(a.benchmark),
        "feedback":lambda:feedback(a.benchmark),
    }
    if a.cmd=="validate":
        if not validate_release(): raise SystemExit(1)
        return
    if funcs[a.cmd]() is not True:
        raise SystemExit(1)
if __name__=="__main__": main()
