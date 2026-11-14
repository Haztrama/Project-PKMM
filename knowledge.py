"""knowledge.py - Basis pengetahuan: posisi pekerjaan, bank pertanyaan, dan kata kunci topik.
Isi kamus identik dengan app.py versi sebelumnya (tidak dipotong)."""

# --- DATA: POSISI PEKERJAAN & PERTANYAAN ---

# Pemetaan Posisi Pekerjaan ke ID Pertanyaan
JOB_ROLES = {
    "Machine Learning Engineer": [1, 2, 3, 4],
    "Data Scientist": [5, 6, 7, 8],
    "Computer Vision Engineer": [9, 10, 11, 12],
    "NLP Engineer": [13, 14, 15, 16],
    "AI Architect": [17, 18, 19, 20]
}

# Database Pertanyaan 
QUESTION_DB = {
    # ML Engineer
    1: "Describe a complex ML model you built and how you ensured its accuracy.",
    2: "Explain the concept of Overfitting and techniques to prevent it.",
    3: "How do you handle imbalanced datasets in a classification problem?",
    4: "Explain the difference between Batch, Stochastic, and Mini-batch Gradient Descent.",
    
    # Data Scientist
    5: "Walk us through your process of Data Cleaning and Preprocessing.",
    6: "Explain the difference between Supervised and Unsupervised Learning.",
    7: "How do you select the most important features for your model?",
    8: "Explain the concept of Bias-Variance Tradeoff.",
    
    # Computer Vision Engineer
    9: "Describe the architecture of a Convolutional Neural Network (CNN).",
    10: "How does Max Pooling work and why is it used?",
    11: "Explain the concept of Transfer Learning in Image Classification.",
    12: "How do you handle Object Detection tasks (e.g., YOLO, R-CNN)?",
    
    # NLP Engineer
    13: "Explain the mechanism of Tokenization and Word Embeddings.",
    14: "Describe the Transformer architecture and the Attention mechanism.",
    15: "How do you handle sequence data using RNNs or LSTMs?",
    16: "Explain the concept of Named Entity Recognition (NER).",
    
    # AI Architect
    17: "How do you design a scalable MLOps pipeline?",
    18: "What factors do you consider when choosing between Cloud vs Edge deployment?",
    19: "How do you ensure data privacy and security in AI systems?",
    20: "Describe a high-level architecture for a real-time recommendation system."
}

# --- DATABASE KATA KUNCI (DIPERLUAS & DIPERBANYAK) ---
# Semakin banyak kata kunci teknis yang disebut kandidat, semakin tinggi skornya.
TOPIC_KEYWORDS = {
    1: ["model", "accuracy", "tuning", "optimization", "hyperparameter", "loss", "metric", "validation", "auc", "roc", "precision", "recall", "deploy", "pipeline", "baseline", "evaluation", "confusion matrix", "cross-validation", "testing", "monitoring"],
    2: ["overfitting", "regularization", "dropout", "l1", "l2", "early", "stopping", "data", "augmentation", "complexity", "generalization", "noise", "pruning", "variance", "training data", "bias", "ensemble", "simplify", "penalty"],
    3: ["imbalanced", "smote", "resampling", "oversampling", "undersampling", "class", "weight", "f1", "precision", "minority", "majority", "stratified", "synthetic", "adayan", "cost-sensitive", "recall", "anomaly", "skewed", "distribution"],
    4: ["gradient", "descent", "batch", "stochastic", "update", "weight", "convergence", "learning", "rate", "optimizer", "momentum", "adam", "cost", "function", "epoch", "iteration", "minima", "backpropagation", "parameter"],
    
    5: ["clean", "missing", "value", "imputation", "outlier", "normalize", "standardize", "pandas", "null", "duplicate", "scaling", "encoding", "categorical", "transform", "preprocessing", "quality", "formatting", "binning", "wrangling", "etl"],
    6: ["supervised", "unsupervised", "label", "clustering", "classification", "regression", "k-means", "target", "prediction", "discovery", "dimension", "pca", "labeled", "unlabeled", "training", "association", "pattern", "input", "output"],
    7: ["feature", "selection", "importance", "pca", "correlation", "dimensional", "reduction", "recursive", "lasso", "ridge", "filter", "wrapper", "information", "gain", "mutual", "variance", "heatmap", "redundant", "engineering"],
    8: ["bias", "variance", "tradeoff", "underfitting", "overfitting", "error", "complexity", "model", "flexible", "irreducible", "total", "generalize", "training", "test", "balance", "sweet spot", "predictive", "performance"],
    
    9: ["cnn", "convolution", "layer", "filter", "kernel", "feature", "map", "relu", "activation", "stride", "padding", "flatten", "dense", "softmax", "visual", "image", "pixel", "architecture", "deep", "learning"],
    10: ["pooling", "max", "average", "dimension", "reduction", "spatial", "downsampling", "parameter", "invariance", "translation", "computation", "summary", "feature", "map", "size", "compress", "information", "receptive", "field"],
    11: ["transfer", "learning", "pretrained", "imagenet", "vgg", "resnet", "finetuning", "weights", "freeze", "domain", "adaptation", "source", "target", "efficientnet", "mobilenet", "feature", "extraction", "saving", "time"],
    12: ["object", "detection", "yolo", "rcnn", "bounding", "box", "anchor", "intersection", "iou", "confidence", "suppression", "region", "proposal", "grid", "localization", "classification", "fast-rcnn", "mask", "ssd"],
    
    13: ["token", "embedding", "vector", "word2vec", "glove", "representation", "vocabulary", "corpus", "semantic", "similarity", "cosine", "context", "n-gram", "stemming", "lemmatization", "split", "preprocessing", "dense", "dimension", "text"],
    14: ["transformer", "attention", "mechanism", "encoder", "decoder", "bert", "gpt", "self-attention", "multi-head", "positional", "encoding", "scale", "dot-product", "sequence", "parallel", "training", "context", "nlp", "model"],
    15: ["rnn", "lstm", "gru", "sequence", "temporal", "memory", "vanishing", "gradient", "gate", "forget", "dependency", "long-term", "short-term", "state", "recurrent", "network", "input", "output", "hidden"],
    16: ["ner", "entity", "recognition", "tagging", "extraction", "information", "text", "label", "person", "organization", "location", "chunking", "bio", "token", "sequence", "model", "spacy", "nltk", "crf"],
    
    17: ["mlops", "pipeline", "ci/cd", "deployment", "monitoring", "docker", "kubernetes", "model", "registry", "versioning", "drift", "serving", "api", "automated", "workflow", "production", "scale", "lifecycle", "infrastructure"],
    18: ["cloud", "edge", "latency", "bandwidth", "cost", "privacy", "device", "resource", "server", "connectivity", "real-time", "power", "consumption", "security", "iot", "processing", "centralized", "decentralized"],
    19: ["privacy", "security", "encryption", "gdpr", "compliance", "anonymization", "access", "control", "federated", "learning", "differential", "secure", "multiparty", "data", "protection", "leakage", "attack", "robustness"],
    20: ["recommendation", "system", "real-time", "collaborative", "filtering", "latency", "streaming", "kafka", "matrix", "factorization", "content-based", "hybrid", "user", "item", "ranking", "personalization", "cold-start", "feedback"]
}
