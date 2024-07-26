import os
import logging

import numpy as np
import svgwrite

import drawing
import lyrics
from rnn import rnn

from flask import Flask, request, jsonify
import os
from tensorflow.python.client import device_lib

app = Flask(__name__)

class Hand(object):

    def __init__(self):
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        self.nn = rnn(
            log_dir='logs',
            checkpoint_dir='checkpoints',
            prediction_dir='predictions',
            learning_rates=[.0001, .00005, .00002],
            batch_sizes=[1024, 2048, 2048],
            patiences=[1500, 1000, 500],
            beta1_decays=[.9, .9, .9],
            validation_batch_size=32,
            optimizer='rms',
            num_training_steps=100000,
            warm_start_init_step=17900,
            regularization_constant=0.0,
            keep_prob=1.0,
            enable_parameter_averaging=False,
            min_steps_to_checkpoint=2000,
            log_interval=20,
            logging_level=logging.CRITICAL,
            grad_clip=10,
            lstm_size=400,
            output_mixture_components=20,
            attention_mixture_components=10
        )
        self.nn.restore()

    def write(self, filename, lines, biases=None, styles=None, stroke_colors=None, stroke_widths=None):
        valid_char_set = set(drawing.alphabet + list("áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ"))
        for line_num, line in enumerate(lines):
            if len(line) > 210:
                raise ValueError(
                    (
                        "Each line must be at most 75 characters. "
                        "Line {} contains {}"
                    ).format(line_num, len(line))
                )

            for char in line:
                if char not in valid_char_set:
                    raise ValueError(
                        (
                            "Invalid character {} detected in line {}. "
                            "Valid character set is {}"
                        ).format(char, line_num, valid_char_set)
                    )

        strokes = self._sample(lines, biases=biases, styles=styles)
        return self._draw(strokes, lines, filename, stroke_colors=stroke_colors, stroke_widths=stroke_widths)
        

    def _sample(self, lines, biases=None, styles=None):
        num_samples = len(lines)
        max_tsteps = 40*max([len(i) for i in lines])
        biases = biases if biases is not None else [0.5]*num_samples

        x_prime = np.zeros([num_samples, 1200, 3])
        x_prime_len = np.zeros([num_samples])
        chars = np.zeros([num_samples, 300])
        chars_len = np.zeros([num_samples])

        if styles is not None:
            for i, (cs, style) in enumerate(zip(lines, styles)):
                x_p = np.load('styles/style-{}-strokes.npy'.format(style))
                c_p = np.load('styles/style-{}-chars.npy'.format(style)).tostring().decode('utf-8')

                c_p = str(c_p) + " " + cs
                c_p = drawing.encode_ascii(c_p)
                c_p = np.array(c_p)

                x_prime[i, :len(x_p), :] = x_p
                x_prime_len[i] = len(x_p)
                chars[i, :len(c_p)] = c_p
                chars_len[i] = len(c_p)

        else:
            for i in range(num_samples):
                encoded = drawing.encode_ascii(lines[i])
                chars[i, :len(encoded)] = encoded
                chars_len[i] = len(encoded)

        [samples] = self.nn.session.run(
            [self.nn.sampled_sequence],
            feed_dict={
                self.nn.prime: styles is not None,
                self.nn.x_prime: x_prime,
                self.nn.x_prime_len: x_prime_len,
                self.nn.num_samples: num_samples,
                self.nn.sample_tsteps: max_tsteps,
                self.nn.c: chars,
                self.nn.c_len: chars_len,
                self.nn.bias: biases
            }
        )
        samples = [sample[~np.all(sample == 0.0, axis=1)] for sample in samples]
        return samples

    def _draw(self, strokes, lines, filename, stroke_colors=None, stroke_widths=None):
        stroke_colors = stroke_colors or ['black']*len(lines)
        stroke_widths = stroke_widths or [2]*len(lines)

        line_height = 60
        view_width = 2000
        view_height = line_height*(len(strokes) + 1)

        dwg = svgwrite.Drawing()
        dwg.viewbox(width=view_width, height=view_height)

        initial_coord = np.array([0, -(3*line_height / 4)])
        for offsets, line, color, width in zip(strokes, lines, stroke_colors, stroke_widths):

            if not line:
                initial_coord[1] -= line_height
                continue

            offsets[:, :2] *= 1.5
            strokes = drawing.offsets_to_coords(offsets)
            strokes = drawing.denoise(strokes)
            strokes[:, :2] = drawing.align(strokes[:, :2])

            strokes[:, 1] *= -1
            strokes[:, :2] -= strokes[:, :2].min() + initial_coord
            strokes[:, 0] += (view_width - strokes[:, 0].max()) / 2

            prev_eos = 1.0
            p = "M{},{} ".format(0, 0)
            for x, y, eos in zip(*strokes.T):
                p += '{}{},{} '.format('M' if prev_eos == 1.0 else 'L', x, y)
                prev_eos = eos
            path = svgwrite.path.Path(p)
            path = path.stroke(color=color, width=width, linecap='round').fill("none")
            dwg.add(path)

            initial_coord[1] -= line_height

        return dwg.tostring()



hand = Hand()

@app.route('/generate', methods=['POST'])
def generate_svg():
    data = request.json
    print(data)
    if not data or 'lines' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    lines = data['lines']
    biases = data.get('biases', [.75 for _ in lines])
    styles = data.get('styles', [9 for _ in lines])
    stroke_colors = data.get('stroke_colors', ['black' for _ in lines])
    stroke_widths = data.get('stroke_widths', [1 for _ in lines])

    # Initialize Hand object

    # Generate SVG
    out = hand.write(
        filename=None,
        lines=lines,
        biases=biases,
        styles=styles,
        stroke_colors=stroke_colors,
        stroke_widths=stroke_widths
    )

    # Return the path or URL to the generated SVG
    return jsonify({'message': 'SVG generated successfully', 'path': out})
@app.route('/g-code', methods=['POST'])
def generate_gcode():
    data = request.json
    print(data)
    if not data or 'lines' not in data:
        return jsonify({'error': 'Missing required parameters'}), 400

    lines = data['lines']
    biases = data.get('biases', [.75 for _ in lines])
    styles = data.get('styles', [9 for _ in lines])
    stroke_colors = data.get('stroke_colors', ['black' for _ in lines])
    stroke_widths = data.get('stroke_widths', [1 for _ in lines])

    # Initialize Hand object

    # Generate SVG
    out = hand.write(
        filename=None,
        lines=lines,
        biases=biases,
        styles=styles,
        stroke_colors=stroke_colors,
        stroke_widths=stroke_widths
    )

    # Return the path or URL to the generated SVG
    return jsonify({'message': 'SVG generated successfully', 'path': out})

if __name__ == '__main__':
    if not os.path.exists('generated_svg'):
        os.makedirs('generated_svg')

    def get_available_gpus():
        local_device_protos = device_lib.list_local_devices()
        print(local_device_protos)
        return [x.name for x in local_device_protos if x.device_type == 'GPU']
    print(get_available_gpus())
    app.run(debug=True, host='0.0.0.0', port=5000)