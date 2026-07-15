#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from suica_sim.adversarial_closure import run_adversarial_closure,write_adversarial_report
def main():
    p=argparse.ArgumentParser();p.add_argument("--profile",choices=("quick","full"),default="quick");p.add_argument("--output-dir",default="results/v6_adversarial_closure");a=p.parse_args()
    cp=ROOT/f"configs/sim_v6/adversarial_{a.profile}.json";raw=cp.read_bytes();cfg=json.loads(raw)
    result=run_adversarial_closure(cfg,hashlib.sha256(raw).hexdigest());out=write_adversarial_report(result,ROOT/a.output_dir)
    print(json.dumps({"gates":result["gates"],"output":str(out)},indent=2))
if __name__=="__main__":main()
