import os
import random
import io
import pandas as pd
import tensorflow as tf
import glob
import operator
import shutil
import tensorflow as tf

from google.protobuf import text_format
from object_detection import exporter
from object_detection.protos import pipeline_pb2
from tensorboard import program
from tensorboard import main as tb
from distutils.dir_util import copy_tree
from PIL import Image
from object_detection.utils import dataset_util
from collections import namedtuple, OrderedDict
from object_detection import model_hparams
from object_detection import model_lib

#aireflow dep
import logging
import datetime
import airflow
from airflow import DAG
from datetime import timedelta
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

############## SETTINGS ##################
output_path = '/tensorflow/workspace/pipeline/configs'  # the path where ex. the tfrecord files should be saved to
image_dir = '/tensorflow/workspace/gateway/public/data'  # path of the imges
csv_input = '/tensorflow/workspace/gateway/public/config/annotations.csv'  # path of the annotations.csv
tf_serving_model_path = '/tensorflow/workspace/serving/saved_models'  # path to the saved model from tf serving
pipeline_config_path = '/tensorflow/workspace/pipeline/configs/pipeline.config'  # the path to the pipeline config file of the DL model.
model_dir = '/tensorflow/workspace/pipeline/configs/training/'  # traingin output dir
num_train_steps = 60000
##########################################

args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(1), # set the start_date and end_date the same date to disable schedule
    'end_date': None,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    dag_id='main',
    default_args=args,
    schedule_interval=None
)

def class_text_to_int(row_label):
    """
    this function represents the label map
    :param row_label:
    :return: the id of the label/class
    """
    if row_label == 'type':  # 'class 1':
        return 1
    elif row_label == 'identification':  # 'class 2':
        return 2
    elif row_label == 'customer':  # 'class 3':
        return 3
    elif row_label == 'content':  # 'class 4':
        return 4
    elif row_label == 'header':  # 'class 5':
        return 5
    else: # 'all the other classes':
        None
def split(df, group):
    """
    this function splits the dataset
    """
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]
def create_tf_example(group, path):
    """
    this function creats the tensors for the tfrecord
    :param group: row of the csv file
    :param path: path to the imges
    :return: converted dataset
    """
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size
    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []
    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example
def create_pipeline():
    reset(output_path, image_dir, csv_input, tf_serving_model_path)
    data(output_path, image_dir, csv_input)
    preprocessmodel(tf_serving_model_path, output_path)
    monitor(model_dir)
    train(pipeline_config_path, model_dir, num_train_steps)
    modelexporter(pipeline_config_path, model_dir, output_path)
    modelmover(output_path)
    trainmover(model_dir,output_path)
    pusher(output_path,tf_serving_model_path)
    clean(image_dir,csv_input)
    reset(output_path, image_dir, csv_input, tf_serving_model_path)
def data(output_path, image_dir, csv_input, **context):
    """
    Generates the eval and train tfrecord.

    :param output_path: the path where the tfrecord files should be saved too
    :param image_dir: the path of the images for the tfrecord files
    :param csv_input: the path of the annotations.csv
    :return:
    """
    train_writer = tf.python_io.TFRecordWriter(output_path + '/train.record')
    eval_writer = tf.python_io.TFRecordWriter(output_path + '/eval.record')
    path = os.path.join(os.getcwd(), image_dir)
    examples = pd.read_csv(csv_input)
    #count_files = len(os.listdir(image_dir))
    included_extensions = ['jpg','jpeg', 'bmp', 'png', 'gif']
    file_names = [fn for fn in os.listdir(image_dir)
                if any(fn.endswith(ext) for ext in included_extensions)]
    count_files = len(file_names)
    eval_file_list = shaffelfiles(image_dir, int(count_files * 0.2)) # here we define the split size normaly 80:20(train:eval) -> 0.2 -> 20% eval dataset
    grouped = split(examples, 'filename')
    for group in grouped:
        if not group.filename in str(eval_file_list):
            tf_example = create_tf_example(group, path)
            train_writer.write(tf_example.SerializeToString())
        else:
            tf_example = create_tf_example(group, path)
            eval_writer.write(tf_example.SerializeToString())
    train_writer.close()
    eval_writer.close()
    logging.info('successfully created the TFRecord: ' + output_path + '/train.record' + ';' + output_path + '/eval.record')
def preprocessmodel(tf_serving_model_path, output_path,**context):
    """
    The funciton is making a copy of the current used model to the
    :param tf_serving_model_path:
    :param output_path:
    :return:
    """
    tmpDir = findlatestdir(tf_serving_model_path)
    logging.info('found latest model:'+ tmpDir)
    mkdir(output_path + '/model/')
    copy_tree(tmpDir, output_path + '/model/')
    logging.info('preprocess: '+str(copy_tree(tmpDir, output_path + '/model/')))
def train(pipeline_config_path, model_dir, num_train_steps,**context):
    """
    This method is responsible for the training process of a new model.

    :param pipeline_config_path: the path where the pipeline config file of the DL model is
    :param model_dir: the path where the training output should be saved too! also this path is later used for the tensorboard
    :param num_train_steps: the int numer of steps untell when the trainer should train the model
    :return: the new trained model
    """
    hparams_overrides = None
    sample_1_of_n_eval_examples = 1 #numer of eval threads if 0 then no evaluation of the current training, if 1 then eval.
    sample_1_of_n_eval_on_train_examples = 5
    checkpoint_dir = None
    eval_training_data = False
    run_once = False
    tf.logging.set_verbosity(tf.logging.INFO) # show the current global steps in the cli
    config = tf.estimator.RunConfig(model_dir=model_dir)#,log_step_count_steps=1) # show every step in the cli
    train_and_eval_dict = model_lib.create_estimator_and_inputs(run_config=config, hparams=model_hparams.create_hparams(hparams_overrides), pipeline_config_path=pipeline_config_path, train_steps=num_train_steps, sample_1_of_n_eval_examples=sample_1_of_n_eval_examples, sample_1_of_n_eval_on_train_examples=(sample_1_of_n_eval_on_train_examples))
    estimator = train_and_eval_dict['estimator']
    train_input_fn = train_and_eval_dict['train_input_fn']
    eval_input_fns = train_and_eval_dict['eval_input_fns']
    eval_on_train_input_fn = train_and_eval_dict['eval_on_train_input_fn']
    predict_input_fn = train_and_eval_dict['predict_input_fn']
    train_steps = train_and_eval_dict['train_steps']
    if checkpoint_dir:
        if eval_training_data:
            name = 'training_data'
            input_fn = eval_on_train_input_fn
        else:
            name = 'validation_data'
            # The first eval input will be evaluated.
            # input_fn = eval_input_fns[0]
        if run_once:
            estimator.evaluate(input_fn, steps=None, checkpoint_path=tf.train.latest_checkpoint(checkpoint_dir))
        else:
            model_lib.continuous_eval(estimator, checkpoint_dir, input_fn, train_steps, name)
    else:
        train_spec, eval_specs = model_lib.create_train_and_eval_specs(train_input_fn, eval_input_fns, eval_on_train_input_fn, predict_input_fn, train_steps, eval_on_train_data=False)
    # Currently only a single Eval Spec is allowed.
    tf.estimator.train_and_evaluate(estimator, train_spec, eval_specs[0])
    logging.info('successfully trained new model')
def monitor(model_dir,**context):
    """
    this function creats a new thread and inside starts the TensorBoard with the directory
    of progress of the trainging job of the new model.
    :param model_dir: the path of the new model training
    :return: # http requests coming in on the defined port
    """
    logging.info('start TensorBoard on port: 6006')
    tb = program.TensorBoard()
    tb.configure(argv=[None, '--logdir', model_dir, '--port', str(6006)])
    url = tb.launch()
    logging.info(url)
def modelexporter(pipeline_config_path, model_dir, output_path,**context):
    """
    this function is exporting the inference_graph of the new model into the "push" folder.

    :param pipeline_config_path: path of the pipeline config file of the model
    :param model_dir: path of the model
    :param output_path: path where the training is saved to
    :return:
    """
    try:
        trained_checkpoint_prefix = tf.train.latest_checkpoint(model_dir) # the path of the last checkpoint ex. /tensorflow/workspace/pipeline/configs/training/model.ckpt-334
        input_type='image_tensor'
        config_override = ''
        input_shape = None
        write_inference_graph = False
        output_directory = os.path.join(output_path, 'push')
        pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
        with tf.gfile.GFile(pipeline_config_path, 'r') as f:
            text_format.Merge(f.read(), pipeline_config)
        text_format.Merge(config_override, pipeline_config)
        exporter.export_inference_graph(input_type, pipeline_config, trained_checkpoint_prefix,output_directory, input_shape=input_shape, write_inference_graph=write_inference_graph)
    except Exception as e:
        logging.info('export of new model failed!' +str(e))
def trainmover(model_dir, output_path,**context):
    shutil.copytree(model_dir,os.path.join(output_path, 'push', 'training'))
def pusher(output_path,tf_serving_model_path,**context):
    try:
        src = os.path.join(output_path, 'push')
        version = newversion(tf_serving_model_path)
        des = os.path.join(tf_serving_model_path, str(version))
        shutil.copytree(src,des)
        shutil.rmtree(src)
    except Exception as e:
        logging.info('push of new model failed!' +str(e))
def clean(image_dir,csv_input,**context):
    try:
        rmdir(image_dir)
        rmfile(csv_input)
    except Exception as e:
        logging.info('clean of image data and annotation.csv failed!' +str(e))
"""
The following function are helpers
"""
def newversion(tf_serving_model_path):
    try:
        directory = findlatestdir(tf_serving_model_path) # get the path of the latest model from tf_serving
        lastStringOfPath = os.path.basename(os.path.normpath(directory)) # string of the last element of the path to the tf serving model
        currentVersion = int(lastStringOfPath) # last name of path is a number therefore we can convert it to an Integer
        newVersion = currentVersion + 1 # the next version should be a +1 higher then the last one.
        return newVersion
    except Exception as e:
        logging.info('find new model version failed!' + str(e))
def modelmover(output_path,**context):
    """
    this function just moves the dir "variables" and the file "saved_model.pb" in the "push"
    folder one level higher. This is neccesery for the tf_serving instance to find the current model.
    :return:
    """
    try:
        output_directory = os.path.join(output_path,'push/')
        des = os.path.join(output_directory, 'saved_model/')
        for name in os.listdir(des):
            if os.path.isdir(name):
                logging.info('moved: '+name)
                shutil.copytree(des+name, output_directory)
                shutil.rmtree(des+name)
            else:
                logging.info('moved: '+name)
                shutil.move(des+name, os.path.join(output_directory,name))
        shutil.rmtree(des)
    except Exception as e:
        logging.info('directory move of new model failed!' +str(e))
def reset(output_path, image_dir, csv_input, tf_serving_model_path, **context):
    """
    the function resets the current folders and files
    :param output_path:
    :param image_dir:
    :param csv_input:
    :param tf_serving_model_path:
    :return:
    """
    try:
        rmfile(output_path + '/train.record')
        rmfile(output_path + '/eval.record')
        rmdir(os.path.join(output_path, 'push'))
        rmdir(os.path.join(output_path, 'model'))
        rmdir(os.path.join(output_path, 'training'))
    except Exception as e:
        logging.info('directory and file reset failed!' +str(e))
    return True
def shaffelfiles(path, summ):
    """
    this function randomly selects files and combines all of them into an List
    :param path: image path
    :param summ: count of the total images
    :return: list of random images selected from the path
    """
    file_list = []
    cnt = 0
    for x in range(0, summ):
        files = os.listdir(path)
        index = random.randrange(0, len(files))
        while not files[index].endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')) or cnt == 5:
            cnt += 1
            index = random.randrange(0, len(files))
        file_list.append(files[index])
        cnt = 0
    file_list_without_doub = list(dict.fromkeys(file_list)) # remove doublicates
    return file_list_without_doub # return the list without doublicates
def rmdir(dir):
    try:
        shutil.rmtree(dir)
        logging.info("remove dir: "+dir)
    except Exception as e:
        logging.info(e)
def rmfile(file):
    """
    removes a file
    :param file:
    :return: creation
    """
    if os.path.exists(file):
        os.remove(file)
        logging.info("remove file: "+file)
    else:
        logging.info("file does'n exist: " + file)
def mkdir(dir):
    """
    create a dir
    :param dir: where
    :return: the new path
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
        logging.info("create: "+dir)
    else:
        logging.info("dir exists already: "+ dir)
        logging.info("remove dir: "+ dir)
        shutil.rmtree(dir)
        logging.info("create dir: "+ dir)
        mkdir(dir)
def findlatestdir(directory):
    """
    find the latest directory inside of a directory
    :param directory: inside which folder
    :return: path
    """
    return max(glob.glob(os.path.join(directory, '*/')), key=os.path.getmtime)

"""
The following executions are for the airflow scheduler.
for testing the pipeline execute create_pipeline() for example like this:
cd workspace/pipeline/.../airflow/dags/
bash python3 \
from main import * \
create_pipeline()
"""

task_reset = PythonOperator(task_id='reset',provide_context=True,retries=1,python_callable=reset,op_kwargs={"output_path":output_path, "image_dir":image_dir, "csv_input":csv_input, "tf_serving_model_path":tf_serving_model_path},dag=dag)
task_data = PythonOperator(task_id='data',provide_context=True,retries=1,python_callable=data,op_kwargs={"output_path":output_path, "image_dir":image_dir, "csv_input":csv_input},dag=dag)
task_preprocessmodel = PythonOperator(task_id='preprocessmodel',provide_context=True,retries=1,python_callable=preprocessmodel,op_kwargs={"tf_serving_model_path":tf_serving_model_path, "output_path":output_path},dag=dag)
task_monitor = PythonOperator(task_id='monitor',provide_context=True,retries=1,python_callable=monitor,op_kwargs={"model_dir":model_dir},dag=dag)
task_train = PythonOperator(task_id='train',provide_context=True,retries=1,python_callable=train,op_kwargs={"pipeline_config_path":pipeline_config_path, "model_dir":model_dir, "num_train_steps":num_train_steps},dag=dag)
task_modelexporter = PythonOperator(task_id='modelexporter',provide_context=True,retries=1,python_callable=modelexporter,op_kwargs={"pipeline_config_path":pipeline_config_path, "model_dir":model_dir, "output_path":output_path},dag=dag)
task_modelmover = PythonOperator(task_id='modelmover',provide_context=True,retries=1,python_callable=modelmover,op_kwargs={"output_path":output_path},dag=dag)
task_trainmover = PythonOperator(task_id='trainmover',provide_context=True,retries=1,python_callable=trainmover,op_kwargs={"model_dir":model_dir, "output_path":output_path},dag=dag)
task_pusher = PythonOperator(task_id='pusher',provide_context=True,retries=1,python_callable=pusher,op_kwargs={"output_path":output_path, "tf_serving_model_path":tf_serving_model_path},dag=dag)
task_clean = PythonOperator(task_id='clean',provide_context=True,retries=1,python_callable=clean,op_kwargs={"image_dir":image_dir, "csv_input":csv_input},dag=dag)
task_reset = PythonOperator(task_id='reset',provide_context=True,retries=1,python_callable=reset,op_kwargs={"output_path":output_path, "image_dir":image_dir, "csv_input":csv_input, "tf_serving_model_path":tf_serving_model_path},dag=dag)

task_reset >> task_data >> task_preprocessmodel >> task_monitor >> task_train >> task_modelexporter >> task_modelmover >> task_trainmover >> task_pusher >> task_clean


