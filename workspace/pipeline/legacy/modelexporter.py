import time
import os
import tensorflow as tf

def modelexporter(model_dir, output_path,**context):
	train_check_prfx = tf.train.latest_checkpoint(model_dir)
	out_dir = os.path.join(output_path, 'push')
	loaded_graph = tf.Graph()
	with tf.Session(graph=loaded_graph) as sess:
	    loader = tf.train.import_meta_graph(train_check_prfx + '.meta')
	    loader.restore(sess, train_check_prfx)
	    builder = tf.saved_model.builder.SavedModelBuilder(out_dir)
	    builder.add_meta_graph_and_variables(sess,[tf.saved_model.tag_constants.TRAINING],strip_default_attrs=True)
		builder.add_meta_graph([tf.saved_model.tag_constants.SERVING], strip_default_attrs=True)
		builder.save()