Provided proper attribution is provided, Google hereby grants permission to
reproduce the tables and figures in this paper solely for use in journalistic or
scholarly works.

## **Attention Is All You Need**



**Niki Parmar** _[∗]_
Google Research
```
nikip@google.com

```


**Ashish Vaswani** _[∗]_
Google Brain
```
avaswani@google.com

```

**Llion Jones** _[∗]_
Google Research
```
 llion@google.com

```


**Noam Shazeer** _[∗]_
Google Brain
```
noam@google.com

```


**Jakob Uszkoreit** _[∗]_
Google Research
```
usz@google.com

```


**Aidan N. Gomez** _[∗†]_
University of Toronto
```
aidan@cs.toronto.edu

```


**Łukasz Kaiser** _[∗]_
Google Brain
```
lukaszkaiser@google.com

```


**Illia Polosukhin** _[∗‡]_

```
             illia.polosukhin@gmail.com

```

**Abstract**


The dominant sequence transduction models are based on complex recurrent or
convolutional neural networks that include an encoder and a decoder. The best
performing models also connect the encoder and decoder through an attention
mechanism. We propose a new simple network architecture, the Transformer,
based solely on attention mechanisms, dispensing with recurrence and convolutions
entirely. Experiments on two machine translation tasks show these models to
be superior in quality while being more parallelizable and requiring significantly
less time to train. Our model achieves 28.4 BLEU on the WMT 2014 Englishto-German translation task, improving over the existing best results, including
ensembles, by over 2 BLEU. On the WMT 2014 English-to-French translation task,
our model establishes a new single-model state-of-the-art BLEU score of 41.8 after
training for 3.5 days on eight GPUs, a small fraction of the training costs of the
best models from the literature. We show that the Transformer generalizes well to
other tasks by applying it successfully to English constituency parsing both with
large and limited training data.


_∗_ Equal contribution. Listing order is random. Jakob proposed replacing RNNs with self-attention and started
the effort to evaluate this idea. Ashish, with Illia, designed and implemented the first Transformer models and
has been crucially involved in every aspect of this work. Noam proposed scaled dot-product attention, multi-head
attention and the parameter-free position representation and became the other person involved in nearly every
detail. Niki designed, implemented, tuned and evaluated countless model variants in our original codebase and
tensor2tensor. Llion also experimented with novel model variants, was responsible for our initial codebase, and
efficient inference and visualizations. Lukasz and Aidan spent countless long days designing various parts of and
implementing tensor2tensor, replacing our earlier codebase, greatly improving results and massively accelerating
our research.

_†_ Work performed while at Google Brain.

_‡_ Work performed while at Google Research.


31st Conference on Neural Information Processing Systems (NIPS 2017), Long Beach, CA, USA.


**1** **Introduction**


Recurrent neural networks, long short-term memory [ 13 ] and gated recurrent [ 7 ] neural networks
in particular, have been firmly established as state of the art approaches in sequence modeling and
transduction problems such as language modeling and machine translation [ 35, 2, 5 ]. Numerous
efforts have since continued to push the boundaries of recurrent language models and encoder-decoder
architectures [38, 24, 15].


Recurrent models typically factor computation along the symbol positions of the input and output
sequences. Aligning the positions to steps in computation time, they generate a sequence of hidden
states _h_ _t_, as a function of the previous hidden state _h_ _t−_ 1 and the input for position _t_ . This inherently
sequential nature precludes parallelization within training examples, which becomes critical at longer
sequence lengths, as memory constraints limit batching across examples. Recent work has achieved
significant improvements in computational efficiency through factorization tricks [ 21 ] and conditional
computation [ 32 ], while also improving model performance in case of the latter. The fundamental
constraint of sequential computation, however, remains.


Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their distance in
the input or output sequences [ 2, 19 ]. In all but a few cases [ 27 ], however, such attention mechanisms
are used in conjunction with a recurrent network.


In this work we propose the Transformer, a model architecture eschewing recurrence and instead
relying entirely on an attention mechanism to draw global dependencies between input and output.
The Transformer allows for significantly more parallelization and can reach a new state of the art in
translation quality after being trained for as little as twelve hours on eight P100 GPUs.


**2** **Background**


The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU

[ 16 ], ByteNet [ 18 ] and ConvS2S [ 9 ], all of which use convolutional neural networks as basic building
block, computing hidden representations in parallel for all input and output positions. In these models,
the number of operations required to relate signals from two arbitrary input or output positions grows
in the distance between positions, linearly for ConvS2S and logarithmically for ByteNet. This makes
it more difficult to learn dependencies between distant positions [ 12 ]. In the Transformer this is
reduced to a constant number of operations, albeit at the cost of reduced effective resolution due
to averaging attention-weighted positions, an effect we counteract with Multi-Head Attention as
described in section 3.2.


Self-attention, sometimes called intra-attention is an attention mechanism relating different positions
of a single sequence in order to compute a representation of the sequence. Self-attention has been
used successfully in a variety of tasks including reading comprehension, abstractive summarization,
textual entailment and learning task-independent sentence representations [4, 27, 28, 22].


End-to-end memory networks are based on a recurrent attention mechanism instead of sequencealigned recurrence and have been shown to perform well on simple-language question answering and
language modeling tasks [34].


To the best of our knowledge, however, the Transformer is the first transduction model relying
entirely on self-attention to compute representations of its input and output without using sequencealigned RNNs or convolution. In the following sections, we will describe the Transformer, motivate
self-attention and discuss its advantages over models such as [17, 18] and [9].


**3** **Model Architecture**


Most competitive neural sequence transduction models have an encoder-decoder structure [ 5, 2, 35 ].
Here, the encoder maps an input sequence of symbol representations ( _x_ 1 _, ..., x_ _n_ ) to a sequence
of continuous representations **z** = ( _z_ 1 _, ..., z_ _n_ ) . Given **z**, the decoder then generates an output
sequence ( _y_ 1 _, ..., y_ _m_ ) of symbols one element at a time. At each step the model is auto-regressive

[10], consuming the previously generated symbols as additional input when generating the next.


2


Figure 1: The Transformer - model architecture.


The Transformer follows this overall architecture using stacked self-attention and point-wise, fully
connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1,
respectively.


**3.1** **Encoder and Decoder Stacks**


**Encoder:** The encoder is composed of a stack of _N_ = 6 identical layers. Each layer has two
sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, positionwise fully connected feed-forward network. We employ a residual connection [ 11 ] around each of
the two sub-layers, followed by layer normalization [ 1 ]. That is, the output of each sub-layer is
LayerNorm( _x_ + Sublayer( _x_ )), where Sublayer( _x_ ) is the function implemented by the sub-layer
itself. To facilitate these residual connections, all sub-layers in the model, as well as the embedding
layers, produce outputs of dimension _d_ model = 512.


**Decoder:** The decoder is also composed of a stack of _N_ = 6 identical layers. In addition to the two
sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head
attention over the output of the encoder stack. Similar to the encoder, we employ residual connections
around each of the sub-layers, followed by layer normalization. We also modify the self-attention
sub-layer in the decoder stack to prevent positions from attending to subsequent positions. This
masking, combined with fact that the output embeddings are offset by one position, ensures that the
predictions for position _i_ can depend only on the known outputs at positions less than _i_ .


**3.2** **Attention**


An attention function can be described as mapping a query and a set of key-value pairs to an output,
where the query, keys, values, and output are all vectors. The output is computed as a weighted sum


3


Scaled Dot-Product Attention Multi-Head Attention


Figure 2: (left) Scaled Dot-Product Attention. (right) Multi-Head Attention consists of several
attention layers running in parallel.


of the values, where the weight assigned to each value is computed by a compatibility function of the
query with the corresponding key.


**3.2.1** **Scaled Dot-Product Attention**


We call our particular attention "Scaled Dot-Product Attention" (Figure 2). The input consists of
queries and keys of dimension _d_ _k_, and values of dimension _d_ _v_ . We compute the dot products of the
query with all keys, divide each by _[√]_ _d_ _k_, and apply a softmax function to obtain the weights on the
values.


In practice, we compute the attention function on a set of queries simultaneously, packed together
into a matrix _Q_ . The keys and values are also packed together into matrices _K_ and _V_ . We compute
the matrix of outputs as:


Attention( _Q, K, V_ ) = softmax( _[Q][K]_ _[T]_ ) _V_ (1)

~~_√_~~ _d_ _k_


The two most commonly used attention functions are additive attention [ 2 ], and dot-product (multiplicative) attention. Dot-product attention is identical to our algorithm, except for the scaling factor
of ~~_√_~~ 1 _d_ _k_ . Additive attention computes the compatibility function using a feed-forward network with
a single hidden layer. While the two are similar in theoretical complexity, dot-product attention is
much faster and more space-efficient in practice, since it can be implemented using highly optimized
matrix multiplication code.


While for small values of _d_ _k_ the two mechanisms perform similarly, additive attention outperforms
dot product attention without scaling for larger values of _d_ _k_ [ 3 ]. We suspect that for large values of
_d_ _k_, the dot products grow large in magnitude, pushing the softmax function into regions where it has
extremely small gradients [4] . To counteract this effect, we scale the dot products by ~~_√_~~ 1 _d_ _k_ .


**3.2.2** **Multi-Head Attention**


Instead of performing a single attention function with _d_ model -dimensional keys, values and queries,
we found it beneficial to linearly project the queries, keys and values _h_ times with different, learned
linear projections to _d_ _k_, _d_ _k_ and _d_ _v_ dimensions, respectively. On each of these projected versions of
queries, keys and values we then perform the attention function in parallel, yielding _d_ _v_ -dimensional


4 To illustrate why the dot products get large, assume that the components of _q_ and _k_ are independent random
variables with mean 0 and variance 1 . Then their dot product, _q · k_ = [�] _[d]_ _i_ =1 _[k]_ _[q]_ _[i]_ _[k]_ _[i]_ [, has mean] [ 0] [ and variance] _[ d]_ _[k]_ [.]


4


output values. These are concatenated and once again projected, resulting in the final values, as
depicted in Figure 2.


Multi-head attention allows the model to jointly attend to information from different representation
subspaces at different positions. With a single attention head, averaging inhibits this.


MultiHead( _Q, K, V_ ) = Concat(head 1 _, ...,_ head h ) _W_ _[O]_

where head i = Attention( _QW_ _i_ _[Q]_ _[, KW]_ _[ K]_ _i_ _[, V W]_ _[ V]_ _i_ [)]


Where the projections are parameter matrices _W_ _i_ _[Q]_ _∈_ R _[d]_ [model] _[×][d]_ _[k]_, _W_ _i_ _[K]_ _∈_ R _[d]_ [model] _[×][d]_ _[k]_, _W_ _i_ _[V]_ _∈_ R _[d]_ [model] _[×][d]_ _[v]_
and _W_ _[O]_ _∈_ R _[hd]_ _[v]_ _[×][d]_ [model] .


In this work we employ _h_ = 8 parallel attention layers, or heads. For each of these we use
_d_ _k_ = _d_ _v_ = _d_ model _/h_ = 64 . Due to the reduced dimension of each head, the total computational cost
is similar to that of single-head attention with full dimensionality.


**3.2.3** **Applications of Attention in our Model**


The Transformer uses multi-head attention in three different ways:


    - In "encoder-decoder attention" layers, the queries come from the previous decoder layer,
and the memory keys and values come from the output of the encoder. This allows every
position in the decoder to attend over all positions in the input sequence. This mimics the
typical encoder-decoder attention mechanisms in sequence-to-sequence models such as

[38, 2, 9].


    - The encoder contains self-attention layers. In a self-attention layer all of the keys, values
and queries come from the same place, in this case, the output of the previous layer in the
encoder. Each position in the encoder can attend to all positions in the previous layer of the
encoder.


    - Similarly, self-attention layers in the decoder allow each position in the decoder to attend to
all positions in the decoder up to and including that position. We need to prevent leftward
information flow in the decoder to preserve the auto-regressive property. We implement this
inside of scaled dot-product attention by masking out (setting to _−∞_ ) all values in the input
of the softmax which correspond to illegal connections. See Figure 2.


**3.3** **Position-wise Feed-Forward Networks**


In addition to attention sub-layers, each of the layers in our encoder and decoder contains a fully
connected feed-forward network, which is applied to each position separately and identically. This
consists of two linear transformations with a ReLU activation in between.


FFN( _x_ ) = max(0 _, xW_ 1 + _b_ 1 ) _W_ 2 + _b_ 2 (2)


While the linear transformations are the same across different positions, they use different parameters
from layer to layer. Another way of describing this is as two convolutions with kernel size 1.
The dimensionality of input and output is _d_ model = 512, and the inner-layer has dimensionality
_d_ _ff_ = 2048.


**3.4** **Embeddings and Softmax**


Similarly to other sequence transduction models, we use learned embeddings to convert the input
tokens and output tokens to vectors of dimension _d_ model . We also use the usual learned linear transformation and softmax function to convert the decoder output to predicted next-token probabilities. In
our model, we share the same weight matrix between the two embedding layers and the pre-softmax
linear transformation, similar to [ 30 ]. In the embedding layers, we multiply those weights by _[√]_ _d_ model .


5


Table 1: Maximum path lengths, per-layer complexity and minimum number of sequential operations
for different layer types. _n_ is the sequence length, _d_ is the representation dimension, _k_ is the kernel
size of convolutions and _r_ the size of the neighborhood in restricted self-attention.


Layer Type Complexity per Layer Sequential Maximum Path Length
Operations
Self-Attention _O_ ( _n_ [2] _· d_ ) _O_ (1) _O_ (1)
Recurrent _O_ ( _n · d_ [2] ) _O_ ( _n_ ) _O_ ( _n_ )
Convolutional _O_ ( _k · n · d_ [2] ) _O_ (1) _O_ ( _log_ _k_ ( _n_ ))
Self-Attention (restricted) _O_ ( _r · n · d_ ) _O_ (1) _O_ ( _n/r_ )


**3.5** **Positional Encoding**


Since our model contains no recurrence and no convolution, in order for the model to make use of the
order of the sequence, we must inject some information about the relative or absolute position of the
tokens in the sequence. To this end, we add "positional encodings" to the input embeddings at the
bottoms of the encoder and decoder stacks. The positional encodings have the same dimension _d_ model
as the embeddings, so that the two can be summed. There are many choices of positional encodings,
learned and fixed [9].


In this work, we use sine and cosine functions of different frequencies:


_PE_ ( _pos,_ 2 _i_ ) = _sin_ ( _pos/_ 10000 [2] _[i/d]_ [model] )

_PE_ ( _pos,_ 2 _i_ +1) = _cos_ ( _pos/_ 10000 [2] _[i/d]_ [model] )


where _pos_ is the position and _i_ is the dimension. That is, each dimension of the positional encoding
corresponds to a sinusoid. The wavelengths form a geometric progression from 2 _π_ to 10000 _·_ 2 _π_ . We
chose this function because we hypothesized it would allow the model to easily learn to attend by
relative positions, since for any fixed offset _k_, _PE_ _pos_ + _k_ can be represented as a linear function of
_PE_ _pos_ .


We also experimented with using learned positional embeddings [ 9 ] instead, and found that the two
versions produced nearly identical results (see Table 3 row (E)). We chose the sinusoidal version
because it may allow the model to extrapolate to sequence lengths longer than the ones encountered
during training.


**4** **Why Self-Attention**


In this section we compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations
( _x_ 1 _, ..., x_ _n_ ) to another sequence of equal length ( _z_ 1 _, ..., z_ _n_ ), with _x_ _i_ _, z_ _i_ _∈_ R _[d]_, such as a hidden
layer in a typical sequence transduction encoder or decoder. Motivating our use of self-attention we
consider three desiderata.


One is the total computational complexity per layer. Another is the amount of computation that can
be parallelized, as measured by the minimum number of sequential operations required.


The third is the path length between long-range dependencies in the network. Learning long-range
dependencies is a key challenge in many sequence transduction tasks. One key factor affecting the
ability to learn such dependencies is the length of the paths forward and backward signals have to
traverse in the network. The shorter these paths between any combination of positions in the input
and output sequences, the easier it is to learn long-range dependencies [ 12 ]. Hence we also compare
the maximum path length between any two input and output positions in networks composed of the
different layer types.


As noted in Table 1, a self-attention layer connects all positions with a constant number of sequentially
executed operations, whereas a recurrent layer requires _O_ ( _n_ ) sequential operations. In terms of
computational complexity, self-attention layers are faster than recurrent layers when the sequence


6


length _n_ is smaller than the representation dimensionality _d_, which is most often the case with
sentence representations used by state-of-the-art models in machine translations, such as word-piece

[ 38 ] and byte-pair [ 31 ] representations. To improve computational performance for tasks involving
very long sequences, self-attention could be restricted to considering only a neighborhood of size _r_ in
the input sequence centered around the respective output position. This would increase the maximum
path length to _O_ ( _n/r_ ). We plan to investigate this approach further in future work.


A single convolutional layer with kernel width _k < n_ does not connect all pairs of input and output
positions. Doing so requires a stack of _O_ ( _n/k_ ) convolutional layers in the case of contiguous kernels,
or _O_ ( _log_ _k_ ( _n_ )) in the case of dilated convolutions [ 18 ], increasing the length of the longest paths
between any two positions in the network. Convolutional layers are generally more expensive than
recurrent layers, by a factor of _k_ . Separable convolutions [ 6 ], however, decrease the complexity
considerably, to _O_ ( _k · n · d_ + _n · d_ [2] ) . Even with _k_ = _n_, however, the complexity of a separable
convolution is equal to the combination of a self-attention layer and a point-wise feed-forward layer,
the approach we take in our model.


As side benefit, self-attention could yield more interpretable models. We inspect attention distributions
from our models and present and discuss examples in the appendix. Not only do individual attention
heads clearly learn to perform different tasks, many appear to exhibit behavior related to the syntactic
and semantic structure of the sentences.


**5** **Training**


This section describes the training regime for our models.


**5.1** **Training Data and Batching**


We trained on the standard WMT 2014 English-German dataset consisting of about 4.5 million
sentence pairs. Sentences were encoded using byte-pair encoding [ 3 ], which has a shared sourcetarget vocabulary of about 37000 tokens. For English-French, we used the significantly larger WMT
2014 English-French dataset consisting of 36M sentences and split tokens into a 32000 word-piece
vocabulary [ 38 ]. Sentence pairs were batched together by approximate sequence length. Each training
batch contained a set of sentence pairs containing approximately 25000 source tokens and 25000
target tokens.


**5.2** **Hardware and Schedule**


We trained our models on one machine with 8 NVIDIA P100 GPUs. For our base models using
the hyperparameters described throughout the paper, each training step took about 0.4 seconds. We
trained the base models for a total of 100,000 steps or 12 hours. For our big models,(described on the
bottom line of table 3), step time was 1.0 seconds. The big models were trained for 300,000 steps
(3.5 days).


**5.3** **Optimizer**


We used the Adam optimizer [ 20 ] with _β_ 1 = 0 _._ 9, _β_ 2 = 0 _._ 98 and _ϵ_ = 10 _[−]_ [9] . We varied the learning
rate over the course of training, according to the formula:


_lrate_ = _d_ _[−]_ model [0] _[.]_ [5] _[·]_ [ min(] _[step]_ [_] _[num]_ _[−]_ [0] _[.]_ [5] _[, step]_ [_] _[num][ ·][ warmup]_ [_] _[steps]_ _[−]_ [1] _[.]_ [5] [)] (3)


This corresponds to increasing the learning rate linearly for the first _warmup_ _ _steps_ training steps,
and decreasing it thereafter proportionally to the inverse square root of the step number. We used
_warmup_ _ _steps_ = 4000.


**5.4** **Regularization**


We employ three types of regularization during training:


7


Table 2: The Transformer achieves better BLEU scores than previous state-of-the-art models on the
English-to-German and English-to-French newstest2014 tests at a fraction of the training cost.


BLEU Training Cost (FLOPs)
Model

EN-DE EN-FR EN-DE EN-FR
ByteNet [18] 23.75
Deep-Att + PosUnk [39] 39.2 1 _._ 0 _·_ 10 [20]

GNMT + RL [38] 24.6 39.92 2 _._ 3 _·_ 10 [19] 1 _._ 4 _·_ 10 [20]

ConvS2S [9] 25.16 40.46 9 _._ 6 _·_ 10 [18] 1 _._ 5 _·_ 10 [20]

MoE [32] 26.03 40.56 2 _._ 0 _·_ 10 [19] 1 _._ 2 _·_ 10 [20]

Deep-Att + PosUnk Ensemble [39] 40.4 8 _._ 0 _·_ 10 [20]

GNMT + RL Ensemble [38] 26.30 41.16 1 _._ 8 _·_ 10 [20] 1 _._ 1 _·_ 10 [21]

ConvS2S Ensemble [9] 26.36 **41.29** 7 _._ 7 _·_ 10 [19] 1 _._ 2 _·_ 10 [21]

Transformer (base model) 27.3 38.1 **3** _**.**_ **3** _**·**_ **10** **[18]**

Transformer (big) **28.4** **41.8** 2 _._ 3 _·_ 10 [19]


**Residual Dropout** We apply dropout [ 33 ] to the output of each sub-layer, before it is added to the
sub-layer input and normalized. In addition, we apply dropout to the sums of the embeddings and the
positional encodings in both the encoder and decoder stacks. For the base model, we use a rate of
_P_ _drop_ = 0 _._ 1.


**Label Smoothing** During training, we employed label smoothing of value _ϵ_ _ls_ = 0 _._ 1 [ 36 ]. This
hurts perplexity, as the model learns to be more unsure, but improves accuracy and BLEU score.


**6** **Results**


**6.1** **Machine Translation**


On the WMT 2014 English-to-German translation task, the big transformer model (Transformer (big)
in Table 2) outperforms the best previously reported models (including ensembles) by more than 2 _._ 0
BLEU, establishing a new state-of-the-art BLEU score of 28 _._ 4 . The configuration of this model is
listed in the bottom line of Table 3. Training took 3 _._ 5 days on 8 P100 GPUs. Even our base model
surpasses all previously published models and ensembles, at a fraction of the training cost of any of
the competitive models.


On the WMT 2014 English-to-French translation task, our big model achieves a BLEU score of 41 _._ 0,
outperforming all of the previously published single models, at less than 1 _/_ 4 the training cost of the
previous state-of-the-art model. The Transformer (big) model trained for English-to-French used
dropout rate _P_ _drop_ = 0 _._ 1, instead of 0 _._ 3.


For the base models, we used a single model obtained by averaging the last 5 checkpoints, which
were written at 10-minute intervals. For the big models, we averaged the last 20 checkpoints. We
used beam search with a beam size of 4 and length penalty _α_ = 0 _._ 6 [ 38 ]. These hyperparameters
were chosen after experimentation on the development set. We set the maximum output length during
inference to input length + 50, but terminate early when possible [38].


Table 2 summarizes our results and compares our translation quality and training costs to other model
architectures from the literature. We estimate the number of floating point operations used to train a
model by multiplying the training time, the number of GPUs used, and an estimate of the sustained
single-precision floating-point capacity of each GPU [5] .


**6.2** **Model Variations**


To evaluate the importance of different components of the Transformer, we varied our base model
in different ways, measuring the change in performance on English-to-German translation on the


5 We used values of 2.8, 3.7, 6.0 and 9.5 TFLOPS for K80, K40, M40 and P100, respectively.


8


Table 3: Variations on the Transformer architecture. Unlisted values are identical to those of the base
model. All metrics are on the English-to-German translation development set, newstest2013. Listed
perplexities are per-wordpiece, according to our byte-pair encoding, and should not be compared to
per-word perplexities.













|Col1|train<br>N d d h d d P ϵ<br>model ff k v drop ls steps|PPL BLEU params<br>(dev) (dev) ×106|
|---|---|---|
|base|6<br>512<br>2048<br>8<br>64<br>64<br>0.1<br>0.1<br>100K|4.92<br>25.8<br>65|
|(A)|1<br>512<br>512<br>4<br>128<br>128<br>16<br>32<br>32<br>32<br>16<br>16|5.29<br>24.9<br>5.00<br>25.5<br>4.91<br>25.8<br>5.01<br>25.4|
|(B)|16<br>32|5.16<br>25.1<br>58<br>5.01<br>25.4<br>60|
|(C)|2<br>4<br>8<br>256<br>32<br>32<br>1024<br>128<br>128<br>1024<br>4096|6.11<br>23.7<br>36<br>5.19<br>25.3<br>50<br>4.88<br>25.5<br>80<br>5.75<br>24.5<br>28<br>4.66<br>26.0<br>168<br>5.12<br>25.4<br>53<br>4.75<br>26.2<br>90|
|(D)|0.0<br>0.2<br>0.0<br>0.2|5.77<br>24.6<br>4.95<br>25.5<br>4.67<br>25.3<br>5.47<br>25.7|
|(E)|positional embedding instead of sinusoids|4.92<br>25.7|
|big|6<br>1024<br>4096<br>16<br>0.3<br>300K|**4.33**<br>**26.4**<br>213|


development set, newstest2013. We used beam search as described in the previous section, but no
checkpoint averaging. We present these results in Table 3.


In Table 3 rows (A), we vary the number of attention heads and the attention key and value dimensions,
keeping the amount of computation constant, as described in Section 3.2.2. While single-head
attention is 0.9 BLEU worse than the best setting, quality also drops off with too many heads.


In Table 3 rows (B), we observe that reducing the attention key size _d_ _k_ hurts model quality. This
suggests that determining compatibility is not easy and that a more sophisticated compatibility
function than dot product may be beneficial. We further observe in rows (C) and (D) that, as expected,
bigger models are better, and dropout is very helpful in avoiding over-fitting. In row (E) we replace our
sinusoidal positional encoding with learned positional embeddings [ 9 ], and observe nearly identical
results to the base model.


**6.3** **English Constituency Parsing**


To evaluate if the Transformer can generalize to other tasks we performed experiments on English
constituency parsing. This task presents specific challenges: the output is subject to strong structural
constraints and is significantly longer than the input. Furthermore, RNN sequence-to-sequence
models have not been able to attain state-of-the-art results in small-data regimes [37].


We trained a 4-layer transformer with _d_ _model_ = 1024 on the Wall Street Journal (WSJ) portion of the
Penn Treebank [ 25 ], about 40K training sentences. We also trained it in a semi-supervised setting,
using the larger high-confidence and BerkleyParser corpora from with approximately 17M sentences

[ 37 ]. We used a vocabulary of 16K tokens for the WSJ only setting and a vocabulary of 32K tokens
for the semi-supervised setting.


We performed only a small number of experiments to select the dropout, both attention and residual
(section 5.4), learning rates and beam size on the Section 22 development set, all other parameters
remained unchanged from the English-to-German base translation model. During inference, we


9


Table 4: The Transformer generalizes well to English constituency parsing (Results are on Section 23
of WSJ)

|Parser|Training|WSJ 23 F1|
|---|---|---|
|Vinyals & Kaiser el al. (2014) [37]<br>Petrov et al. (2006) [29]<br>Zhu et al. (2013) [40]<br>Dyer et al. (2016) [8]|WSJ only, discriminative<br>WSJ only, discriminative<br>WSJ only, discriminative<br>WSJ only, discriminative|88.3<br>90.4<br>90.4<br>91.7|
|Transformer (4 layers)|WSJ only, discriminative|91.3|
|Zhu et al. (2013) [40]<br>Huang & Harper (2009) [14]<br>McClosky et al. (2006) [26]<br>Vinyals & Kaiser el al. (2014) [37]|semi-supervised<br>semi-supervised<br>semi-supervised<br>semi-supervised|91.3<br>91.3<br>92.1<br>92.1|
|Transformer (4 layers)|semi-supervised|92.7|
|Luong et al. (2015) [23]<br>Dyer et al. (2016) [8]|multi-task<br>generative|93.0<br>93.3|



increased the maximum output length to input length + 300 . We used a beam size of 21 and _α_ = 0 _._ 3
for both WSJ only and the semi-supervised setting.


Our results in Table 4 show that despite the lack of task-specific tuning our model performs surprisingly well, yielding better results than all previously reported models with the exception of the
Recurrent Neural Network Grammar [8].


In contrast to RNN sequence-to-sequence models [ 37 ], the Transformer outperforms the BerkeleyParser [29] even when training only on the WSJ training set of 40K sentences.


**7** **Conclusion**


In this work, we presented the Transformer, the first sequence transduction model based entirely on
attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with
multi-headed self-attention.


For translation tasks, the Transformer can be trained significantly faster than architectures based
on recurrent or convolutional layers. On both WMT 2014 English-to-German and WMT 2014
English-to-French translation tasks, we achieve a new state of the art. In the former task our best
model outperforms even all previously reported ensembles.


We are excited about the future of attention-based models and plan to apply them to other tasks. We
plan to extend the Transformer to problems involving input and output modalities other than text and
to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs
such as images, audio and video. Making generation less sequential is another research goals of ours.


The code we used to train and evaluate our models is available at `[https://github.com/](https://github.com/tensorflow/tensor2tensor)`
`[tensorflow/tensor2tensor](https://github.com/tensorflow/tensor2tensor)` .


**Acknowledgements** We are grateful to Nal Kalchbrenner and Stephan Gouws for their fruitful
comments, corrections and inspiration.


**References**


[1] Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E Hinton. Layer normalization. _arXiv preprint_
_[arXiv:1607.06450](http://arxiv.org/abs/1607.06450)_, 2016.


[2] Dzmitry Bahdanau, Kyunghyun Cho, and Yoshua Bengio. Neural machine translation by jointly
learning to align and translate. _CoRR_, abs/1409.0473, 2014.


[3] Denny Britz, Anna Goldie, Minh-Thang Luong, and Quoc V. Le. Massive exploration of neural
machine translation architectures. _CoRR_, abs/1703.03906, 2017.


[4] Jianpeng Cheng, Li Dong, and Mirella Lapata. Long short-term memory-networks for machine
reading. _[arXiv preprint arXiv:1601.06733](http://arxiv.org/abs/1601.06733)_, 2016.


10


[5] Kyunghyun Cho, Bart van Merrienboer, Caglar Gulcehre, Fethi Bougares, Holger Schwenk,
and Yoshua Bengio. Learning phrase representations using rnn encoder-decoder for statistical
machine translation. _CoRR_, abs/1406.1078, 2014.


[6] Francois Chollet. Xception: Deep learning with depthwise separable convolutions. _arXiv_
_[preprint arXiv:1610.02357](http://arxiv.org/abs/1610.02357)_, 2016.


[7] Junyoung Chung, Çaglar Gülçehre, Kyunghyun Cho, and Yoshua Bengio. Empirical evaluation
of gated recurrent neural networks on sequence modeling. _CoRR_, abs/1412.3555, 2014.


[8] Chris Dyer, Adhiguna Kuncoro, Miguel Ballesteros, and Noah A. Smith. Recurrent neural
network grammars. In _Proc. of NAACL_, 2016.


[9] Jonas Gehring, Michael Auli, David Grangier, Denis Yarats, and Yann N. Dauphin. Convolutional sequence to sequence learning. _[arXiv preprint arXiv:1705.03122v2](http://arxiv.org/abs/1705.03122)_, 2017.


[10] Alex Graves. Generating sequences with recurrent neural networks. _arXiv preprint_
_[arXiv:1308.0850](http://arxiv.org/abs/1308.0850)_, 2013.


[11] Kaiming He, Xiangyu Zhang, Shaoqing Ren, and Jian Sun. Deep residual learning for image recognition. In _Proceedings of the IEEE Conference on Computer Vision and Pattern_
_Recognition_, pages 770–778, 2016.


[12] Sepp Hochreiter, Yoshua Bengio, Paolo Frasconi, and Jürgen Schmidhuber. Gradient flow in
recurrent nets: the difficulty of learning long-term dependencies, 2001.


[13] Sepp Hochreiter and Jürgen Schmidhuber. Long short-term memory. _Neural computation_,
9(8):1735–1780, 1997.


[14] Zhongqiang Huang and Mary Harper. Self-training PCFG grammars with latent annotations
across languages. In _Proceedings of the 2009 Conference on Empirical Methods in Natural_
_Language Processing_, pages 832–841. ACL, August 2009.


[15] Rafal Jozefowicz, Oriol Vinyals, Mike Schuster, Noam Shazeer, and Yonghui Wu. Exploring
the limits of language modeling. _[arXiv preprint arXiv:1602.02410](http://arxiv.org/abs/1602.02410)_, 2016.


[16] Łukasz Kaiser and Samy Bengio. Can active memory replace attention? In _Advances in Neural_
_Information Processing Systems, (NIPS)_, 2016.


[17] Łukasz Kaiser and Ilya Sutskever. Neural GPUs learn algorithms. In _International Conference_
_on Learning Representations (ICLR)_, 2016.


[18] Nal Kalchbrenner, Lasse Espeholt, Karen Simonyan, Aaron van den Oord, Alex Graves, and Koray Kavukcuoglu. Neural machine translation in linear time. _[arXiv preprint arXiv:1610.10099v2](http://arxiv.org/abs/1610.10099)_,
2017.


[19] Yoon Kim, Carl Denton, Luong Hoang, and Alexander M. Rush. Structured attention networks.
In _International Conference on Learning Representations_, 2017.


[20] Diederik Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In _ICLR_, 2015.


[21] Oleksii Kuchaiev and Boris Ginsburg. Factorization tricks for LSTM networks. _arXiv preprint_
_[arXiv:1703.10722](http://arxiv.org/abs/1703.10722)_, 2017.


[22] Zhouhan Lin, Minwei Feng, Cicero Nogueira dos Santos, Mo Yu, Bing Xiang, Bowen
Zhou, and Yoshua Bengio. A structured self-attentive sentence embedding. _arXiv preprint_
_[arXiv:1703.03130](http://arxiv.org/abs/1703.03130)_, 2017.


[23] Minh-Thang Luong, Quoc V. Le, Ilya Sutskever, Oriol Vinyals, and Lukasz Kaiser. Multi-task
sequence to sequence learning. _[arXiv preprint arXiv:1511.06114](http://arxiv.org/abs/1511.06114)_, 2015.


[24] Minh-Thang Luong, Hieu Pham, and Christopher D Manning. Effective approaches to attentionbased neural machine translation. _[arXiv preprint arXiv:1508.04025](http://arxiv.org/abs/1508.04025)_, 2015.


11


[25] Mitchell P Marcus, Mary Ann Marcinkiewicz, and Beatrice Santorini. Building a large annotated
corpus of english: The penn treebank. _Computational linguistics_, 19(2):313–330, 1993.


[26] David McClosky, Eugene Charniak, and Mark Johnson. Effective self-training for parsing. In
_Proceedings of the Human Language Technology Conference of the NAACL, Main Conference_,
pages 152–159. ACL, June 2006.


[27] Ankur Parikh, Oscar Täckström, Dipanjan Das, and Jakob Uszkoreit. A decomposable attention
model. In _Empirical Methods in Natural Language Processing_, 2016.


[28] Romain Paulus, Caiming Xiong, and Richard Socher. A deep reinforced model for abstractive
summarization. _[arXiv preprint arXiv:1705.04304](http://arxiv.org/abs/1705.04304)_, 2017.


[29] Slav Petrov, Leon Barrett, Romain Thibaux, and Dan Klein. Learning accurate, compact,
and interpretable tree annotation. In _Proceedings of the 21st International Conference on_
_Computational Linguistics and 44th Annual Meeting of the ACL_, pages 433–440. ACL, July
2006.


[30] Ofir Press and Lior Wolf. Using the output embedding to improve language models. _arXiv_
_[preprint arXiv:1608.05859](http://arxiv.org/abs/1608.05859)_, 2016.


[31] Rico Sennrich, Barry Haddow, and Alexandra Birch. Neural machine translation of rare words
with subword units. _[arXiv preprint arXiv:1508.07909](http://arxiv.org/abs/1508.07909)_, 2015.


[32] Noam Shazeer, Azalia Mirhoseini, Krzysztof Maziarz, Andy Davis, Quoc Le, Geoffrey Hinton,
and Jeff Dean. Outrageously large neural networks: The sparsely-gated mixture-of-experts
layer. _[arXiv preprint arXiv:1701.06538](http://arxiv.org/abs/1701.06538)_, 2017.


[33] Nitish Srivastava, Geoffrey E Hinton, Alex Krizhevsky, Ilya Sutskever, and Ruslan Salakhutdinov. Dropout: a simple way to prevent neural networks from overfitting. _Journal of Machine_
_Learning Research_, 15(1):1929–1958, 2014.


[34] Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston, and Rob Fergus. End-to-end memory
networks. In C. Cortes, N. D. Lawrence, D. D. Lee, M. Sugiyama, and R. Garnett, editors,
_Advances in Neural Information Processing Systems 28_, pages 2440–2448. Curran Associates,
Inc., 2015.


[35] Ilya Sutskever, Oriol Vinyals, and Quoc VV Le. Sequence to sequence learning with neural
networks. In _Advances in Neural Information Processing Systems_, pages 3104–3112, 2014.


[36] Christian Szegedy, Vincent Vanhoucke, Sergey Ioffe, Jonathon Shlens, and Zbigniew Wojna.
Rethinking the inception architecture for computer vision. _CoRR_, abs/1512.00567, 2015.


[37] Vinyals & Kaiser, Koo, Petrov, Sutskever, and Hinton. Grammar as a foreign language. In
_Advances in Neural Information Processing Systems_, 2015.


[38] Yonghui Wu, Mike Schuster, Zhifeng Chen, Quoc V Le, Mohammad Norouzi, Wolfgang
Macherey, Maxim Krikun, Yuan Cao, Qin Gao, Klaus Macherey, et al. Google’s neural machine
translation system: Bridging the gap between human and machine translation. _arXiv preprint_
_[arXiv:1609.08144](http://arxiv.org/abs/1609.08144)_, 2016.


[39] Jie Zhou, Ying Cao, Xuguang Wang, Peng Li, and Wei Xu. Deep recurrent models with
fast-forward connections for neural machine translation. _CoRR_, abs/1606.04199, 2016.


[40] Muhua Zhu, Yue Zhang, Wenliang Chen, Min Zhang, and Jingbo Zhu. Fast and accurate
shift-reduce constituent parsing. In _Proceedings of the 51st Annual Meeting of the ACL (Volume_
_1: Long Papers)_, pages 434–443. ACL, August 2013.


12


**Attention Visualizations**


Figure 3: An example of the attention mechanism following long-distance dependencies in the
encoder self-attention in layer 5 of 6. Many of the attention heads attend to a distant dependency of
the verb ‘making’, completing the phrase ‘making...more difficult’. Attentions here shown only for
the word ‘making’. Different colors represent different heads. Best viewed in color.


13


and 6. Note that the attentions are very sharp for this word.


14


sentence. We give two such examples above, from two different heads from the encoder self-attention
at layer 5 of 6. The heads clearly learned to perform different tasks.


15


