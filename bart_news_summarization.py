# -*- coding: utf-8 -*-
"""BART-news_Summarization.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oqsU9hOFT9fx7UqkfAmwgxXs2Mv5tGCA
"""

!pip install transformers
!pip install sentencepiece
!pip install datasets
!pip install rouge-score

import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
import warnings
warnings.filterwarnings("ignore")
from tqdm import tqdm

import tensorflow as tf
from datasets import Dataset, DatasetDict
from transformers import BartTokenizer, TFBartForConditionalGeneration, TFAutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, create_optimizer
from rouge_score import rouge_scorer

#importing the data from google drive
from google.colab import drive
drive.mount('/content/drive')

training_path=os.path.join("/content/drive/MyDrive/Data/News/news_summarization_training.csv")
validation_path=os.path.join("/content/drive/MyDrive/Data/News/news_summarization_validation.csv")
train=pd.read_csv(training_path)
valid=pd.read_csv(validation_path)
train=Dataset.from_pandas(train)
valid=Dataset.from_pandas(valid)
dataset=DatasetDict()
dataset['training']=train.remove_columns(['Unnamed: 0'])
dataset['validation']=valid.remove_columns(['Unnamed: 0'])
dataset

checkpoint="facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(checkpoint)
model= TFAutoModelForSeq2SeqLM.from_pretrained(checkpoint)

max_input_length=512
max_target_length=80
def preprocess(example):
  input = tokenizer(example['text'],
                    max_length=max_input_length,
                    truncation=True,
                    )
  with tokenizer.as_target_tokenizer():
    labels = tokenizer(example['summary'],
                       max_length=max_target_length,
                       truncation=True)
  input['labels']=labels['input_ids']
  return input

tokenized_dataset = dataset.map(preprocess,batched=True)
tokenized_dataset

tokenized_dataset.remove_columns(['summary','text'])

datacollator=DataCollatorForSeq2Seq(tokenizer,model=model,return_tensors="tf")

tf_train_dataset = tokenized_dataset['training'].to_tf_dataset(
    columns=['input_ids', 'attention_mask', 'labels'],
    collate_fn=datacollator,
    shuffle=True,
    batch_size=1
)
tf_train_dataset

tf_valid_dataset = tokenized_dataset['validation'].to_tf_dataset(
    columns=['input_ids', 'attention_mask', 'labels'],
    collate_fn=datacollator,
    shuffle=False,
    batch_size=1)
tf_valid_dataset

epochs = 1
#No of training steps are len(dataset)/batch_size*no of epochs
num_train_steps = len(tf_train_dataset) * epochs

#creating a optimizer using transformers create optimizer
optimizer, schedule = create_optimizer(
    init_lr=4e-5,
    num_warmup_steps=0,
    num_train_steps=num_train_steps,
    weight_decay_rate=0.01,
)

model.compile(optimizer=optimizer) #for loss the model will use the models internal loss by default

# Training in mixed-precision float16 for faster training and efficient memory usage
tf.keras.mixed_precision.set_global_policy("mixed_float16")

history = model.fit(tf_train_dataset,validation_data=tf_valid_dataset,epochs=epochs)

#generating the summaries on the testing dataset
#testing only on the first 100 samples
reference=[]
model_generated=[]
for i,batch in enumerate(tqdm(tf_valid_dataset),start=1):
  if i>101:
    break
  labels=batch['labels'].numpy()
  labels=np.where(labels!=-100,labels,tokenizer.pad_token_id)
  labels=tokenizer.batch_decode(labels,skip_special_tokens=True)
  reference.extend(labels)
  pred=model.generate(**batch,min_length=55,max_length=100)
  pred_decoded = tokenizer.batch_decode(pred,skip_special_tokens=True)
  model_generated.extend(pred_decoded)

def calc_metrics(preds,actual):
  metrics=['rouge1','rouge2','rougeL']
  result={metrics[0]:[],metrics[1]:[],metrics[2]:[]}
  for metric in metrics:
    precision=[]
    recall=[]
    f1=[]
    scorer = rouge_scorer.RougeScorer([metric],use_stemmer=True)
    for x,y in zip(model_generated,reference):
      scores = scorer.score(x,y)
      precision.append(scores[metric][0])
      recall.append(scores[metric][1])
      f1.append(scores[metric][2])
    result[metric].append(np.mean(precision))
    result[metric].append(np.mean(recall))
    result[metric].append(np.mean(f1))
  return pd.DataFrame(result,index=['Precision','Recall','F1-Score'])

scores=calc_metrics(model_generated,reference)
scores

#creating a function to generate summary
def generate_summary(text,min_length=55,max_length=80):
  text = "summarize: "+text
  input = tokenizer(text,max_length=512,truncation=True,return_tensors="tf").input_ids
  op=model.generate(input,min_length=min_length,max_length=max_length)
  decoded_op = tokenizer.batch_decode(op,skip_special_tokens=True)
  return decoded_op

import nltk
from nltk import sent_tokenize
nltk.download('punkt')
testfile=os.path.join("/content/drive/MyDrive/Data/News/summary test.txt")
text = open(testfile,"r").read()
text=" ".join(sent_tokenize(text))
print(text)

predicted_summary = generate_summary(text,min_length=20,max_length=100)

predicted_summary

"""**Actual_summary:** "Meghalaya BJP Leader, Accused Of Running Brothel, Arrested In UP Bernard Marak had been on the run after six minors were rescued and 73 people arrested from his farmhouse 'Rimpu Bagan' during a raid on Saturday"

**Generated_summary:** 
"BJP's Meghalaya Vice-President Bernard Marak, accused of operating a brothel at his farmhouse, has been arrested in Hapur district of Uttar Pradesh. Police said Marak was asked to cooperate in the probe but is evading the investigators. The arrest came hours after the police put out a lookout notice for Marak. Marak had been on the run after six minors were rescued and 73 people were arrested from his"
"""