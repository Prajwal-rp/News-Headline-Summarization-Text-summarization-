# News-Headline-Summarization-Text-summarization

# Problem statement
Text summarization is all about converting a bunch of paragraphs into a few
sentences that explain the whole document’s gist. There are hundreds of
applications in every industry, given the amount of text data. Text data is increasing
exponentially. A lot of time is needed to analyze, understand, and summarize each
piece of it

### some of the applications of summarization are:
* Summarizing news articles to enrich the user experience
* Legal document summarization
* Summarizing clinical research documents
* Product review insight from multiple data sources
* Call center data summarization to understand the high-level cause
* Summarize the educational notes and book for quick revision
* Transcript summarization
* Social media analysis

# About the data
We are using a news data set to generate headlines. The data set consists of text and
headlines for more than 3000 records.


# Approach:
There are two main ways to summarize text in NLP: 
* extractive summarization
* abstractive summarization.
**Here we will be using abstractive summarization technique because this algorithm creates new sentences and phrases which cover most of
the context from the original text.**

# Model building
here we will be using pretrained model and finetuning the model on our data for summarization.
For this Finetuning we will be using Hugging face transformers
The pretrained models used are:
1) T5-(Text-TO-Text=Transfer-Transformer) -t5-base

T5 is an encoder-decoder model pre-trained on a multi-task mixture of unsupervised and supervised tasks and for which each task is converted into a text-to-text format.
we will be using the base version of T5(t5-base)

2) BART - facebook/bart-large-cnn

BART model pre-trained on English language, and fine-tuned on CNN Daily Mail.
BART is a transformer encoder-encoder (seq2seq) model with a bidirectional (BERT-like) encoder and an autoregressive (GPT-like) decoder. 
BART is pre-trained by corrupting text with an arbitrary noising function, and learning a model to reconstruct the original text.

# finetuning parameters:
## T5
* epochs=8
* Learning rate = 4e-5
* Btach_size = 8

## BART
* epochs=1
* Learning arte = 4e-5
* Batch_size = 1(Due to computational resource constraint)

# Results
![results](https://user-images.githubusercontent.com/93460334/183608401-b3d2485c-6e6e-44e8-84f1-00d68ca3fc57.jpg)


The loss and the Rouge scores for the BART model are better compared to the T5 model
