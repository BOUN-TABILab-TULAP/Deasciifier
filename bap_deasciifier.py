# -*- coding: utf-8 -*-


import pickle

char_to_ix = pickle.load(open("chardict_deasciifier.pickle", "rb"))
# print(char_to_ix)
tag_to_ix = pickle.load(open("tagdict_deasciifier.pickle", "rb"))
# print(tag_to_ix)

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.autograd as autograd
torch.manual_seed(1)

class LSTMTagger(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, vocab_size, tagset_size):
        super(LSTMTagger, self).__init__()
        self.hidden_dim = hidden_dim
        #self.batch_size = batch_size

        self.char_embeddings = nn.Embedding(vocab_size, embedding_dim)

        # The LSTM takes word embeddings as inputs, and outputs hidden states
        # with dimensionality hidden_dim.
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, bidirectional=True)  # <- change here

        # The linear layer that maps from hidden state space to tag space
        self.hidden2tag = nn.Linear(hidden_dim * 2, tagset_size)

    def forward(self, sentence):
        embeds = self.char_embeddings(sentence)
        lstm_out, _ = self.lstm(embeds.view(len(sentence), 1, -1))
        tag_space = self.hidden2tag(lstm_out.view(len(sentence), -1))
        tag_scores = F.log_softmax(tag_space, dim=1)
        return tag_scores

model = LSTMTagger(300, 256, len(char_to_ix), len(tag_to_ix))
loss_function = nn.NLLLoss()
optimizer = optim.SGD(model.parameters(), lr = 0.1)

model_save_name = '2103_deasciifier_emb300_hid256_epoch10.pt'

model.load_state_dict(torch.load(model_save_name))

def prepare_sequence(seq, to_ix):
  idxs = [to_ix[ch] for ch in seq]
  return torch.tensor(idxs, dtype = torch.long)

def _prob_to_tag(_tag_scores):
  sentence_tag_list = []
  prob_to_tag = []
  for ch in _tag_scores:
    chlist = list(ch)
      #print(chlist)
    maxi = max(chlist)
    ind = chlist.index(maxi)  
    prob_to_tag.append((list(tag_to_ix.keys())[ind]))
  return prob_to_tag

def deasciify(sentence):
  inputs = prepare_sequence(sentence, char_to_ix)
  _tag_scores = model(inputs)
  out = _prob_to_tag(_tag_scores)
  out = ''.join(out)
  return out

# deasciify("Yagmur yagarken camlari kapatin lutfen.")