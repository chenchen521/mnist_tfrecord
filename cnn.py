# -*- coding: utf-8 -*-
"""
Created on Thu Aug 30 14:47:06 2018

@author: todd
"""
# -*- coding: utf-8 -*-
import tensorflow as tf

def read_image(file_queue):
    
    reader = tf.TFRecordReader()
    key, value = reader.read(file_queue)
    print ('1',value.shape)
    
    _, serialized_example = reader.read(file_queue)
    print('2',serialized_example.shape)
    
    features = tf.parse_single_example(
        serialized_example,
        features={
          'image_raw': tf.FixedLenFeature([], tf.string),
          'label': tf.FixedLenFeature([], tf.int64),
          })

    image = tf.decode_raw(features['image_raw'], tf.uint8)
    print ('3',image.shape)
    
    image.set_shape([784])   #(784,)
    print('4',image.shape)
    
    image = tf.cast(image, tf.float32) * (1. / 255) - 0.5
    label = tf.cast(features['label'], tf.int32)
    print('5',label.shape)
    
    return image, label

def read_image_batch(file_queue, batch_size):
    img, label = read_image(file_queue)
    capacity = 3 * batch_size
    image_batch, label_batch = tf.train.batch([img, label], batch_size=batch_size, capacity=capacity, num_threads=10)
    print('6',image_batch.shape)   #(17, 784)
    print('7',label_batch.shape)   #(17,)
    
    one_hot_labels = tf.to_float(tf.one_hot(label_batch, 10, 1, 0))  #(17,10)
    print('8',one_hot_labels.shape) 
    
    return image_batch, one_hot_labels

def main(_):

    train_file_path = 'D:/minist/train.tfrecords'
    test_file_path = 'D:/minist/test.tfrecords'
    ckpt_path = 'D:/minist/model.ckpt'

    train_image_filename_queue = tf.train.string_input_producer(
            [train_file_path])
    train_images, train_labels = read_image_batch(train_image_filename_queue, 17) #(17,784)  (17,10)

    test_image_filename_queue = tf.train.string_input_producer(
            [test_file_path])
    test_images, test_labels = read_image_batch(test_image_filename_queue, 17)  #(17,784)  (17,10)


    W = tf.Variable(tf.zeros([784, 10]))  #（784，10）
    b = tf.Variable(tf.zeros([10]))      #(10,)

    x = tf.reshape(train_images, [-1, 784])  #(17, 784)
    print('x', x.shape)
    
    y = tf.matmul(x, W) + b  #（17，784）    #(17,10)
    print('y', y.shape)
    
    y_ = tf.to_float(train_labels)    #(17,10)
    print('y_',y_.shape)
    
    print('tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y)',tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y).shape)  #(17,)
    cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
    print('cross_entropy',cross_entropy.shape)
    
    train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)

    x_test = tf.reshape(test_images, [-1, 784])
    y_pred = tf.matmul(x_test, W) + b
    y_test = tf.to_float(test_labels)

    correct_prediction = tf.equal(tf.argmax(y_pred, 1), tf.argmax(y_test, 1))
    print('correct_prediction',correct_prediction.shape)  #(17,)

    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    
    saver = tf.train.Saver()

    sess = tf.InteractiveSession()
    tf.global_variables_initializer().run()

    # start queue runner
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    # Train and Test 
    for i in range(20):
        sess.run(train_step)
        print("step:", i + 1, "accuracy:", sess.run(accuracy))

    save_path = saver.save(sess, ckpt_path)
    print("Model saved in file: %s" % save_path)

    # stop queue runner
    coord.request_stop()
    coord.join(threads)

if __name__ == '__main__':
    tf.app.run(main=main)