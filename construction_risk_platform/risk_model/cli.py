import argparse,json,cv2
from .pipeline import RiskPipeline
def main():
 p=argparse.ArgumentParser(); p.add_argument('--weights'); p.add_argument('--image'); p.add_argument('--video'); p.add_argument('--camera',action='store_true'); p.add_argument('--save'); a=p.parse_args(); pipe=RiskPipeline(a.weights)
 if a.image:
  im=cv2.imread(a.image)
  if im is None: raise FileNotFoundError(a.image)
  risk,ann=pipe.analyze_image(im,a.image); print(json.dumps(risk.to_dict(),indent=2)); cv2.imwrite(a.save or 'risk_output.jpg',ann); return
 src=0 if a.camera else a.video
 if src is None: p.error('Use --image, --video, or --camera')
 pipe.analyze_video(src,True,a.save)
if __name__=='__main__': main()
