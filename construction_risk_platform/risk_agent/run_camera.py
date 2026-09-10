import argparse
from .agent import ConstructionRiskAgent
def main():
 p=argparse.ArgumentParser(); p.add_argument('--weights'); p.add_argument('--source',default='0'); p.add_argument('--save'); a=p.parse_args(); src=0 if a.source=='0' else a.source; ConstructionRiskAgent(a.weights).monitor(src,a.save)
if __name__=='__main__': main()
