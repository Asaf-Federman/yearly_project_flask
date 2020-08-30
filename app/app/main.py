from flask import Flask
from .algorithms import asymmetric_eval as asy
from .algorithms import border_eval as border
from .algorithms import size_eval as size
from .algorithms import predictions_extractions as prediction
from .classes.Mole import Mole
from .utils import upload_image as ui
from flask import jsonify, request
from . import pb_inference as inference
from .utils import log
import numpy as np
import numpy.core.multiarray
import cv2
import sys
import jsonpickle

app = Flask(__name__)

@app.route("/")
def hello():
    print ("Hello World", file=sys.stderr)
    return "Hello"

@app.route("/api/analyze", methods=['POST'])
def analyze():
    path = ui.upload_file(request)
    dpi = request.args['dpi']
    # file = request.files['mask']
    log.writeToLogs("Starting to check a new image: "+path)
    inference.init_inference()
    mask = inference.quick_inference(path)
    # separated_masks = prediction.separate_objects_from_mask(mask) TODO: in the future we will separate more than one mask
    separated_masks = utils.cut_roi_from_mask(mask, utils.find_object_coords(mask))
    moles_analyze_results = []
    for index, separated_mask in enumerate(separated_masks):
        # smt = "/files/seperated_masks/"+ file.filename
        # cv2.imwrite(smt, separated_mask)
        bdr = border.border_eval(separated_mask)  
        sz = size.size_eval(separated_mask, int(dpi))
        asymtrc = asy.eval_asymmetric(separated_mask)
        crdint = border.find_all_coordinates(separated_mask)
        moles_analyze_results.append(Mole(asymtrc, sz, bdr, crdint))
    # print (moles_analyze_results[0].toJSON(), file=sys.stderr)
    return jsonify({'results': moles_analyze_results.toJSON()})

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=80)
