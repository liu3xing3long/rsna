from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import re

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_boolean('use_fp16', False, """Use tf.float16 vs tf.float32""")

TOWER_NAME = 'tower'

def variable_on_cpu(name, shape, initializer):
    with tf.device('/cpu:0'):
        dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
        var = tf.get_variable(name, shape, initializer=initializer, dtype=dtype)
    return var

def variable_with_weight_decay(name, shape, stddev, wd=None):
    dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
    var = variable_on_cpu(name, shape, tf.truncated_normal_initializer(stddev=stddev, dtype=dtype))
    if wd is not None:
        weight_decay = tf.multiply(tf.nn.l2_loss(var), wd, name='weight_loss')
        tf.add_to_collection('losses', weight_decay)
    return var

def activation_summary(x):
    tensor_name = re.sub('%s_[0-9]*/' % TOWER_NAME, '', x.op.name)
    tf.summary.histogram(tensor_name + '/activations', x)
    tf.summary.scalar(tensor_name, '/sparsity', tf.nn.zero_fraction(x))

# roughly follow ConvNet layers from VGG-16 with changes from S. Ren et.al. (Faster R-CNN)
# NB: the code is completely un-rolled to make it easy to understand and tweak
def rpn_model(images):
    with tf.variable_scope('conv1') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,3,64], stddev=5e-2)
        conv = tf.nn.conv2d(images, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [64], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv1 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv1)

    with tf.variable_scope('conv2') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,64,64], stddev=5e-2)
        conv = tf.nn.conv2d(conv1, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [64], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv2 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv2)

    max_pool1 = tf.nn.max_pool(conv2,ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME', name='max_pool1')

    with tf.variable_scope('conv3') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,64,128], stddev=5e-2)
        conv = tf.nn.conv2d(max_pool1, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [128], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv3 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv3)

    with tf.variable_scope('conv4') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,128,128], stddev=5e-2)
        conv = tf.nn.conv2d(conv3, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [128], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv4 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv4)

    max_pool2 = tf.nn.max_pool(conv4,ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME', name='max_pool2')

    with tf.variable_scope('conv5') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,128,256], stddev=5e-2)
        conv = tf.nn.conv2d(max_pool2, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [256], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv5 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv5)

    with tf.variable_scope('conv6') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,256,256], stddev=5e-2)
        conv = tf.nn.conv2d(conv5, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [256], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv6 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv6)

    with tf.variable_scope('conv7') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,256,256], stddev=5e-2)
        conv = tf.nn.conv2d(conv6, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [256], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv7 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv7)

    max_pool3 = tf.nn.max_pool(conv7,ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME', name='max_pool3')

    with tf.variable_scope('conv8') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,256,512], stddev=5e-2)
        conv = tf.nn.conv2d(max_pool3, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [512], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv8 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv8)

    with tf.variable_scope('conv9') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,512,512], stddev=5e-2)
        conv = tf.nn.conv2d(conv8, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [512], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv9 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv9)

    with tf.variable_scope('conv10') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,512,512], stddev=5e-2)
        conv = tf.nn.conv2d(conv9, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [512], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv10 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv10)

    max_pool4 = tf.nn.max_pool(conv10,ksize=[1,2,2,1], strides=[1,2,2,1], padding='SAME', name='max_pool4')

    with tf.variable_scope('conv11') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,512,512], stddev=5e-2)
        conv = tf.nn.conv2d(max_pool4, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [512], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv11 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv11)

    with tf.variable_scope('conv12') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,512,512], stddev=5e-2)
        conv = tf.nn.conv2d(conv11, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [512], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv12 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv12)

    with tf.variable_scope('conv13') as scope:
        kernel = variable_with_weight_decay('weights', shape=[3,3,512,512], stddev=5e-2)
        conv = tf.nn.conv2d(conv12, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biasas', [512], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        conv13 = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(conv13)

    # with all 13 convolutional layers VGG-16 complete, now we take Ren's approach for the RPN 
    with tf.variable_scope('ren_conv') as scope:
        kernel = variable_with_weight_decay('weights',shape=[3,3,512,256], stddev=5e-2)
        conv = tf.nn.conv2d(conv13, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biases', [256], tf.constant_initializer(0.0))
        pre_activation = tf.nn.bias_add(conv, biases)
        ren_conv = tf.nn.relu(pre_activation, name=scope.name)
        activation_summary(ren_conv)
    
    # box-regression layer
    with tf.variable_scope('ren_reg') as scope:
        kernel = variable_with_weight_decay('weights', shape=[1,1,256,4], stddev=5e-2)
        conv = tf.nn.conv2d(ren_conv, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biases',[4], tf.constant_initializer(0.0))
        ren_reg = tf.nn.bias_add(conv, biases)

    # box-classification layer
    with tf.variable_scope('ren_cls') as scope:
        kernel = variable_with_weight_decay('weights', shape=[1,1,256,2], stddev=5e-2)
        conv = tf.nn.conv2d(ren_conv, kernel, [1,1,1,1], padding='SAME')
        biases = variable_on_cpu('biases',[4], tf.constant_initializer(0.0))
        ren_cls = tf.nn.bias_add(conv, biases)

    # ren_reg has Ren's reg layer, ren_cls has Ren's cls layer
    return ren_reg, ren_cls