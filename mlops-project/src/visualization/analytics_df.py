#!/usr/bin/env python
# coding: utf-8

# # Sera venenoso
#
# El objetivo de este experimento es para saber si un hongo es venenoso
# o no, usando las habilidades de DS y ML

# ## Analitica de datos

# In[49]:


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, train_test_split

# In[50]:


FOLDER_PATH = "sera-venenoso/"

df_train = pd.read_csv(f"{FOLDER_PATH}train.csv")
df_test = pd.read_csv(f"{FOLDER_PATH}test.csv")
df_class_test = pd.read_csv(f"{FOLDER_PATH}sample_submission.csv")


# In[51]:


df_train.head()


# In[52]:


df_test.head()


# In[53]:


df_class_test.replace(
    {"Edibla": "Edible", "Poisonousa": "Poisonous"}, inplace=True
)
df_class_test.head()


# In[54]:


df_test = df_test.merge(df_class_test, on="id")
df_test.head()


# In[55]:


df = pd.concat([df_train, df_test]).sort_values("id")
df.head()
df[df.duplicated()]


# In[ ]:


# In[56]:


df.dtypes


# In[57]:


df.describe(include="all")


# In[58]:


df.corr()


# Revisando todos los datos al parecer se tienen puras variables
# categoricas se tendran que transformar

# In[59]:


# transformando el id a indice del dataframe
df.head()
df[df.duplicated()]


# In[60]:


dict_data_parse = {}

for column in df:
    if column == "id":
        continue

    parse = df[column].unique().tolist()

    # Este forma no me gusta, hay que revisar como mejorar
    mini_dict = {}
    rest = 0
    for k, v in enumerate(parse):
        if v == "None":
            rest += 1
            val = None
        else:
            k -= rest
            val = k

        mini_dict[v] = val

    dict_data_parse[column] = mini_dict


# In[61]:


for k, v in dict_data_parse.items():
    df[k].replace(v, inplace=True)

df[df.duplicated()]


# In[62]:


df[df.index.duplicated()]


# In[63]:


# profile = ProfileReport(df, title='sera venenoso')
# profile


# Eliminando variable con un solo valor y variables con missing values

# In[64]:


# Columna veil-type solo tiene un dato
print(df.shape)
df.drop(["veil-type", "id"], inplace=True, errors="ignore", axis=1)
df.dropna(axis=1, inplace=True)


# In[65]:


df.shape


# In[66]:


sns.set_theme(style="white")
corr = df.corr()

# Generate a mask for the upper triangle
mask = np.triu(np.ones_like(corr, dtype=bool))

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(16, 16))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(230, 20, as_cmap=True)

sns.heatmap(
    corr,
    mask=mask,
    cmap=cmap,
    vmax=0.3,
    center=0,
    square=True,
    linewidths=0.5,
    cbar_kws={"shrink": 0.5},
    annot=True,
)


# Tomando en cuanta los valores de correlacion que se tienen con class
# y usando tambien odor (siendo la relacion mas grande)
# usare el valor 0.3 en adelante para el modelo

# In[67]:


colums_corr = corr[(corr["class"] >= 0.30) & (corr["class"] < 1)][["class"]]
colums_corr = colums_corr.index.values.tolist()
df_worker = df[colums_corr + ["class"]]
X = df_worker[colums_corr]
Y = df_worker["class"]
df_worker.head()


# Despues del procesado de datos y borrado de otros se tienen datos que
# parecen duplicados, se borran

# In[68]:


df_worker.drop_duplicates(inplace=True)
df_worker.reset_index(inplace=True)
df_worker.drop("index", axis=1, inplace=True, errors="ignore")
df_worker.head()


# Partiendo los datos para entrenar y para probar

# In[70]:


X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)


# Creando los ML (instanciando las clases)

# In[71]:


lr = LogisticRegression()
multi_nb = GaussianNB()
knn = KNeighborsClassifier()
svc = SVC()
tree = DecisionTreeClassifier()


# ### Trabajando con la regresion logistica

# In[72]:


lr.fit(X_train, y_train)
y_pred = lr.predict(X_test)
result = lr.score(X_test, y_test)


# ### Validations

# In[73]:


"Accuracy: %.2f%%" % (result * 100.0)


# In[74]:


cm = confusion_matrix(y_test, y_pred)
cm


# In[75]:


print(classification_report(y_test, y_pred))


# In[76]:


scores = cross_val_score(lr, X_train, y_train, cv=10)
scores


# ### Trabajando con Naive Bayes

# In[77]:


multi_nb.fit(X_train, y_train)
y_pred = multi_nb.predict(X_test)
result = multi_nb.score(X_test, y_test)


# ### Validations

# In[78]:


"Accuracy: %.2f%%" % (result * 100.0)


# In[79]:


cm = confusion_matrix(y_test, y_pred)
cm


# In[80]:


print(classification_report(y_test, y_pred))


# In[81]:


scores = cross_val_score(multi_nb, X_train, y_train, cv=10)
scores


# ### Trabajando con KNN

# In[82]:


knn.fit(X_train, y_train)
y_pred = knn.predict(X_test)
result = knn.score(X_test, y_test)


# ### Validations

# In[83]:


"Accuracy: %.2f%%" % (result * 100.0)


# In[84]:


cm = confusion_matrix(y_test, y_pred)
cm


# In[85]:


print(classification_report(y_test, y_pred))


# In[86]:


scores = cross_val_score(knn, X_train, y_train, cv=10)
scores


# ### Trabajando con Support Vector Machine

# In[87]:


svc.fit(X_train, y_train)
y_pred = svc.predict(X_test)
result = svc.score(X_test, y_test)


# ### Validations

# In[88]:


"Accuracy: %.2f%%" % (result * 100.0)


# In[89]:


cm = confusion_matrix(y_test, y_pred)
cm


# In[90]:


print(classification_report(y_test, y_pred))


# In[91]:


scores = cross_val_score(svc, X_train, y_train, cv=10)
scores


# ### Trabajando con arbol de decision

# In[92]:


tree.fit(X_train, y_train)
y_pred = tree.predict(X_test)
result = tree.score(X_test, y_test)


# ### Validations

# In[93]:


"Accuracy: %.2f%%" % (result * 100.0)


# In[94]:


cm = confusion_matrix(y_test, y_pred)
cm


# In[95]:


print(classification_report(y_test, y_pred))


# In[96]:


scores = cross_val_score(tree, X_train, y_train, cv=10)
scores
