# 
# This simple app extracts the training images from the .dcm files. See the README.md
# for more details.
#

import tensorflow as tf
from labelrecord import LabelRecord

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('positives_dir','positives',"""Directory for the positive image regions""")
tf.app.flags.DEFINE_string('negatives_dir','negatives',"""Directory for the negative image regions""")
tf.app.flags.DEFINE_string('label_file','../input/stage_1_train_labels.csv',"""Path to labels .csv file""")
tf.app.flags.DEFINE_string('image_path','../input/stage_1_train_images',"""Root directory for the .dcm files containing the train CXRs""")

def _init_output_directories():
    if tf.gfile.Exists(FLAGS.positives_dir):
        tf.gfile.DeleteRecursively(FLAGS.positives_dir)
    tf.gfile.MakeDirs(FLAGS.positives_dir)

    if tf.gfile.Exists(FLAGS.negatives_dir):
        tf.gfile.DeleteRecursively(FLAGS.negatives_dir)
    tf.gfile.MakeDirs(FLAGS.negatives_dir)

# returns collection of all bounding boxes
def _get_bounding_boxes(records):
    return [box for (_,v) in records.items() for box in v.boundingBoxes if v.hasBoundingBox]

# main entry point
def main(argv=None):
    _init_output_directories()

    print('loading labels from %s' % FLAGS.label_file)
    lr = LabelRecord()
    label_records = lr.load(FLAGS.label_file)
    cnt = 0
    for (_,v) in label_records.items():
        if v.hasBoundingBox:
            cnt = cnt + 1
    print('%d records have bounding boxes' % cnt)

    bb = _get_bounding_boxes(label_records)
    print('found %d bounding boxes' % len(bb))

if __name__ == '__main__':
    tf.app.run()
    