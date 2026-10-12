import hashlib, joblib, numpy as np, pandas as pd
import pickle
from pathlib import Path
import os
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
try:
    from xgboost import XGBRegressor
    from xgboost.core import XGBoostError
except ImportError:
    XGBRegressor = None
    XGBoostError = RuntimeError
from .config import EXPERIMENTS,MODEL,FEATURES,CONFIGS,FEEDBACK
from .data_validation import parse_correctness, validate_measurements
from .recommendation import choose_action, use_safe_fallback

def action_frame(df):
 x=df[FEATURES].copy()
 for c in CONFIGS: x["action_"+c]=(df["configuration"]==c).astype(int)
 return x
def training_data_signature(df):
 columns=["program_id","configuration","speedup_vs_o3",*FEATURES]
 valid=df[df.correctness.map(parse_correctness).eq(True)].copy()
 speedups=pd.to_numeric(valid.speedup_vs_o3,errors="coerce")
 valid=valid[np.isfinite(speedups)&speedups.gt(0)]
 values=valid[columns].sort_values(columns,kind="stable")
 return hashlib.sha256(values.to_csv(index=False,float_format="%.17g").encode("utf-8")).hexdigest()
def _new_model(cross_validation=False):
 if XGBRegressor is not None:
  return XGBRegressor(n_estimators=120 if cross_validation else 180,max_depth=3,learning_rate=0.05,subsample=0.9,colsample_bytree=0.9,objective="reg:squarederror",n_jobs=2,random_state=42)
 return RandomForestRegressor(n_estimators=150 if cross_validation else 250,min_samples_leaf=1,random_state=42)
def _grouped_splits(df,n_splits=None):
 program_count=df.program_id.nunique()
 folds=min(5,program_count) if n_splits is None else n_splits
 if folds<2:
  return []
 return list(GroupKFold(n_splits=folds).split(df,groups=df.program_id))
def _grouped_cv_report(X,y,df):
 splits=_grouped_splits(df)
 if not splits:
  raise ValueError("At least two distinct programs are required for grouped CV.")
 model_predictions=np.full(len(df),np.nan); median_predictions=np.full(len(df),np.nan)
 predicted_best=[]; measured_best=[]
 for train_index,test_index in splits:
  fold_model=_new_model(cross_validation=True); fold_model.fit(X.iloc[train_index],y.iloc[train_index])
  model_predictions[test_index]=fold_model.predict(X.iloc[test_index])
  median_predictions[test_index]=float(np.median(y.iloc[train_index]))
  held=df.iloc[test_index].copy(); held["_prediction"]=model_predictions[test_index]
  for _,rows in held.groupby("program_id",sort=False):
   predicted_best.append(rows.loc[rows["_prediction"].idxmax(),"configuration"])
   measured_best.append(rows.loc[rows["speedup_vs_o3"].astype(float).idxmax(),"configuration"])
 return {
  "group_cv_log_speedup_mae":float(np.mean(np.abs(model_predictions-y.to_numpy()))),
  "group_cv_median_baseline_log_speedup_mae":float(np.mean(np.abs(median_predictions-y.to_numpy()))),
  "group_cv_top1_accuracy":float(np.mean(np.asarray(predicted_best)==np.asarray(measured_best))),
  "group_cv_o3_policy_top1_accuracy":float(np.mean(np.asarray(measured_best)=="O3")),
  "group_cv_folds":len(splits),
  "group_cv_programs":int(df.program_id.nunique()),
  "group_cv_observations":int(len(df)),
 }
def _clean_measurements(df):
 valid=df[df.correctness.map(parse_correctness).eq(True)].copy()
 speedups=pd.to_numeric(valid.speedup_vs_o3,errors="coerce")
 return valid[np.isfinite(speedups)&speedups.gt(0)].copy()
def evaluate_frame(frame):
 df=_clean_measurements(frame)
 if df.empty:
  raise ValueError("No correct, positively labeled observations are available.")
 if df.program_id.nunique()<4:
  return {"programs":int(df.program_id.nunique()),"observations":len(df),"folds":0}
 X=action_frame(df); y=np.log(pd.to_numeric(df.speedup_vs_o3,errors="raise"))
 report=_grouped_cv_report(X,y,df)
 report["group_cv_model_family"]=type(_new_model(cross_validation=True)).__name__
 return {
  "programs":int(df.program_id.nunique()),
  "observations":int(len(df)),
  "folds":report["group_cv_folds"],
  **report,
 }
def train():
 if not EXPERIMENTS.exists(): raise RuntimeError("No dataset. Run `python run.py collect` first.")
 df=pd.read_csv(EXPERIMENTS)
 errors=validate_measurements(df,"experiments")
 if errors: raise RuntimeError("Invalid experiment data:\n"+"\n".join(errors[:20]))
 df=_clean_measurements(df)
 if df.program_id.nunique()<3: raise RuntimeError("Need at least three distinct benchmark programs to train.")
 X=action_frame(df); y=np.log(df.speedup_vs_o3.astype(float))
 model=_new_model()
 model.fit(X,y)
 n=df.program_id.nunique()
 cv_report=_grouped_cv_report(X,y,df) if n>=4 else {}
 joblib.dump({"model_version":1,"model":model,"features":FEATURES,"configs":list(CONFIGS),"trained_rows":len(df),"programs":sorted(df.program_id.unique().tolist()),"training_data_signature":training_data_signature(df),**cv_report},MODEL)
 print(f"Trained {type(model).__name__} reward model on {len(df)} measured rows across {n} programs.")
 if cv_report:
  print(
   f"Grouped evaluation programs: {cv_report['group_cv_programs']}; "
   f"observations: {cv_report['group_cv_observations']}; "
   f"folds: {cv_report['group_cv_folds']}."
  )
  print(f"Model family: {type(_new_model(cross_validation=True)).__name__}")
  print(f"Program-grouped CV MAE (log speedup): {cv_report['group_cv_log_speedup_mae']:.4f}")
  print(f"Grouped median baseline MAE (log speedup): {cv_report['group_cv_median_baseline_log_speedup_mae']:.4f}")
  print(f"Grouped top-1 configuration accuracy: {cv_report['group_cv_top1_accuracy']:.3f}")
  print(f"O3 policy top-1 accuracy: {cv_report['group_cv_o3_policy_top1_accuracy']:.3f}")
  if cv_report["group_cv_log_speedup_mae"]>=cv_report["group_cv_median_baseline_log_speedup_mae"]:
   print("Warning: grouped CV did not outperform the median baseline; treat recommendations as uncertain.")
 print("This small program set provides exploratory grouped CV, not a claim of generalization.")
 return joblib.load(MODEL)
def load():
 model_path=Path(os.environ.get("ADVISOR_MODEL_PATH",str(MODEL))).expanduser()
 if not model_path.exists(): raise RuntimeError("Model missing. Run `python run.py train` or configure ADVISOR_MODEL_PATH.")
 try: bundle=joblib.load(model_path)
 except (OSError,EOFError,ValueError,KeyError,ImportError,AttributeError,pickle.UnpicklingError,XGBoostError) as exc:
  raise RuntimeError(f"Could not load trusted model artifact {model_path.name}: {exc}") from exc
 if not isinstance(bundle,dict) or "model" not in bundle or "features" not in bundle:
  raise RuntimeError(f"Invalid model bundle: {model_path.name} lacks model/schema metadata.")
 if list(bundle["features"])!=list(FEATURES):
  raise RuntimeError("Model feature schema does not match the current inference feature schema.")
 if "configs" in bundle and list(bundle["configs"])!=list(CONFIGS):
  raise RuntimeError("Model configuration schema does not match configured actions.")
 return bundle
def predict_action(program_id,features,bundle=None):
 b=load() if bundle is None else bundle; model=b["model"]; rows=[]
 for c in CONFIGS:
  row=dict(features)
  for a in CONFIGS: row["action_"+a]=int(a==c)
  rows.append(row)
 X=pd.DataFrame(rows)[b["features"]+["action_"+c for c in CONFIGS]]
 rewards=model.predict(X); predictions={c:float(np.exp(r)) for c,r in zip(CONFIGS,rewards)}
 predictions["O3"]=1.0
 return choose_action(predictions,b),predictions
